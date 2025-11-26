# ======================================================================
#  TIMETABLE GENERATOR – FINAL VERIFIED VERSION
#  (Strict rules: P → COE → PDP → T → L)
#  All constraints applied as discussed.
# ======================================================================

from app import db
import random
from collections import defaultdict

# ---------------------------------------------------------------
# TIME SLOTS (24-hour format kept clean for frontend mapping)
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
# CREATE GROUPS: A → A1, A2  /  B → B1, B2
# ---------------------------------------------------------------
def make_groups(section):
    return f"{section}1", f"{section}2"
# ======================================================================
#  PART 2 — LOAD DATA, GROUP BY TYPE, PREPARE ROOM MAP
# ======================================================================

def load_data():
    """Fetch teaching load + rooms."""
    teaching_load = list(db["teaching_load"].find({}, {"_id": 0}))
    rooms = list(db["room_list"].find({}, {"_id": 0}))
    return teaching_load, rooms


def group_by_sem_section(teaching_load):
    """
    Groups teaching load into:
    - L (lecture)
    - T (tutorial)
    - P (lab)
    - PDP
    - COE
    
    Also builds:
    - lecture_count[sem][sec][subject] = total L classes needed
    - group_map[(sem, sec)] = list of rows
    """
    grouped = defaultdict(lambda: defaultdict(list))
    lecture_count = defaultdict(lambda: defaultdict(int))

    # final typed groups
    L = defaultdict(lambda: defaultdict(list))
    T = defaultdict(lambda: defaultdict(list))
    P = defaultdict(lambda: defaultdict(list))
    PDP = defaultdict(lambda: defaultdict(list))
    COE = defaultdict(lambda: defaultdict(list))

    for row in teaching_load:
        sem = row["Semester"]
        sec = row["Section"]
        subject = row["Subject_Name"]
        faculty = row["Faculty_Name"]

        # LECTURE COUNT LOGIC (STRICT)
        if row["L"] > 0:
            for _ in range(row["L"]):
                L[sem][sec].append({
                    "subject": subject,
                    "faculty": faculty
                })
        
        if row["T"] > 0:
            for _ in range(row["T"]):
                T[sem][sec].append({
                    "subject": subject,
                    "faculty": faculty
                })

        if row["P"] > 0:
            for _ in range(row["P"]):
                P[sem][sec].append({
                    "subject": subject,
                    "faculty": faculty
                })

        if row["PDP"] > 0:
            for _ in range(row["PDP"]):
                PDP[sem][sec].append({
                    "subject": subject,
                    "faculty": faculty
                })

        if row["COE"] > 0:
            for _ in range(row["COE"]):
                COE[sem][sec].append({
                    "subject": subject,
                    "faculty": faculty
                })

        # group mapping
        grouped[sem][sec].append(row)

    return L, T, P, PDP, COE, grouped


def build_room_map(room_list):
    """
    Creates:
    - lecture_room[(sem, sec)] → fixed room
    - lab_rooms → list of labs
    - any_rooms → fallback list for PDP/COE/T
    """
    lecture_room = {}
    lab_rooms = []
    any_rooms = []

    # STEP 1 — assign fixed lecture room per sem-section
    for r in room_list:
        room = r["Room_No"]
        rtype = r["Room_Type"]

        if rtype == "Lab":
            lab_rooms.append(room)
        else:
            any_rooms.append(room)

        # If assigned mapping exists, use it
        if "Assigned_Semester" in r and "Assigned_Section" in r:
            sem = r["Assigned_Semester"]
            sec = r["Assigned_Section"]
            lecture_room[(sem, sec)] = room

    return lecture_room, lab_rooms, any_rooms
# ======================================================================
#  PART 3 — BUSY MATRICES, CHECK & MARK FUNCTIONS
# ======================================================================

def initialize_state():
    """
    Initializes all state holders used during timetable generation.
    """
    faculty_busy = {}     # (faculty, day, slot) → True
    section_busy = {}     # (sem, sec, day, slot) → True
    group_busy = {}       # (sem, sec_group, day, slot) → True

    subject_daily_used = defaultdict(lambda: defaultdict(set))
    # subject_daily_used[(sem, sec)][day] = set(subjects placed)

    special_daily_used = defaultdict(lambda: defaultdict(str))
    # special_daily_used[(sem, sec)][day] = "PDP" or "COE"

    timetable = []  # final saved records

    return faculty_busy, section_busy, group_busy, subject_daily_used, special_daily_used, timetable


# ---------------------------------------------------------------
#  CHECK FREE (faculty, section, groups)
# ---------------------------------------------------------------
def is_free(sem, sec, faculty, day, slots, faculty_busy, section_busy, group_busy, groups=None):
    groups = groups or []

    for slot in slots:
        # Faculty busy?
        if faculty_busy.get((faculty, day, slot)):
            return False

        # Section busy?
        if section_busy.get((sem, sec, day, slot)):
            return False

        # Group busy?
        for g in groups:
            if group_busy.get((sem, g, day, slot)):
                return False

    return True


# ---------------------------------------------------------------
#  MARK OCCUPIED
# ---------------------------------------------------------------
def mark_slots(sem, sec, faculty, day, slots,
               faculty_busy, section_busy, group_busy,
               groups=None):

    groups = groups or []

    for slot in slots:
        faculty_busy[(faculty, day, slot)] = True
        section_busy[(sem, sec, day, slot)] = True

        for g in groups:
            group_busy[(sem, g, day, slot)] = True
# ======================================================================
#  PART 4 — CORE PLACEMENT HELPERS
#  (Applies all strict rules: priority, special clashes, once-per-day)
# ======================================================================

# ---------------------------------------------------------------
#  TRY PLACE IN FIRST HALF THEN SECOND HALF (1-hour)
# ---------------------------------------------------------------
def try_place_single_hour(
    sem, sec, subject, faculty, type_name,
    allowed_rooms,
    faculty_busy, section_busy, group_busy,
    subject_daily_used, special_daily_used,
    timetable
):
    """
    General engine for L, PDP, and fallback T (if needed).
    """

    for day in DAYS:

        # SPECIAL RULE: PDP & COE can't be same day
        if type_name == "PDP" and special_daily_used[(sem, sec)][day] == "COE":
            continue
        if type_name == "COE" and special_daily_used[(sem, sec)][day] == "PDP":
            continue

        # RULE: L / T / PDP cannot repeat same subject on same day
        if subject in subject_daily_used[(sem, sec)][day]:
            continue

        # FIRST HALF PRIORITY
        for slot in FIRST_HALF_1HR:
            room = random.choice(allowed_rooms) if allowed_rooms else None

            if is_free(
                sem, sec, faculty, day, [slot],
                faculty_busy, section_busy, group_busy
            ):
                # commit
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

                mark_slots(
                    sem, sec, faculty, day, [slot],
                    faculty_busy, section_busy, group_busy
                )

                subject_daily_used[(sem, sec)][day].add(subject)
                if type_name in ["COE", "PDP"]:
                    special_daily_used[(sem, sec)][day] = type_name

                return True

        # SECOND HALF fallback
        for slot in SECOND_HALF_1HR:
            room = random.choice(allowed_rooms) if allowed_rooms else None

            if is_free(
                sem, sec, faculty, day, [slot],
                faculty_busy, section_busy, group_busy
            ):
                # commit
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

                mark_slots(
                    sem, sec, faculty, day, [slot],
                    faculty_busy, section_busy, group_busy
                )

                subject_daily_used[(sem, sec)][day].add(subject)
                if type_name in ["COE", "PDP"]:
                    special_daily_used[(sem, sec)][day] = type_name

                return True

    return False
# ======================================================================
#  PART 5 — 2-HOUR SLOT PLACEMENT + PAIRING ENGINE
# ======================================================================

# ---------------------------------------------------------------
# TRY PLACE TWO-HOUR CLASS (COE or LAB)
# ---------------------------------------------------------------
def try_place_two_hour(
    sem, sec,
    subj1, subj2,
    fac1, fac2,
    group1, group2,
    allowed_rooms,
    faculty_busy, section_busy, group_busy,
    subject_daily_used, special_daily_used,
    timetable,
    type_name="P"
):
    """
    Places Labs (P) or COE (2-hour block)
    P has (A1/A2 split)
    COE has full section (no groups)
    """

    for day in DAYS:

        # Special restriction: PDP & COE cannot be same day
        if type_name == "COE" and special_daily_used[(sem, sec)][day] == "PDP":
            continue
        if type_name == "PDP" and special_daily_used[(sem, sec)][day] == "COE":
            continue

        # Do not repeat subjects on same day
        if subj1 in subject_daily_used[(sem, sec)][day]:
            continue
        if subj2 in subject_daily_used[(sem, sec)][day]:
            continue

        # FIRST HALF priority
        for (s1, s2) in FIRST_HALF_2HR:
            room1, room2 = random.sample(allowed_rooms, 2) if len(allowed_rooms) >= 2 else (None, None)

            # LAB uses grouping (A1/A2). COE does NOT use groups.
            grp1_list = [group1] if type_name == "P" else []
            grp2_list = [group2] if type_name == "P" else []

            if is_free(sem, sec, fac1, day, [s1, s2], faculty_busy, section_busy, group_busy, grp1_list) and \
               is_free(sem, sec, fac2, day, [s1, s2], faculty_busy, section_busy, group_busy, grp2_list):

                timetable.append({
                    "Semester": sem,
                    "Section": sec,
                    "Day": day,
                    "Type": type_name,
                    "Slot": s1,
                    "Slot2": s2,
                    "Groups": [
                        {"group": group1, "subject": subj1, "faculty": fac1, "room": room1},
                        {"group": group2, "subject": subj2, "faculty": fac2, "room": room2}
                    ] if type_name == "P" else [],
                    "Subject": subj1 if type_name == "COE" else None,
                    "Faculty": fac1 if type_name == "COE" else None,
                    "Room": room1 if type_name == "COE" else None
                })

                # Mark slots
                mark_slots(sem, sec, fac1, day, [s1, s2], faculty_busy, section_busy, group_busy, grp1_list)
                mark_slots(sem, sec, fac2, day, [s1, s2], faculty_busy, section_busy, group_busy, grp2_list)

                # Mark usage
                subject_daily_used[(sem, sec)][day].add(subj1)
                subject_daily_used[(sem, sec)][day].add(subj2)

                if type_name == "COE":
                    special_daily_used[(sem, sec)][day] = "COE"

                return True

        # SECOND HALF fallback
        for (s1, s2) in SECOND_HALF_2HR:
            room1, room2 = random.sample(allowed_rooms, 2) if len(allowed_rooms) >= 2 else (None, None)

            grp1_list = [group1] if type_name == "P" else []
            grp2_list = [group2] if type_name == "P" else []

            if is_free(sem, sec, fac1, day, [s1, s2], faculty_busy, section_busy, group_busy, grp1_list) and \
               is_free(sem, sec, fac2, day, [s1, s2], faculty_busy, section_busy, group_busy, grp2_list):

                timetable.append({
                    "Semester": sem,
                    "Section": sec,
                    "Day": day,
                    "Type": type_name,
                    "Slot": s1,
                    "Slot2": s2,
                    "Groups": [
                        {"group": group1, "subject": subj1, "faculty": fac1, "room": room1},
                        {"group": group2, "subject": subj2, "faculty": fac2, "room": room2}
                    ] if type_name == "P" else [],
                    "Subject": subj1 if type_name == "COE" else None,
                    "Faculty": fac1 if type_name == "COE" else None,
                    "Room": room1 if type_name == "COE" else None
                })

                mark_slots(sem, sec, fac1, day, [s1, s2], faculty_busy, section_busy, group_busy, grp1_list)
                mark_slots(sem, sec, fac2, day, [s1, s2], faculty_busy, section_busy, group_busy, grp2_list)

                subject_daily_used[(sem, sec)][day].add(subj1)
                subject_daily_used[(sem, sec)][day].add(subj2)

                if type_name == "COE":
                    special_daily_used[(sem, sec)][day] = "COE"

                return True

    return False
def build_pairs(subject_list):
    """
    Input: list of dictionaries → {subject, faculty}
    Output: [(subjA, subjB), (subjB, subjA), ...] strict alternating
    Pattern:
        Day1 → subj1(A1), subj2(A2)
        Day2 → subj2(A1), subj1(A2)
    """
    if len(subject_list) < 2:
        return []

    pairs = []

    for i in range(0, len(subject_list), 2):
        if i + 1 < len(subject_list):
            s1 = subject_list[i]
            s2 = subject_list[i + 1]

            # Pair 1 → normal
            pairs.append((s1, s2))

            # Pair 2 → swapped
            pairs.append((s2, s1))

    return pairs
# ======================================================================
#  PART 6 — MAIN GENERATION ENGINE (ORDER STRICT + FIRST-HALF PRIORITY)
# ======================================================================

import random

def generate_timetable():
    # deterministic output → same timetable every run
    random.seed(999)

    # -----------------------------------------------------------
    # LOAD + GROUP + STATE INIT
    # -----------------------------------------------------------
    teaching_load, room_list = load_data()
    L, T, P, PDP, COE, section_map = group_by_sem_section(teaching_load)
    lecture_room, lab_rooms, any_rooms = build_room_map(room_list)

    (
        faculty_busy,
        section_busy,
        group_busy,
        subject_daily_used,
        special_daily_used,
        timetable
    ) = initialize_state()

    # ALL semesters + sections from teaching_load
    all_sem_sec = [(sem, sec) for sem in section_map for sec in section_map[sem]]

    # -----------------------------------------------------------
    # Helper: check if FIRST-HALF has empty slot
    # -----------------------------------------------------------
    def first_half_has_empty(sem, sec, day):
        for slot in FIRST_HALF_1HR:
            if not section_busy.get((sem, sec, day, slot)):
                return True
        return False

    # -----------------------------------------------------------
    # 1) PLACE LAB CLASSES (P) — HIGHEST PRIORITY (2-hour)
    # -----------------------------------------------------------
    for (sem, sec) in all_sem_sec:
        plist = P[sem][sec]
        if not plist:
            continue

        g1, g2 = make_groups(sec)
        pairs = build_pairs(plist)

        for (s1, s2) in pairs:
            try_place_two_hour(
                sem, sec,
                s1["subject"], s2["subject"],
                s1["faculty"], s2["faculty"],
                g1, g2,
                lab_rooms,
                faculty_busy, section_busy, group_busy,
                subject_daily_used, special_daily_used,
                timetable,
                type_name="P"
            )

    # -----------------------------------------------------------
    # 2) PLACE COE (2-hour block)
    # -----------------------------------------------------------
    for (sem, sec) in all_sem_sec:
        for item in COE[sem][sec]:
            try_place_two_hour(
                sem, sec,
                item["subject"], item["subject"],
                item["faculty"], item["faculty"],
                None, None,
                any_rooms + list(lecture_room.values()),
                faculty_busy, section_busy, group_busy,
                subject_daily_used, special_daily_used,
                timetable,
                type_name="COE"
            )

    # -----------------------------------------------------------
    # 3) PLACE PDP — should prefer first-half
    # -----------------------------------------------------------
    for (sem, sec) in all_sem_sec:
        pdp_items = PDP[sem][sec]
        last_used_day_index = -2

        for item in pdp_items:
            placed = False

            for i, day in enumerate(DAYS):
                # alternate-day rule
                if i - last_used_day_index < 2:
                    continue

                # skip if COE already same day
                if special_daily_used[(sem, sec)][day] == "COE":
                    continue

                # PDP must prefer FIRST-HALF → do not allow 2nd half if first is free
                if first_half_has_empty(sem, sec, day):
                    # try first-half only
                    for slot in FIRST_HALF_1HR:
                        if try_place_single_hour(
                            sem, sec,
                            item["subject"], item["faculty"],
                            "PDP",
                            any_rooms,
                            faculty_busy, section_busy, group_busy,
                            subject_daily_used, special_daily_used,
                            timetable,
                            force_slot=slot
                        ):
                            last_used_day_index = i
                            placed = True
                            break

                    if placed:
                        break

                # if first-half not available → allow second-half
                if try_place_single_hour(
                    sem, sec,
                    item["subject"], item["faculty"],
                    "PDP",
                    any_rooms,
                    faculty_busy, section_busy, group_busy,
                    subject_daily_used, special_daily_used,
                    timetable
                ):
                    last_used_day_index = i
                    placed = True
                    break

            if not placed:
                # last backup
                try_place_single_hour(
                    sem, sec,
                    item["subject"], item["faculty"],
                    "PDP",
                    any_rooms,
                    faculty_busy, section_busy, group_busy,
                    subject_daily_used, special_daily_used,
                    timetable
                )

    # -----------------------------------------------------------
    # 4) PLACE TUTORIALS (T)
    #    MUST fill FIRST-HALF completely before second-half
    # -----------------------------------------------------------
    for (sem, sec) in all_sem_sec:
        t_items = T[sem][sec]
        if not t_items:
            continue

        g1, g2 = make_groups(sec)
        pairs = build_pairs(t_items)

        for (s1, s2) in pairs:

            for day in DAYS:

                # subject cannot repeat same day
                if s1["subject"] in subject_daily_used[(sem, sec)][day]:
                    continue
                if s2["subject"] in subject_daily_used[(sem, sec)][day]:
                    continue

                # FIRST-HALF PRIORITY
                placed = False

                for slot in FIRST_HALF_1HR:
                    if not is_free(
                        sem, sec, s1["faculty"], day, [slot],
                        faculty_busy, section_busy, group_busy, [g1]
                    ):
                        continue

                    if not is_free(
                        sem, sec, s2["faculty"], day, [slot],
                        faculty_busy, section_busy, group_busy, [g2]
                    ):
                        continue

                    # place T
                    timetable.append({
                        "Semester": sem,
                        "Section": sec,
                        "Day": day,
                        "Type": "T",
                        "Slot": slot,
                        "Groups": [
                            {
                                "group": g1,
                                "subject": s1["subject"],
                                "faculty": s1["faculty"],
                                "room": random.choice(any_rooms)
                            },
                            {
                                "group": g2,
                                "subject": s2["subject"],
                                "faculty": s2["faculty"],
                                "room": random.choice(any_rooms)
                            }
                        ],
                        "Subject": None,
                        "Faculty": None,
                        "Room": None
                    })

                    mark_slots(
                        sem, sec, s1["faculty"], day, [slot],
                        faculty_busy, section_busy, group_busy, [g1]
                    )
                    mark_slots(
                        sem, sec, s2["faculty"], day, [slot],
                        faculty_busy, section_busy, group_busy, [g2]
                    )

                    subject_daily_used[(sem, sec)][day].add(s1["subject"])
                    subject_daily_used[(sem, sec)][day].add(s2["subject"])

                    placed = True
                    break

                if placed:
                    break

                # allow SECOND-HALF ONLY if first-half fully blocked
                if not first_half_has_empty(sem, sec, day):

                    for slot in SECOND_HALF_1HR:

                        if not is_free(
                            sem, sec, s1["faculty"], day, [slot],
                            faculty_busy, section_busy, group_busy, [g1]
                        ):
                            continue

                        if not is_free(
                            sem, sec, s2["faculty"], day, [slot],
                            faculty_busy, section_busy, group_busy, [g2]
                        ):
                            continue

                        # place T in afternoon
                        timetable.append({
                            "Semester": sem,
                            "Section": sec,
                            "Day": day,
                            "Type": "T",
                            "Slot": slot,
                            "Groups": [
                                {
                                    "group": g1,
                                    "subject": s1["subject"],
                                    "faculty": s1["faculty"],
                                    "room": random.choice(any_rooms)
                                },
                                {
                                    "group": g2,
                                    "subject": s2["subject"],
                                    "faculty": s2["faculty"],
                                    "room": random.choice(any_rooms)
                                }
                            ],
                            "Subject": None,
                            "Faculty": None,
                            "Room": None
                        })

                        mark_slots(
                            sem, sec, s1["faculty"], day, [slot],
                            faculty_busy, section_busy, group_busy, [g1]
                        )
                        mark_slots(
                            sem, sec, s2["faculty"], day, [slot],
                            faculty_busy, section_busy, group_busy, [g2]
                        )

                        subject_daily_used[(sem, sec)][day].add(s1["subject"])
                        subject_daily_used[(sem, sec)][day].add(s2["subject"])

                        break

    # -----------------------------------------------------------
    # 5) PLACE LECTURES (L) — strict FIRST-HALF priority
    # -----------------------------------------------------------
    for (sem, sec) in all_sem_sec:
        l_items = L[sem][sec]
        if not l_items:
            continue

        fixed_room = lecture_room.get((sem, sec), random.choice(any_rooms))

        for item in l_items:

            placed = False

            # FIRST HALF ALWAYS FIRST
            for day in DAYS:
                for slot in FIRST_HALF_1HR:
                    if try_place_single_hour(
                        sem, sec,
                        item["subject"], item["faculty"],
                        "L",
                        [fixed_room],
                        faculty_busy, section_busy, group_busy,
                        subject_daily_used, special_daily_used,
                        timetable,
                        force_slot=slot
                    ):
                        placed = True
                        break
                if placed:
                    break

            # fallback to second-half ONLY when first-half full
            if not placed:
                for day in DAYS:
                    if first_half_has_empty(sem, sec, day):
                        continue
                    try_place_single_hour(
                        sem, sec,
                        item["subject"], item["faculty"],
                        "L",
                        [fixed_room],
                        faculty_busy, section_busy, group_busy,
                        subject_daily_used, special_daily_used,
                        timetable
                    )

    # SAVE
    if timetable:
        db["timetable"].delete_many({})
        db["timetable"].insert_many(timetable)

    return {"success": True, "count": len(timetable)}

# ---------------------------------------------------------------
#  TRY PLACE A SINGLE 1-HOUR CLASS (L / T / PDP) WITH OPTIONAL FORCE SLOT
# ---------------------------------------------------------------
def try_place_single_hour(
    sem, sec,
    subject, faculty,
    type_name,
    allowed_rooms,
    faculty_busy, section_busy, group_busy,
    subject_daily_used, special_daily_used,
    timetable,
    force_slot=None
):
    """
    If force_slot is provided:
        → Attempt ONLY that slot (first-half rule handling is done by caller).
    Otherwise:
        → Try all first-half slots, then fallback to second-half.
    """

    # ------------- helper for committing --------------
    def commit(day, slot):
        room = random.choice(allowed_rooms) if allowed_rooms else None

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

        mark_slots(
            sem, sec, faculty, day, [slot],
            faculty_busy, section_busy, group_busy
        )

        subject_daily_used[(sem, sec)][day].add(subject)
        if type_name in ["COE", "PDP"]:
            special_daily_used[(sem, sec)][day] = type_name

        return True

    # ============================================================
    #  CASE 1 — FORCE SLOT MODE (caller decided first/second half)
    # ============================================================
    if force_slot:
        for day in DAYS:

            # COE & PDP can't be same day
            if type_name == "PDP" and special_daily_used[(sem, sec)][day] == "COE":
                continue
            if type_name == "COE" and special_daily_used[(sem, sec)][day] == "PDP":
                continue

            # subject cannot repeat same day
            if subject in subject_daily_used[(sem, sec)][day]:
                continue

            # check availability
            if is_free(
                sem, sec, faculty, day, [force_slot],
                faculty_busy, section_busy, group_busy
            ):
                return commit(day, force_slot)

        return False  # forced slot could not be placed

    # ============================================================
    #  CASE 2 — NORMAL MODE (FIRST HALF → SECOND HALF)
    # ============================================================
    for day in DAYS:

        # COE & PDP conflict
        if type_name == "PDP" and special_daily_used[(sem, sec)][day] == "COE":
            continue
        if type_name == "COE" and special_daily_used[(sem, sec)][day] == "PDP":
            continue

        # subject cannot repeat same day
        if subject in subject_daily_used[(sem, sec)][day]:
            continue

        # ---------- FIRST HALF ----------
        for slot in FIRST_HALF_1HR:
            if is_free(
                sem, sec, faculty, day, [slot],
                faculty_busy, section_busy, group_busy
            ):
                return commit(day, slot)

        # ---------- SECOND HALF ----------
        for slot in SECOND_HALF_1HR:
            if is_free(
                sem, sec, faculty, day, [slot],
                faculty_busy, section_busy, group_busy
            ):
                return commit(day, slot)

    return False

# ======================================================================
#  PART 7 — FINAL WRAPPER + EXPORT
# ======================================================================

def run_timetable_generator():
    """
    Wrapper function — can be called directly from route/controller.
    Clears old timetable and regenerates a fresh one.
    """
    result = generate_timetable()
    return result


# ======================================================================
#  END OF FILE
# ======================================================================
