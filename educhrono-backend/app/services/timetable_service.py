from app import db
import random

# ---------------------------------------------------------------
# TIME SLOT DEFINITIONS
# ---------------------------------------------------------------

FIRST_HALF_1HR = [
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00"
]

SECOND_HALF_1HR = [
    "14:00-15:00",
    "15:00-16:00",
    "16:00-17:00"
]

FIRST_HALF_2HR = [
    ("09:00-10:00", "10:00-11:00"),
    ("10:00-11:00", "11:00-12:00")
]

SECOND_HALF_2HR = [
    ("14:00-15:00", "15:00-16:00"),
    ("15:00-16:00", "16:00-17:00")
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


# ---------------------------------------------------------------
# GROUP GENERATOR (A → A1, A2)
# ---------------------------------------------------------------
def generate_groups(section):
    return f"{section}1", f"{section}2"
def generate_timetable():

    # --------------------------------------------------------------
    # FETCH DATA
    # --------------------------------------------------------------
    teaching_load = list(db["teaching_load"].find({}, {"_id": 0}))
    room_list = list(db["room_list"].find({}, {"_id": 0}))

    if not teaching_load:
        return {"success": False, "message": "Teaching Load Empty"}

    if not room_list:
        return {"success": False, "message": "Room List Empty"}

    # Clear old timetable
    db["timetable"].delete_many({})

    # --------------------------------------------------------------
    # ROOM CATEGORIZATION
    # --------------------------------------------------------------
    classrooms = [r["Room_No"] for r in room_list if r["Room_Type"] == "Room"]
    labs = [r["Room_No"] for r in room_list if r["Room_Type"] == "Lab"]

    # Fallback safety
    if not classrooms:
        classrooms = [r["Room_No"] for r in room_list]

    if not labs:
        labs = [r["Room_No"] for r in room_list]

    timetable = []

    # --------------------------------------------------------------
    # BUSY MATRICES
    # --------------------------------------------------------------
    faculty_busy = {}         # (faculty, day, slot)
    section_busy = {}         # (semester, section, day, slot)
    group_busy = {}           # (semester, group, day, slot)

    # track daily usage:
    daily_L_used = {}         # Lecture: only 1 per subject per day
    daily_PDP_COE = {}        # PDP/COE separation
    daily_T_used = {}         # Tutorial: max 1 per subject per day
    daily_P_used = {}         # Lab: max 1 per subject per day

    # --------------------------------------------------------------
    # MARK BUSY
    # --------------------------------------------------------------
    def mark(sem, sec, faculty, day, slots, groups=None):
        groups = groups or []
        for s in slots:
            faculty_busy[(faculty, day, s)] = True
            section_busy[(sem, sec, day, s)] = True
            for g in groups:
                group_busy[(sem, g, day, s)] = True

    # --------------------------------------------------------------
    # CHECK FREE
    # --------------------------------------------------------------
    def free(sem, sec, faculty, day, slots, groups=None):
        groups = groups or []
        for s in slots:
            if faculty_busy.get((faculty, day, s)):
                return False
            if section_busy.get((sem, sec, day, s)):
                return False
            for g in groups:
                if group_busy.get((sem, g, day, s)):
                    return False
        return True
    # --------------------------------------------------------------
    # HELPER: Check and Set Daily Used Flags
    # --------------------------------------------------------------
    def mark_daily_use(daily_map, sem, sec, day, subject):
        key = (sem, sec)
        if key not in daily_map:
            daily_map[key] = {}
        if day not in daily_map[key]:
            daily_map[key][day] = set()
        daily_map[key][day].add(subject)

    def is_used_today(daily_map, sem, sec, day, subject):
        key = (sem, sec)
        return subject in daily_map.get(key, {}).get(day, set())

    # --------------------------------------------------------------
    # PLACE SINGLE-HOUR CLASS (L / PDP)
    # --------------------------------------------------------------
    def place_single(sem, sec, subject, faculty, type_name):

        # daily usage maps
        L_used = daily_L_used
        PDP_COE = daily_PDP_COE

        # room assignment rules
        if type_name == "L":
            room = classrooms[sem % len(classrooms)]
        elif type_name == "PDP":
            room = classrooms[sem % len(classrooms)]
        else:
            room = random.choice(classrooms)

        # COE/PDP cannot overlap same slot — but CAN occur same day
        def same_slot_conflict(day, slot):
            key = (sem, sec)
            if key in PDP_COE and day in PDP_COE[key]:
                if slot in PDP_COE[key][day]:  # exact slot conflict
                    return True
            return False

        # L & PDP: subject cannot repeat same day
        def subject_day_block(day):
            if type_name == "L":
                return is_used_today(L_used, sem, sec, day, subject)
            if type_name == "PDP":
                return is_used_today(L_used, sem, sec, day, subject)
            return False

        for day in DAYS:

            if subject_day_block(day):
                continue

            # first-half priority
            for slot in FIRST_HALF_1HR:
                if same_slot_conflict(day, slot):
                    continue
                if free(sem, sec, faculty, day, [slot]):

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

                    mark(sem, sec, faculty, day, [slot])

                    # mark daily usage
                    if type_name == "L":
                        mark_daily_use(L_used, sem, sec, day, subject)
                    if type_name == "PDP":
                        mark_daily_use(L_used, sem, sec, day, subject)
                        key = (sem, sec)
                        PDP_COE.setdefault(key, {}).setdefault(day, set()).add(slot)

                    return True

            # fallback second half
            for slot in SECOND_HALF_1HR:
                if same_slot_conflict(day, slot):
                    continue
                if free(sem, sec, faculty, day, [slot]):

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

                    mark(sem, sec, faculty, day, [slot])

                    if type_name == "L":
                        mark_daily_use(L_used, sem, sec, day, subject)
                    if type_name == "PDP":
                        mark_daily_use(L_used, sem, sec, day, subject)
                        key = (sem, sec)
                        PDP_COE.setdefault(key, {}).setdefault(day, set()).add(slot)

                    return True

        return False

    # --------------------------------------------------------------
    # PLACE COE (2-HOUR BLOCK)
    # --------------------------------------------------------------
    def place_coe(sem, sec, subject, faculty):

        PDP_COE = daily_PDP_COE
        L_used = daily_L_used
        room = classrooms[sem % len(classrooms)]

        # COE cannot repeat same day
        def subject_day_block(day):
            return is_used_today(L_used, sem, sec, day, subject)

        for day in DAYS:

            if subject_day_block(day):
                continue

            # FIRST HALF priority
            for s1, s2 in FIRST_HALF_2HR:
                # cannot overlap PDP in *same slot*
                key = (sem, sec)
                if key in PDP_COE and day in PDP_COE[key]:
                    if s1 in PDP_COE[key][day] or s2 in PDP_COE[key][day]:
                        continue

                if free(sem, sec, faculty, day, [s1, s2]):

                    timetable.append({
                        "Semester": sem,
                        "Section": sec,
                        "Subject": subject,
                        "Faculty": faculty,
                        "Type": "COE",
                        "Day": day,
                        "Slot": s1,
                        "Slot2": s2,
                        "Room": room
                    })

                    mark(sem, sec, faculty, day, [s1, s2])

                    mark_daily_use(L_used, sem, sec, day, subject)

                    # store COE slots
                    PDP_COE.setdefault((sem, sec), {}).setdefault(day, set()).update([s1, s2])

                    return True

            # SECOND HALF fallback
            for s1, s2 in SECOND_HALF_2HR:

                key = (sem, sec)
                if key in PDP_COE and day in PDP_COE[key]:
                    if s1 in PDP_COE[key][day] or s2 in PDP_COE[key][day]:
                        continue

                if free(sem, sec, faculty, day, [s1, s2]):

                    timetable.append({
                        "Semester": sem,
                        "Section": sec,
                        "Subject": subject,
                        "Faculty": faculty,
                        "Type": "COE",
                        "Day": day,
                        "Slot": s1,
                        "Slot2": s2,
                        "Room": room
                    })

                    mark(sem, sec, faculty, day, [s1, s2])

                    mark_daily_use(L_used, sem, sec, day, subject)

                    PDP_COE.setdefault((sem, sec), {}).setdefault(day, set()).update([s1, s2])

                    return True

        return False
    # --------------------------------------------------------------
    # PLACE TUTORIAL PAIR (T)
    # --------------------------------------------------------------
    def place_tutorial_pair(sem, sec, subj1, subj2, fac1, fac2, g1, g2):

        daily_T = daily_T_used

        # subject-day restriction: only once per subject per day
        def subject_day_block(day):
            return (
                is_used_today(daily_T, sem, sec, day, subj1)
                or is_used_today(daily_T, sem, sec, day, subj2)
            )

        for day in DAYS:

            if subject_day_block(day):
                continue

            # FIRST HALF preferred
            for slot in FIRST_HALF_1HR:

                if free(sem, sec, fac1, day, [slot], [g1]) and \
                   free(sem, sec, fac2, day, [slot], [g2]):

                    # rooms for tutorials (prefer labs)
                    room1 = labs[0] if labs else classrooms[0]
                    room2 = labs[1 % len(labs)] if labs else classrooms[1 % len(classrooms)]

                    timetable.append({
                        "Semester": sem,
                        "Section": sec,
                        "Type": "T",
                        "Day": day,
                        "Slot": slot,
                        "Groups": [
                            {"group": g1, "subject": subj1, "faculty": fac1, "room": room1},
                            {"group": g2, "subject": subj2, "faculty": fac2, "room": room2}
                        ]
                    })

                    # mark busy for both groups and faculty
                    mark(sem, sec, fac1, day, [slot], [g1])
                    mark(sem, sec, fac2, day, [slot], [g2])

                    # mark daily subject usage
                    mark_daily_use(daily_T, sem, sec, day, subj1)
                    mark_daily_use(daily_T, sem, sec, day, subj2)

                    return True

            # SECOND HALF fallback
            for slot in SECOND_HALF_1HR:

                if free(sem, sec, fac1, day, [slot], [g1]) and \
                   free(sem, sec, fac2, day, [slot], [g2]):

                    room1 = labs[0] if labs else classrooms[0]
                    room2 = labs[1 % len(labs)] if labs else classrooms[1 % len(classrooms)]

                    timetable.append({
                        "Semester": sem,
                        "Section": sec,
                        "Type": "T",
                        "Day": day,
                        "Slot": slot,
                        "Groups": [
                            {"group": g1, "subject": subj1, "faculty": fac1, "room": room1},
                            {"group": g2, "subject": subj2, "faculty": fac2, "room": room2}
                        ]
                    })

                    mark(sem, sec, fac1, day, [slot], [g1])
                    mark(sem, sec, fac2, day, [slot], [g2])

                    mark_daily_use(daily_T, sem, sec, day, subj1)
                    mark_daily_use(daily_T, sem, sec, day, subj2)

                    return True

        return False
    # --------------------------------------------------------------
    # PLACE LAB PAIR (P)
    # --------------------------------------------------------------
    def place_lab_pair(sem, sec, subj1, subj2, fac1, fac2, g1, g2):

        daily_P = daily_P_used

        # Restriction: only one lab per subject per day
        def subject_day_block(day):
            return (
                is_used_today(daily_P, sem, sec, day, subj1)
                or is_used_today(daily_P, sem, sec, day, subj2)
            )

        for day in DAYS:

            if subject_day_block(day):
                continue

            # FIRST HALF priority
            for s1, s2 in FIRST_HALF_2HR:

                if free(sem, sec, fac1, day, [s1, s2], [g1]) and \
                   free(sem, sec, fac2, day, [s1, s2], [g2]):

                    # Prefer labs
                    if len(labs) >= 2:
                        room1, room2 = random.sample(labs, 2)
                    else:
                        room1, room2 = random.sample(classrooms, 2)

                    timetable.append({
                        "Semester": sem,
                        "Section": sec,
                        "Type": "P",
                        "Day": day,
                        "Slot": s1,
                        "Slot2": s2,
                        "Groups": [
                            {"group": g1, "subject": subj1, "faculty": fac1, "room": room1},
                            {"group": g2, "subject": subj2, "faculty": fac2, "room": room2}
                        ]
                    })

                    # Mark faculty, section, groups busy
                    mark(sem, sec, fac1, day, [s1, s2], [g1])
                    mark(sem, sec, fac2, day, [s1, s2], [g2])

                    # Daily subject usage
                    mark_daily_use(daily_P, sem, sec, day, subj1)
                    mark_daily_use(daily_P, sem, sec, day, subj2)

                    return True

            # SECOND HALF fallback
            for s1, s2 in SECOND_HALF_2HR:

                if free(sem, sec, fac1, day, [s1, s2], [g1]) and \
                   free(sem, sec, fac2, day, [s1, s2], [g2]):

                    if len(labs) >= 2:
                        room1, room2 = random.sample(labs, 2)
                    else:
                        room1, room2 = random.sample(classrooms, 2)

                    timetable.append({
                        "Semester": sem,
                        "Section": sec,
                        "Type": "P",
                        "Day": day,
                        "Slot": s1,
                        "Slot2": s2,
                        "Groups": [
                            {"group": g1, "subject": subj1, "faculty": fac1, "room": room1},
                            {"group": g2, "subject": subj2, "faculty": fac2, "room": room2}
                        ]
                    })

                    mark(sem, sec, fac1, day, [s1, s2], [g1])
                    mark(sem, sec, fac2, day, [s1, s2], [g2])

                    mark_daily_use(daily_P, sem, sec, day, subj1)
                    mark_daily_use(daily_P, sem, sec, day, subj2)

                    return True

        return False
    # --------------------------------------------------------------
    # GROUP TEACHING LOAD BY (SEMESTER, SECTION)
    # --------------------------------------------------------------
    grouped = {}
    for it in teaching_load:
        key = (it["Semester"], it["Section"])
        grouped.setdefault(key, []).append(it)

    # --------------------------------------------------------------
    # SORT SUBJECTS (T / P)
    # --------------------------------------------------------------
    def get_sorted_subjects(items, key_type):
        """Return subjects with T or P > 0 sorted alphabetically"""
        result = []

        for it in items:
            if it[key_type] > 0:
                result.append({
                    "subject": it["Subject_Name"],
                    "faculty": it["Faculty_Name"],
                    "count": it[key_type]
                })

        result.sort(key=lambda x: x["subject"])
        return result

    # --------------------------------------------------------------
    # BUILD PAIRS (Option A strict: every hour paired)
    # --------------------------------------------------------------
    def build_pairs(subject_list, total_pairs_needed):
        """
        Build subject pairs for T/P.
        Must ensure:
        - s1 != s2
        - round-robin pairing
        """
        if len(subject_list) < 2:
            return []

        pairs = []
        idx = 0

        while len(pairs) < total_pairs_needed:
            s1 = subject_list[idx % len(subject_list)]
            s2 = subject_list[(idx + 1) % len(subject_list)]

            if s1["subject"] != s2["subject"]:
                pairs.append((s1, s2))

            idx += 1  # move one step only for better rotation

        return pairs
    # --------------------------------------------------------------
    # FIRST PASS: PLACE LECTURES → PDP → COE
    # --------------------------------------------------------------
    for (sem, sec), items in grouped.items():

        # ------------------------------
        # 1) PLACE ALL LECTURES (L)
        # ------------------------------
        for it in items:
            for _ in range(it["L"]):
                place_single(
                    sem=sem,
                    sec=sec,
                    subject=it["Subject_Name"],
                    faculty=it["Faculty_Name"],
                    type_name="L"
                )

        # -------------------------------------
        # 2) PLACE PDP (AFTER ALL L’s)
        # -------------------------------------
        for it in items:
            for _ in range(it["PDP"]):
                place_single(
                    sem=sem,
                    sec=sec,
                    subject=it["Subject_Name"],
                    faculty=it["Faculty_Name"],
                    type_name="PDP"
                )

        # -------------------------------------
        # 3) PLACE COE (2 Hr block)
        # -------------------------------------
        for it in items:
            for _ in range(it["COE"]):
                place_coe(
                    sem=sem,
                    sec=sec,
                    subject=it["Subject_Name"],
                    faculty=it["Faculty_Name"]
                )
    # --------------------------------------------------------------
    # SECOND PASS: PLACE TUTORIALS (T) & LABS (P)
    # --------------------------------------------------------------
    for (sem, sec), items in grouped.items():

        # GROUPS (e.g., A → A1, A2)
        g1, g2 = generate_groups(sec)

        # -------------------------
        # TUTORIAL PAIRS (T)
        # -------------------------
        t_list = get_sorted_subjects(items, "T")
        total_T = sum(i["T"] for i in items)

        t_pairs = build_pairs(t_list, total_T)

        for s1, s2 in t_pairs:
            place_tutorial_pair(
                sem=sem,
                sec=sec,
                subj1=s1["subject"],
                subj2=s2["subject"],
                fac1=s1["faculty"],
                fac2=s2["faculty"],
                g1=g1,
                g2=g2
            )

        # -------------------------
        # LAB PAIRS (P)
        # -------------------------
        p_list = get_sorted_subjects(items, "P")
        total_P = sum(i["P"] for i in items)

        p_pairs = build_pairs(p_list, total_P)

        for s1, s2 in p_pairs:
            place_lab_pair(
                sem=sem,
                sec=sec,
                subj1=s1["subject"],
                subj2=s2["subject"],
                fac1=s1["faculty"],
                fac2=s2["faculty"],
                g1=g1,
                g2=g2
            )
    # --------------------------------------------------------------
    # SAVE FINAL TIMETABLE INTO DB
    # --------------------------------------------------------------
    if timetable:
        db["timetable"].insert_many(timetable)

    return {
        "success": True,
        "message": "Timetable generated successfully",
        "count": len(timetable)
    }

# END OF FILE
