from app import db
import random

# ============================================
# CONSTANTS
# ============================================

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

TIME_SLOTS = [
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00",   # last slot before lunch (NO 2-hour block can start here)
    "14:00-15:00",
    "15:00-16:00",
    "16:00-17:00"
]

# ============================================
# GROUP SPLIT → A → A1, A2
# ============================================
def generate_groups(section):
    return [f"{section}1", f"{section}2"]

# ============================================
# Utility: Get faculty for specific subject
# ============================================
def get_faculty_for_subject(sem, sec, subject):
    rec = db["teaching_load"].find_one(
        {"Semester": sem, "Section": sec, "Subject_Name": subject},
        {"Faculty_Name": 1, "_id": 0}
    )
    return rec["Faculty_Name"] if rec else ""

# ============================================
# MAIN GENERATOR
# ============================================
def generate_timetable():

    teaching_load = list(db["teaching_load"].find({}, {"_id": 0}))
    room_list = list(db["room_list"].find({}, {"_id": 0}))

    if not teaching_load:
        return {"success": False, "message": "Teaching load empty"}

    if not room_list:
        return {"success": False, "message": "Room list empty"}

    db["timetable"].delete_many({})

    timetable = []
    faculty_busy = {}
    section_busy = {}
    subject_used_daily = {}

    # ============================================
    # ROOMS
    # ============================================
    fixed_rooms = {}
    labs = []

    for r in room_list:
        if r["Room_Type"] == "Room" and r["Assigned_Semester"]:
            fixed_rooms[(r["Assigned_Semester"], r["Assigned_Section"])] = r["Room_No"]

        if r["Room_Type"] == "Lab":
            labs.append(r["Room_No"])

    # ============================================
    # SUBJECT SPLIT (Exclude PDP & COE)
    # ============================================
    group_subject_map = {}
    unique_sections = set((t["Semester"], t["Section"]) for t in teaching_load)

    for (sem, sec) in unique_sections:

        all_subjects = [
            t["Subject_Name"]
            for t in teaching_load
            if t["Semester"] == sem and t["Section"] == sec
        ]

        subjects = [
            s for s in all_subjects
            if "personality" not in s.lower()
            and "centre" not in s.lower()
            and "center" not in s.lower()
        ]

        random.shuffle(subjects)
        mid = len(subjects) // 2 or 1

        group_subject_map[(sem, sec)] = {
            "G1": subjects[:mid],
            "G2": subjects[mid:]
        }

    # ============================================
    # HELPERS
    # ============================================
    def mark_busy(sem, sec, subgroups, faculty, day, slots):
        for slot in slots:
            faculty_busy[(faculty, day, slot)] = True
            section_busy[(sem, sec, day, slot)] = True
            for sg in subgroups:
                section_busy[(sem, sg, day, slot)] = True

    def is_free(sem, sec, subgroups, faculty, day, slots):
        for slot in slots:
            if faculty_busy.get((faculty, day, slot)):
                return False
            if section_busy.get((sem, sec, day, slot)):
                return False
            for sg in subgroups:
                if section_busy.get((sem, sg, day, slot)):
                    return False
        return True

    # ============================================
    # SINGLE SLOT (L, PDP)
    # ============================================
    def place_single(sem, sec, faculty, subject, type_name, room):

        daily = subject_used_daily.setdefault((sem, sec), {})

        for day in DAYS:

            # PDP & COE cannot be on same day
            if type_name == "PDP" and "COE" in daily.get(day, set()):
                continue
            if type_name == "COE" and "PDP" in daily.get(day, set()):
                continue

            used_today = daily.setdefault(day, set())
            if subject in used_today:
                continue

            for slot in TIME_SLOTS:

                if not is_free(sem, sec, [], faculty, day, [slot]):
                    continue

                timetable.append({
                    "Semester": sem,
                    "Section": sec,
                    "Subject": subject,
                    "Faculty": faculty,
                    "Type": type_name,
                    "Day": day,
                    "Slot": slot,
                    "Room": room
                })

                mark_busy(sem, sec, [], faculty, day, [slot])
                used_today.add(subject)
                return True

        return False

    # ============================================
    # TWO HOUR BLOCK (T / P)
    # ============================================
    def place_two_hour(sem, sec, type_name,
                       subject1, subject2, faculty1, faculty2,
                       g1, g2, room1, room2):

        daily = subject_used_daily.setdefault((sem, sec), {})

        for day in DAYS:

            if type_name == "PDP" and "COE" in daily.get(day, set()):
                continue
            if type_name == "COE" and "PDP" in daily.get(day, set()):
                continue

            used_today = daily.setdefault(day, set())
            if subject1 in used_today or subject2 in used_today:
                continue

            for i in range(len(TIME_SLOTS) - 1):

                s1 = TIME_SLOTS[i]
                s2 = TIME_SLOTS[i + 1]

                # ❗ PREVENT 2-hour block starting at 12:00–13:00
                if s1 == "12:00-13:00":
                    continue

                # ensure free
                if not is_free(sem, sec, [g1, g2], faculty1, day, [s1, s2]):
                    continue
                if not is_free(sem, sec, [g1, g2], faculty2, day, [s1, s2]):
                    continue

                # Save
                timetable.append({
                    "Semester": sem,
                    "Section": sec,
                    "Type": type_name,
                    "Day": day,
                    "Slot": s1,
                    "Slot2": s2,
                    "Groups": [
                        {
                            "group": g1,
                            "subject": subject1,
                            "faculty": faculty1,
                            "room": room1,
                            "type": type_name
                        },
                        {
                            "group": g2,
                            "subject": subject2,
                            "faculty": faculty2,
                            "room": room2,
                            "type": type_name
                        }
                    ]
                })

                mark_busy(sem, sec, [g1, g2], faculty1, day, [s1, s2])
                mark_busy(sem, sec, [g1, g2], faculty2, day, [s1, s2])

                used_today.add(subject1)
                used_today.add(subject2)
                daily[day].add(type_name)
                return True

        return False

    # ============================================
    # COE (NO GROUP SPLIT – 2 HOUR BLOCK)
    # ============================================
    def place_coe(sem, sec, subject, faculty, class_room):

        daily = subject_used_daily.setdefault((sem, sec), {})

        for day in DAYS:

            if "PDP" in daily.get(day, set()):
                continue

            used_today = daily.setdefault(day, set())
            if subject in used_today:
                continue

            for i in range(len(TIME_SLOTS) - 1):

                s1 = TIME_SLOTS[i]
                s2 = TIME_SLOTS[i + 1]

                # ❗ COE also cannot overlap lunch
                if s1 == "12:00-13:00":
                    continue

                if faculty_busy.get((faculty, day, s1)): continue
                if faculty_busy.get((faculty, day, s2)): continue
                if section_busy.get((sem, sec, day, s1)): continue
                if section_busy.get((sem, sec, day, s2)): continue

                timetable.append({
                    "Semester": sem,
                    "Section": sec,
                    "Type": "COE",
                    "Subject": subject,
                    "Faculty": faculty,
                    "Day": day,
                    "Slot": s1,
                    "Slot2": s2,
                    "Room": class_room
                })

                faculty_busy[(faculty, day, s1)] = True
                faculty_busy[(faculty, day, s2)] = True

                section_busy[(sem, sec, day, s1)] = True
                section_busy[(sem, sec, day, s2)] = True

                used_today.add(subject)
                daily[day].add("COE")
                return True

        return False

    # ============================================
    # PROCESS LOAD
    # ============================================
    for t in teaching_load:

        sem = t["Semester"]
        sec = t["Section"]
        subject = t["Subject_Name"]
        faculty = t["Faculty_Name"]

        L = t["L"]
        T = t["T"]
        P = t["P"]
        PDP = t["PDP"]
        COE = t["COE"]

        g1, g2 = generate_groups(sec)

        class_room = fixed_rooms.get((sem, sec), None)

        g1subs = group_subject_map[(sem, sec)]["G1"]
        g2subs = group_subject_map[(sem, sec)]["G2"]

        # LECTURES
        for _ in range(L):
            place_single(sem, sec, faculty, subject, "L", class_room)

        # PDP
        for _ in range(PDP):
            place_single(sem, sec, faculty, subject, "PDP", class_room)

        # COE
        for _ in range(COE):
            place_coe(sem, sec, subject, faculty, class_room)

        # TUTORIALS
        for _ in range(T):

            if not g1subs or not g2subs:
                continue

            s1 = random.choice(g1subs)
            s2 = random.choice(g2subs)

            f1 = get_faculty_for_subject(sem, sec, s1)
            f2 = get_faculty_for_subject(sem, sec, s2)

            room1, room2 = random.sample(labs, 2)

            place_two_hour(sem, sec, "T",
                           s1, s2, f1, f2,
                           g1, g2, room1, room2)

        # LABS
        for _ in range(P):

            if not g1subs or not g2subs:
                continue

            s1 = random.choice(g1subs)
            s2 = random.choice(g2subs)

            f1 = get_faculty_for_subject(sem, sec, s1)
            f2 = get_faculty_for_subject(sem, sec, s2)

            room1, room2 = random.sample(labs, 2)

            place_two_hour(sem, sec, "P",
                           s1, s2, f1, f2,
                           g1, g2, room1, room2)

    if timetable:
        db["timetable"].insert_many(timetable)

    return {"success": True, "count": len(timetable)}
