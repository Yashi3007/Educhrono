
# ======================================================================
#  TIMETABLE GENERATOR – FINAL VERSION (WITH FIXED PROJECT1 + COE ROOMS)
# ======================================================================
#  Requirements implemented:
#
#   1) 4th year (Semester 7), Sections A / B / C:
#        • All subjects whose name contains "project1"
#          are treated as Project1 Lab.
#        • Project1 Lab is FIXED on:
#              Wednesday, Thursday, Friday
#              11:00–12:00 and 12:00–13:00  (2-hour block)
#        • Stored as Type="P" (lab), full section (no A1/A2 split).
#
#   2) COE Labs:
#        • All Semester 3 COE classes are in room  B-202  only.
#        • All Semester 5 COE classes are in room  B-201  only.
#        • No overlapping COE in same room & time.
#
#   3) GAP RULE for each section per day:
#        Once any slot is occupied, a later slot can be used only if
#        the previous slot in the chain is already filled.
#        Slot chain:
#           09–10 → 10–11 → 11–12 → 12–13 → 14–15 → 15–16 → 16–17
#
#   4) Priority of placement:
#        Project1 (fixed) → Labs (P) → COE → PDP → Tutorials (T) → Lectures (L)
#
#  Collections:
#       teaching_load  : input load
#       room_list      : rooms
#       timetable      : output timetable (cleared, then insert_many)
#
# ======================================================================

from app import db
import random
from collections import defaultdict

# ======================================================================
#  PART 1 – CONSTANTS: SLOTS, DAYS, PROJECT CONFIG
# ======================================================================

FIRST_HALF_1HR = [
    "09:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-13:00",
]

SECOND_HALF_1HR = [
    "14:00-15:00",
    "15:00-16:00",
    "16:00-17:00",
]

FIRST_HALF_2HR = [
    ("09:00-10:00", "10:00-11:00"),
    ("10:00-11:00", "11:00-12:00"),
    ("11:00-12:00", "12:00-13:00"),
]

SECOND_HALF_2HR = [
    ("14:00-15:00", "15:00-16:00"),
    ("15:00-16:00", "16:00-17:00"),
]

ALL_SLOTS_ORDER = FIRST_HALF_1HR + SECOND_HALF_1HR

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# ---------------------------------------------------------------
#  FIXED PROJECT CONFIG (HARD-CODED)
#  Sem 7 → Project1
#  Sem 8 → Project2
#  Sections → A, B, C
#  Days → Wednesday, Thursday, Friday
#  Time → 11:00–12:00 & 12:00–13:00
# ---------------------------------------------------------------

FIXED_PROJECT_CONFIG = {
    7: {   # 4th Year – Semester 7 → PROJECT1
        "keyword": "project1",
        "Sections": ["A", "B", "C"],
        "Days": ["Wednesday", "Thursday", "Friday"],
        "Slots": ("11:00-12:00", "12:00-13:00"),
    },
    8: {   # 4th Year – Semester 8 → PROJECT2
        "keyword": "project2",
        "Sections": ["A", "B", "C"],
        "Days": ["Wednesday", "Thursday", "Friday"],
        "Slots": ("11:00-12:00", "12:00-13:00"),
    },
}


# Fixed Project1 config – ONLY Semester 7
PROJECT1_FIXED_SEM = 7
PROJECT1_FIXED_SECTIONS = ["A", "B", "C"]
PROJECT1_FIXED_DAYS = ["Wednesday", "Thursday", "Friday"]
PROJECT1_FIXED_SLOTS = ("11:00-12:00", "12:00-13:00")

# Saturday holiday only for 4th year
SATURDAY_HOLIDAY_SEMS = [7, 8]


# ======================================================================
#  PART 2 – SMALL HELPERS
# ======================================================================

def to_int(value, default=0):
    """
    Safe int conversion.
    Handles: '', None, '  ', '7', 7, '7.0'
    """
    try:
        s = str(value).strip()
        if s == "" or s.lower() == "nan":
            return default
        if "." in s:
            return int(float(s))
        return int(s)
    except Exception:
        return default


def make_groups(section):
    """Create two groups for labs/tutorials: A → A1/A2 etc."""
    sec = str(section).strip()
    return f"{sec}1", f"{sec}2"


def is_saturday_holiday(sem, day):
    """Sem 7 & 8: no classes on Saturday."""
    return sem in SATURDAY_HOLIDAY_SEMS and day == "Saturday"


def can_place_without_gap(sem, sec, day, slot, section_busy):
    """
    Gap rule: slot allowed only if
        • it is the first slot in chain, OR
        • previous slot is already filled for that section/day.
    """
    if slot not in ALL_SLOTS_ORDER:
        return True

    idx = ALL_SLOTS_ORDER.index(slot)
    if idx == 0:
        return True

    prev_slot = ALL_SLOTS_ORDER[idx - 1]
    return section_busy.get((sem, sec, day, prev_slot), False)


# ======================================================================
#  PART 3 – LOAD DATA & GROUP BY SEM-SECTION
# ======================================================================

def load_data():
    teaching_load = list(db["teaching_load"].find({}, {"_id": 0}))
    rooms = list(db["room_list"].find({}, {"_id": 0}))
    return teaching_load, rooms


def group_by_sem_section(teaching_load):
    """
    Expand numeric loads into single units.
    Returns:
        L, T, P, PDP, COE, section_map
    """
    L = defaultdict(lambda: defaultdict(list))
    T = defaultdict(lambda: defaultdict(list))
    P = defaultdict(lambda: defaultdict(list))
    PDP = defaultdict(lambda: defaultdict(list))
    COE = defaultdict(lambda: defaultdict(list))
    section_map = defaultdict(lambda: defaultdict(list))

    for row in teaching_load:
        sem = to_int(row.get("Semester"), 0)
        if sem == 0:   # skip invalid rows
            continue

        sec = str(row.get("Section", "")).strip()
        if not sec:
            continue

        subject = str(row.get("Subject_Name", "")).strip()
        faculty = str(row.get("Faculty_Name", "")).strip()

        l_cnt = to_int(row.get("L"), 0)
        t_cnt = to_int(row.get("T"), 0)
        p_cnt = to_int(row.get("P"), 0)
        coe_cnt = to_int(row.get("COE"), 0)
        pdp_cnt = to_int(row.get("PDP"), 0)

        for _ in range(l_cnt):
            L[sem][sec].append({"subject": subject, "faculty": faculty})

        for _ in range(t_cnt):
            T[sem][sec].append({"subject": subject, "faculty": faculty})

        for _ in range(p_cnt):
            P[sem][sec].append({"subject": subject, "faculty": faculty})

        for _ in range(coe_cnt):
            COE[sem][sec].append({"subject": subject, "faculty": faculty})

        for _ in range(pdp_cnt):
            PDP[sem][sec].append({"subject": subject, "faculty": faculty})

        section_map[sem][sec].append(row)

    return L, T, P, PDP, COE, section_map


# ======================================================================
#  PART 4 – ROOMS
# ======================================================================

def build_room_map(room_list):
    """
    Build:
        lecture_room[(sem,sec)] → fixed lecture room
        lab_rooms_normal        → Lab rooms except B-201/B-202
        any_rooms               → non-lab rooms
    B-201 and B-202 are reserved only for COE (sem 5 & sem 3).
    """
    lecture_room = {}
    lab_rooms_normal = []
    any_rooms = []

    for r in room_list:
        room_no = str(r.get("Room_No", "")).strip()
        rtype = str(r.get("Room_Type", "")).strip()

        if rtype == "Lab":
            if room_no not in ("B-201", "B-202"):
                lab_rooms_normal.append(room_no)
        else:
            any_rooms.append(room_no)

        if "Assigned_Semester" in r and "Assigned_Section" in r:
            sem = to_int(r.get("Assigned_Semester"), 0)
            sec = str(r.get("Assigned_Section", "")).strip()
            if sem and sec:
                lecture_room[(sem, sec)] = room_no

    return lecture_room, lab_rooms_normal, any_rooms


# ======================================================================
#  PART 5 – STATE STRUCTURES
# ======================================================================

def initialize_state():
    faculty_busy = {}      # (faculty, day, slot) → True
    section_busy = {}      # (sem, sec, day, slot) → True
    group_busy = {}        # (sem, group, day, slot) → True

    subject_daily_used = defaultdict(lambda: defaultdict(set))
    special_daily_used = defaultdict(lambda: defaultdict(str))

    timetable = []
    return faculty_busy, section_busy, group_busy, subject_daily_used, special_daily_used, timetable


def is_free(
    sem, sec, faculty, day, slots,
    faculty_busy, section_busy, group_busy,
    groups=None
):
    groups = groups or []

    for slot in slots:
        if faculty_busy.get((faculty, day, slot)):
            return False
        if section_busy.get((sem, sec, day, slot)):
            return False
        for g in groups:
            if group_busy.get((sem, g, day, slot)):
                return False
    return True


def mark_slots(
    sem, sec, faculty, day, slots,
    faculty_busy, section_busy, group_busy,
    groups=None
):
    groups = groups or []

    for slot in slots:
        faculty_busy[(faculty, day, slot)] = True
        section_busy[(sem, sec, day, slot)] = True
        for g in groups:
            group_busy[(sem, g, day, slot)] = True


# ======================================================================
#  PART 6 – FIXED PROJECT1 LABS (SEM 7, A/B/C)
# ======================================================================

def extract_sem7_project1_labs(P):
    """
    Take only subjects whose name contains "project1" (case-insensitive)
    from Semester 7, Sections A/B/C.
    Remove them from P so they are not scheduled again.
    """
    project_labs = defaultdict(lambda: defaultdict(list))
    sem = PROJECT1_FIXED_SEM

    if sem not in P:
        return project_labs

    for sec in list(P[sem].keys()):
        items = P[sem][sec]
        new_items = []
        for item in items:
            subj_l = item["subject"].lower()
            if sec in PROJECT1_FIXED_SECTIONS and "project1" in subj_l:
                project_labs[sem][sec].append(item)
            else:
                new_items.append(item)
        P[sem][sec] = new_items

    return project_labs


def place_fixed_project_from_p_or_coe(
    P, COE, any_rooms,
    faculty_busy, section_busy, group_busy,
    subject_daily_used, special_daily_used,
    timetable
):
    """
    FINAL HARD FIX:
    Sem 7 → Project1 Lab
    Sem 8 → Project2 Lab
    Sections → A, B, C ONLY
    Days → Wednesday, Thursday, Friday
    Time → 11:00–12:00 & 12:00–13:00 (2 hours)
    Force = True (koi condition check nahi)
    """

    for sem, config in FIXED_PROJECT_CONFIG.items():
        keyword = config["keyword"].lower()
        fixed_sections = config["Sections"]
        days = config["Days"]
        s1, s2 = config["Slots"]

        for sec in fixed_sections:

            p_items = P.get(sem, {}).get(sec, [])
            c_items = COE.get(sem, {}).get(sec, [])

            matches = []

            for item in p_items:
                if keyword in item["subject"].lower():
                    matches.append(item)

            for item in c_items:
                if keyword in item["subject"].lower():
                    matches.append(item)

            if not matches:
                matches = [{
                    "subject": f"{config['keyword']} Lab",
                    "faculty": "Project Guide"
                }]

            for i, day in enumerate(days):
                item = matches[i % len(matches)]
                subject = item["subject"]
                faculty = item["faculty"]

                room = random.choice(any_rooms) if any_rooms else None

                timetable.append({
                    "Semester": sem,
                    "Section": sec,
                    "Day": day,
                    "Type": "P",
                    "Slot": s1,
                    "Slot2": s2,
                    "Subject": subject,
                    "Faculty": faculty,
                    "Room": room
                })

                faculty_key = f"{faculty}__{sec}"

                mark_slots(
                    sem, sec, faculty_key, day, [s1, s2],
                    faculty_busy, section_busy, group_busy
                )

                subject_daily_used[(sem, sec)][day].add(subject)
                special_daily_used[(sem, sec)][day] = "COE"

            P.setdefault(sem, {})
            COE.setdefault(sem, {})

            P[sem][sec] = [
                x for x in P[sem].get(sec, [])
                if keyword not in x["subject"].lower()
            ]

            COE[sem][sec] = [
                x for x in COE[sem].get(sec, [])
                if keyword not in x["subject"].lower()
            ]

# ======================================================================
#  PART 7 – LAB/TUTORIAL PAIRING
# ======================================================================

def build_pairs(items):
    """Return [(s1,s2), (s2,s1), ...]."""
    if len(items) < 2:
        return []

    pairs = []
    for i in range(0, len(items), 2):
        if i + 1 >= len(items):
            break
        a = items[i]
        b = items[i + 1]
        pairs.append((a, b))
        pairs.append((b, a))
    return pairs


# ======================================================================
#  PART 8 – 2-HOUR LAB (P)
# ======================================================================

def try_place_two_hour_lab(
    sem, sec,
    subj1, subj2,
    fac1, fac2,
    group1, group2,
    allowed_rooms,
    faculty_busy, section_busy, group_busy,
    subject_daily_used, special_daily_used,
    timetable
):
    slot_pairs = FIRST_HALF_2HR + SECOND_HALF_2HR

    for day in DAYS:

        if is_saturday_holiday(sem, day):
            continue

        if subj1 in subject_daily_used[(sem, sec)][day]:
            continue
        if subj2 in subject_daily_used[(sem, sec)][day]:
            continue

        for (s1, s2) in slot_pairs:

            if not can_place_without_gap(sem, sec, day, s1, section_busy):
                continue

            g1_list = [group1] if group1 else []
            g2_list = [group2] if group2 else []

            if not is_free(
                sem, sec, fac1, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
                g1_list,
            ):
                continue

            if not is_free(
                sem, sec, fac2, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
                g2_list,
            ):
                continue

            room1 = random.choice(allowed_rooms) if allowed_rooms else None
            room2 = random.choice(allowed_rooms) if allowed_rooms else None

            timetable.append({
                "Semester": sem,
                "Section": sec,
                "Day": day,
                "Type": "P",
                "Slot": s1,
                "Slot2": s2,
                "Subject": None,
                "Faculty": None,
                "Room": None,
                "Groups": [
                    {"group": group1, "subject": subj1, "faculty": fac1, "room": room1},
                    {"group": group2, "subject": subj2, "faculty": fac2, "room": room2},
                ],
            })

            mark_slots(
                sem, sec, fac1, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
                g1_list,
            )
            mark_slots(
                sem, sec, fac2, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
                g2_list,
            )

            subject_daily_used[(sem, sec)][day].add(subj1)
            subject_daily_used[(sem, sec)][day].add(subj2)

            return True

    return False


# ======================================================================
#  PART 9 – GENERIC 2-HOUR BLOCK (for non-fixed COE)
# ======================================================================

def try_place_two_hour(
    sem, sec,
    subj1, subj2,
    fac1, fac2,
    group1, group2,
    allowed_rooms,
    faculty_busy, section_busy, group_busy,
    subject_daily_used, special_daily_used,
    timetable,
    type_name="COE",
):
    slot_pairs = FIRST_HALF_2HR + SECOND_HALF_2HR

    for day in DAYS:

        if is_saturday_holiday(sem, day):
            continue

        if type_name == "COE" and special_daily_used[(sem, sec)][day] == "PDP":
            continue
        if type_name == "PDP" and special_daily_used[(sem, sec)][day] == "COE":
            continue

        if subj1 in subject_daily_used[(sem, sec)][day]:
            continue
        if subj2 in subject_daily_used[(sem, sec)][day]:
            continue

        for (s1, s2) in slot_pairs:

            if not can_place_without_gap(sem, sec, day, s1, section_busy):
                continue

            g1_list = [group1] if group1 else []
            g2_list = [group2] if group2 else []

            if not is_free(
                sem, sec, fac1, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
                g1_list,
            ):
                continue

            if not is_free(
                sem, sec, fac2, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
                g2_list,
            ):
                continue

            room1 = random.choice(allowed_rooms) if allowed_rooms else None
            room2 = random.choice(allowed_rooms) if allowed_rooms else None

            record = {
                "Semester": sem,
                "Section": sec,
                "Day": day,
                "Type": type_name,
                "Slot": s1,
                "Slot2": s2,
            }

            if type_name == "COE":
                record["Subject"] = subj1
                record["Faculty"] = fac1
                record["Room"] = room1
                record["Groups"] = []
            else:  # generic 2-hour block
                record["Subject"] = None
                record["Faculty"] = None
                record["Room"] = None
                record["Groups"] = [
                    {"group": group1, "subject": subj1, "faculty": fac1, "room": room1},
                    {"group": group2, "subject": subj2, "faculty": fac2, "room": room2},
                ]

            timetable.append(record)

            mark_slots(
                sem, sec, fac1, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
                g1_list,
            )
            mark_slots(
                sem, sec, fac2, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
                g2_list,
            )

            subject_daily_used[(sem, sec)][day].add(subj1)
            subject_daily_used[(sem, sec)][day].add(subj2)

            if type_name == "COE":
                special_daily_used[(sem, sec)][day] = "COE"

            return True

    return False


# ======================================================================
#  PART 10 – COE (SEM 3 → B-202, SEM 5 → B-201)
# ======================================================================

def coe_fixed_room_for_sem(sem):
    if sem == 3:
        return "B-202"
    if sem == 5:
        return "B-201"
    return None


def try_place_coe_block(
    sem, sec,
    subject, faculty,
    room,
    faculty_busy, section_busy, group_busy,
    subject_daily_used, special_daily_used,
    coe_room_busy,
    timetable
):
    slot_pairs = FIRST_HALF_2HR + SECOND_HALF_2HR

    for day in DAYS:

        if is_saturday_holiday(sem, day):
            continue

        # COE should not clash with PDP
        if special_daily_used[(sem, sec)][day] == "PDP":
            continue

        if subject in subject_daily_used[(sem, sec)][day]:
            continue

        for (s1, s2) in slot_pairs:

            if not can_place_without_gap(sem, sec, day, s1, section_busy):
                continue

            if not is_free(
                sem, sec, faculty, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
            ):
                continue

            # 🔥 IMPORTANT FIX: room clash ONLY if room exists
            if room:
                if coe_room_busy.get((room, day, s1)) or coe_room_busy.get((room, day, s2)):
                    continue

            timetable.append({
                "Semester": sem,
                "Section": sec,
                "Day": day,
                "Type": "COE",
                "Slot": s1,
                "Slot2": s2,
                "Subject": subject,
                "Faculty": faculty,
                "Room": room,
                "Groups": [],
            })

            mark_slots(
                sem, sec, faculty, day, [s1, s2],
                faculty_busy, section_busy, group_busy,
            )

            if room:
                coe_room_busy[(room, day, s1)] = True
                coe_room_busy[(room, day, s2)] = True

            subject_daily_used[(sem, sec)][day].add(subject)
            special_daily_used[(sem, sec)][day] = "COE"

            return True

    return False



# ======================================================================
#  PART 11 – SINGLE-HOUR CLASSES (L / PDP / GENERIC)
# ======================================================================

def try_place_single_hour(
    sem, sec,
    subject, faculty,
    type_name,
    allowed_rooms,
    faculty_busy, section_busy, group_busy,
    subject_daily_used, special_daily_used,
    timetable,
    force_slot=None,
):
    def commit(day, slot):
        room = random.choice(allowed_rooms) if allowed_rooms else None

        timetable.append({
            "Semester": sem,
            "Section": sec,
            "Day": day,
            "Type": type_name,
            "Slot": slot,
            "Subject": subject,
            "Faculty": faculty,
            "Room": room,
        })

        mark_slots(
            sem, sec, faculty, day, [slot],
            faculty_busy, section_busy, group_busy,
        )

        # Daily subject tracking (skip lectures)
        if type_name != "L":
            subject_daily_used[(sem, sec)][day].add(subject)

        # Special day marker
        if type_name in ("COE", "PDP"):
            special_daily_used[(sem, sec)][day] = type_name

        return True

    # --------------------------------------------------
    # FORCED SLOT MODE (used by 4th year logic)
    # --------------------------------------------------
    if force_slot is not None:
        for day in DAYS:

            if is_saturday_holiday(sem, day):
                continue

            # PDP is soft → no COE restriction
            if type_name != "PDP":
                if type_name == "PDP" and special_daily_used[(sem, sec)][day] == "COE":
                    continue

                if not can_place_without_gap(sem, sec, day, force_slot, section_busy):
                    continue

            if is_free(
                sem, sec, faculty, day, [force_slot],
                faculty_busy, section_busy, group_busy,
            ):
                return commit(day, force_slot)

        return False

    # --------------------------------------------------
    # NORMAL MODE
    # --------------------------------------------------
    for day in DAYS:

        if is_saturday_holiday(sem, day):
            continue

        for slot in ALL_SLOTS_ORDER:

            # PDP → NO gap rule, NO COE restriction
            if type_name != "PDP":
                if not can_place_without_gap(sem, sec, day, slot, section_busy):
                    continue

            if is_free(
                sem, sec, faculty, day, [slot],
                faculty_busy, section_busy, group_busy,
            ):
                return commit(day, slot)

    return False



# ======================================================================
#  PART 12 – MAIN GENERATION
# ======================================================================

def generate_timetable():
    random.seed(999)

    teaching_load, room_list = load_data()
    L, T, P, PDP, COE, section_map = group_by_sem_section(teaching_load)
    lecture_room, lab_rooms_normal, any_rooms = build_room_map(room_list)

    (
        faculty_busy,
        section_busy,
        group_busy,
        subject_daily_used,
        special_daily_used,
        timetable,
    ) = initialize_state()

    coe_room_busy = {}
    second_half_lecture_used = defaultdict(int)

    all_sem_sec = [(sem, sec) for sem in section_map for sec in section_map[sem]]

    # ==========================================================
    # 0) FIXED PROJECT LABS (SEM 7 / 8)
    # ==========================================================
    extract_sem7_project1_labs(P)
    place_fixed_project_from_p_or_coe(
        P, COE, any_rooms,
        faculty_busy, section_busy, group_busy,
        subject_daily_used, special_daily_used,
        timetable
    )

    # ==========================================================
    # 1) LABS (P)
    # ==========================================================
    for sem, sec in all_sem_sec:
        if not P[sem][sec]:
            continue

        g1, g2 = make_groups(sec)
        for s1, s2 in build_pairs(P[sem][sec]):
            if not try_place_two_hour_lab(
                sem, sec,
                s1["subject"], s2["subject"],
                s1["faculty"], s2["faculty"],
                g1, g2,
                lab_rooms_normal,
                faculty_busy, section_busy, group_busy,
                subject_daily_used, special_daily_used,
                timetable,
            ):
                raise Exception(f"LAB NOT PLACED ❌ Sem {sem} Sec {sec}")

    # ==========================================================
    # 2) COE (🔥 SEM 3 SEC J EXCEPTION ADDED)
    # ==========================================================
    for sem, sec in all_sem_sec:
        for item in COE[sem][sec]:

            # ✅ Fixed room ONLY for Sem 3 & 5 (NOT 4th year)
            room = coe_fixed_room_for_sem(sem)
            if sem in (7, 8):
                room = None

            ok = (
                try_place_coe_block(
                    sem, sec,
                    item["subject"], item["faculty"],
                    room,
                    faculty_busy, section_busy, group_busy,
                    subject_daily_used, special_daily_used,
                    coe_room_busy,
                    timetable,
                )
                if room
                else try_place_two_hour(
                    sem, sec,
                    item["subject"], item["subject"],
                    item["faculty"], item["faculty"],
                    None, None,
                    any_rooms,
                    faculty_busy, section_busy, group_busy,
                    subject_daily_used, special_daily_used,
                    timetable,
                    type_name="COE",
                )
            )

            # 🔥 ONLY ALLOWED FAILURE
            if not ok:
                if sem == 3 and sec == "J":
                    print("⚠️ COE skipped for Sem 3 Sec J (allowed)")
                    continue
                else:
                    raise Exception(f"COE NOT PLACED ❌ Sem {sem} Sec {sec}")

    # ==========================================================
    # 3) PDP
    # ==========================================================
    for sem, sec in all_sem_sec:
        for item in PDP[sem][sec]:
            if not try_place_single_hour(
                sem, sec,
                item["subject"], item["faculty"],
                "PDP",
                any_rooms,
                faculty_busy, section_busy, group_busy,
                subject_daily_used, special_daily_used,
                timetable,
            ):
                raise Exception(f"PDP NOT PLACED ❌ Sem {sem} Sec {sec}")

    # ==========================================================
    # 4) LECTURES (4th YEAR RULE INCLUDED)
    # ==========================================================
    for sem, sec in all_sem_sec:
        l_items = L[sem][sec]
        if not l_items:
            continue

        fixed_room = lecture_room.get((sem, sec))
        rooms_for_lecture = [fixed_room] if fixed_room else any_rooms

        for item in l_items:
            placed = False

            if sem in (7, 8):
                for day in DAYS:
                    if is_saturday_holiday(sem, day):
                        continue

                    required = [
                        "09:00-10:00",
                        "10:00-11:00",
                        "11:00-12:00",
                        "12:00-13:00",
                    ]

                    nine_to_one_full = all(
                        section_busy.get((sem, sec, day, s), False)
                        for s in required
                    )

                    # FIRST HALF
                    for slot in FIRST_HALF_1HR:
                        if is_free(
                            sem, sec, item["faculty"], day, [slot],
                            faculty_busy, section_busy, group_busy
                        ):
                            try_place_single_hour(
                                sem, sec,
                                item["subject"], item["faculty"],
                                "L",
                                rooms_for_lecture,
                                faculty_busy, section_busy, group_busy,
                                subject_daily_used, special_daily_used,
                                timetable,
                                force_slot=slot,
                            )
                            placed = True
                            break

                    if placed:
                        break

                    # SECOND HALF (max 2/week & only if 9–1 full)
                    if nine_to_one_full and second_half_lecture_used[(sem, sec)] < 2:
                        for slot in SECOND_HALF_1HR:
                            if is_free(
                                sem, sec, item["faculty"], day, [slot],
                                faculty_busy, section_busy, group_busy
                            ):
                                try_place_single_hour(
                                    sem, sec,
                                    item["subject"], item["faculty"],
                                    "L",
                                    rooms_for_lecture,
                                    faculty_busy, section_busy, group_busy,
                                    subject_daily_used, special_daily_used,
                                    timetable,
                                    force_slot=slot,
                                )
                                second_half_lecture_used[(sem, sec)] += 1
                                placed = True
                                break

                    if placed:
                        break

            else:
                for day in DAYS:
                    if is_saturday_holiday(sem, day):
                        continue

                    for slot in ALL_SLOTS_ORDER:
                        if can_place_without_gap(sem, sec, day, slot, section_busy):
                            if is_free(
                                sem, sec, item["faculty"], day, [slot],
                                faculty_busy, section_busy, group_busy
                            ):
                                try_place_single_hour(
                                    sem, sec,
                                    item["subject"], item["faculty"],
                                    "L",
                                    rooms_for_lecture,
                                    faculty_busy, section_busy, group_busy,
                                    subject_daily_used, special_daily_used,
                                    timetable,
                                    force_slot=slot,
                                )
                                placed = True
                                break
                    if placed:
                        break

            if not placed:
                raise Exception(f"LECTURE NOT PLACED ❌ Sem {sem} Sec {sec}")

    # ==========================================================
    # SAVE
    # ==========================================================
    db["timetable"].delete_many({})
    db["timetable"].insert_many(timetable)

    return {"success": True, "count": len(timetable)}



