from app import db
import random

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

TIME_SLOTS = [
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00",
    "14:00-15:00",
    "15:00-16:00",
    "16:00-17:00"
]

# -------------------------------------------
# GROUP GENERATION:  A → A1,A2
# -------------------------------------------
def generate_groups(section):
    return [f"{section}1", f"{section}2"]


# -------------------------------------------
# Get faculty for SUBJECT (for correct groups)
# -------------------------------------------
def get_faculty_for_subject(sem, sec, subject):
    rec = db["teaching_load"].find_one(
        {"Semester": sem, "Section": sec, "Subject_Name": subject},
        {"Faculty_Name": 1, "_id": 0}
    )
    return rec["Faculty_Name"] if rec else ""


# ================================================================
# MAIN FUNCTION
# ================================================================
def generate_timetable():

    teaching_load = list(db["teaching_load"].find({}, {"_id": 0}))
    room_list = list(db["room_list"].find({}, {"_id": 0}))

    if not teaching_load:
        return {"success": False, "message": "Teaching load empty"}

    if not room_list:
        return {"success": False, "message": "Room list empty"}

    # Clear old data
    db["timetable"].delete_many({})

    timetable = []
    faculty_busy = {}          # (faculty, day, slot)
    section_busy = {}          # (sem, sec, day, slot)
    subject_used_daily = {}    # (sem, sec)[day] = {subjects}

    # ------------------------------------------------
    # ROOMS
    # ------------------------------------------------
    fixed_rooms = {}
    labs = []

    for r in room_list:
        if r["Room_Type"] == "Room" and r["Assigned_Semester"]:
            fixed_rooms[(r["Assigned_Semester"], r["Assigned_Section"])] = r["Room_No"]

        if r["Room_Type"] == "Lab":
            labs.append(r["Room_No"])

    # ------------------------------------------------
    # SUBJECT SPLIT FOR GROUPS  (Option B)
    # ------------------------------------------------
    group_subject_map = {}

    unique_sections = set((t["Semester"], t["Section"]) for t in teaching_load)

    for (sem, sec) in unique_sections:
        subjects = [
            t["Subject_Name"]
            for t in teaching_load
            if t["Semester"] == sem and t["Section"] == sec
        ]
        random.shuffle(subjects)

        mid = len(subjects) // 2 or 1
        group_subject_map[(sem, sec)] = {
            "G1": subjects[:mid],
            "G2": subjects[mid:]
        }

    # ------------------------------------------------
    # HELPER FOR L/PDP/COE (single slot)
    # ------------------------------------------------
    def place_single(sem, sec, faculty, subject, type_name, room):

        daily = subject_used_daily.setdefault((sem, sec), {})

        for day in DAYS:
            used_today = daily.setdefault(day, set())

            if subject in used_today:
                continue

            for slot in TIME_SLOTS:

                if faculty_busy.get((faculty, day, slot)):
                    continue

                if section_busy.get((sem, sec, day, slot)):
                    continue

                entry = {
                    "Semester": sem,
                    "Section": sec,
                    "Subject": subject,
                    "Faculty": faculty,
                    "Day": day,
                    "Slot": slot,
                    "Room": room,
                    "Type": type_name
                }

                timetable.append(entry)

                faculty_busy[(faculty, day, slot)] = True
                section_busy[(sem, sec, day, slot)] = True
                used_today.add(subject)
                return True

        return False

    # ================================================================
    # PROCESS EACH SUBJECT
    # ================================================================
    for t in teaching_load:

        sem = t["Semester"]
        sec = t["Section"]
        faculty = t["Faculty_Name"]
        subject = t["Subject_Name"]

        L = t["L"]
        T = t["T"]
        P = t["P"]
        PDP = t["PDP"]
        COE = t["COE"]

        class_room = fixed_rooms.get((sem, sec))
        g1, g2 = generate_groups(sec)

        g1_list = group_subject_map[(sem, sec)]["G1"]
        g2_list = group_subject_map[(sem, sec)]["G2"]

        # ------------------------------------------------
        # 1. LECTURES
        # ------------------------------------------------
        for _ in range(L):
            place_single(sem, sec, faculty, subject, "L", class_room)

        # ------------------------------------------------
        # 2. PDP  (single slot)
        # ------------------------------------------------
        for _ in range(PDP):
            place_single(sem, sec, faculty, subject, "PDP", class_room)

        # ------------------------------------------------
        # 3. COE — MUST BE 2 HOURS
        # ------------------------------------------------
        for _ in range(COE):

            daily = subject_used_daily.setdefault((sem, sec), {})

            for day in DAYS:

                if subject in daily.setdefault(day, set()):
                    continue

                for i in range(len(TIME_SLOTS) - 1):

                    s1 = TIME_SLOTS[i]
                    s2 = TIME_SLOTS[i + 1]

                    if faculty_busy.get((faculty, day, s1)): continue
                    if faculty_busy.get((faculty, day, s2)): continue

                    if section_busy.get((sem, sec, day, s1)): continue
                    if section_busy.get((sem, sec, day, s2)): continue

                    entry = {
                        "Semester": sem,
                        "Section": sec,
                        "Type": "COE",
                        "Subject": subject,
                        "Faculty": faculty,
                        "Day": day,
                        "Slot": s1,
                        "Slot2": s2,
                        "Room": class_room
                    }

                    timetable.append(entry)

                    for s in (s1, s2):
                        faculty_busy[(faculty, day, s)] = True
                        section_busy[(sem, sec, day, s)] = True

                    daily[day].add(subject)
                    break
                else:
                    continue
                break

        # ------------------------------------------------
        # 4. TUTORIALS (T)
        # ------------------------------------------------
        for _ in range(T):

            g1_sub = random.choice(g1_list)
            g2_sub = random.choice(g2_list)

            f1 = get_faculty_for_subject(sem, sec, g1_sub)
            f2 = get_faculty_for_subject(sem, sec, g2_sub)

            daily = subject_used_daily.setdefault((sem, sec), {})

            for day in DAYS:

                if g1_sub in daily.setdefault(day, set()): continue
                if g2_sub in daily.setdefault(day, set()): continue

                for slot in TIME_SLOTS:

                    if faculty_busy.get((f1, day, slot)): continue
                    if faculty_busy.get((f2, day, slot)): continue

                    if section_busy.get((sem, sec, day, slot)): continue
                    if section_busy.get((sem, g1, day, slot)): continue
                    if section_busy.get((sem, g2, day, slot)): continue

                    entry = {
                        "Semester": sem,
                        "Section": sec,
                        "Type": "T",
                        "Day": day,
                        "Slot": slot,
                        "Groups": [
                            {
                                "group": g1,
                                "subject": g1_sub,
                                "faculty": f1,
                                "room": random.choice(labs),
                                "type": "T"
                            },
                            {
                                "group": g2,
                                "subject": g2_sub,
                                "faculty": f2,
                                "room": random.choice(labs),
                                "type": "T"
                            }
                        ]
                    }

                    timetable.append(entry)

                    faculty_busy[(f1, day, slot)] = True
                    faculty_busy[(f2, day, slot)] = True

                    section_busy[(sem, sec, day, slot)] = True
                    section_busy[(sem, g1, day, slot)] = True
                    section_busy[(sem, g2, day, slot)] = True

                    daily[day].add(g1_sub)
                    daily[day].add(g2_sub)
                    break
                else:
                    continue
                break

        # ------------------------------------------------
        # 5. P (LAB) — 2 HOURS
        # ------------------------------------------------
        for _ in range(P):

            g1_sub = random.choice(g1_list)
            g2_sub = random.choice(g2_list)

            f1 = get_faculty_for_subject(sem, sec, g1_sub)
            f2 = get_faculty_for_subject(sem, sec, g2_sub)

            daily = subject_used_daily.setdefault((sem, sec), {})

            for day in DAYS:

                if g1_sub in daily.setdefault(day, set()): continue
                if g2_sub in daily.setdefault(day, set()): continue

                for i in range(len(TIME_SLOTS) - 1):

                    s1 = TIME_SLOTS[i]
                    s2 = TIME_SLOTS[i + 1]

                    conflict = False
                    for s in (s1, s2):
                        if faculty_busy.get((f1, day, s)): conflict = True
                        if faculty_busy.get((f2, day, s)): conflict = True
                        if section_busy.get((sem, sec, day, s)): conflict = True
                        if section_busy.get((sem, g1, day, s)): conflict = True
                        if section_busy.get((sem, g2, day, s)): conflict = True
                    if conflict:
                        continue

                    room = random.choice(labs)

                    entry = {
                        "Semester": sem,
                        "Section": sec,
                        "Type": "P",
                        "Day": day,
                        "Slot": s1,
                        "Slot2": s2,
                        "Groups": [
                            {
                                "group": g1,
                                "subject": g1_sub,
                                "faculty": f1,
                                "room": room,
                                "type": "P"
                            },
                            {
                                "group": g2,
                                "subject": g2_sub,
                                "faculty": f2,
                                "room": room,
                                "type": "P"
                            }
                        ]
                    }

                    timetable.append(entry)

                    for s in (s1, s2):
                        faculty_busy[(f1, day, s)] = True
                        faculty_busy[(f2, day, s)] = True
                        section_busy[(sem, sec, day, s)] = True
                        section_busy[(sem, g1, day, s)] = True
                        section_busy[(sem, g2, day, s)] = True

                    daily[day].add(g1_sub)
                    daily[day].add(g2_sub)
                    break
                else:
                    continue
                break

    # SAVE
    if timetable:
        db["timetable"].insert_many(timetable)

    return {"success": True, "count": len(timetable)}
