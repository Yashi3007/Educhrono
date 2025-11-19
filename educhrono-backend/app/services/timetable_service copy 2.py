from datetime import datetime
import random
from app import db
from collections import defaultdict


def generate_timetable():
    try:
        db["timetable"].delete_many({})
        print("🧹 Cleared old timetable data")

        random.seed(42)
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        time_slots = [
            "9:00–10:00", "10:00–11:00", "11:00–12:00",
            "12:00–1:00", "2:00–3:00", "3:00–4:00"
        ]
        lunch_slot = "1:00–2:00"

        teaching_load = list(db["teaching_load"].find({}, {"_id": 0}))
        if not teaching_load:
            return {"success": False, "status": "No teaching load data"}

        room_list = list(db["room_list"].find({}, {"_id": 0}))
        lab_list = list(db["lab_list"].find({}, {"_id": 0}))
        lecture_rooms = [r["Room_No"] for r in room_list if "Room" in r.get("Room_Type", "")]
        lab_rooms = [l["Lab_No"] for l in lab_list]
        if not lecture_rooms:
            lecture_rooms = ["CSE-101", "CSE-102", "CSE-103"]
        if not lab_rooms:
            lab_rooms = ["CSE-LAB1", "CSE-LAB2", "CSE-LAB3"]

        timetable = []
        placed_counter = defaultdict(lambda: {"L": 0, "T": 0, "P": 0, "COE": 0, "PDP": 0})
        expected_counter = defaultdict(lambda: {"L": 0, "T": 0, "P": 0, "COE": 0, "PDP": 0})

        # ---------------- Helper Functions ----------------
        def parse_slots(slot):
            return slot.split('+') if '+' in slot else [slot]

        def is_conflict(faculty, section, day, slot, subject):
            new_slots = set(parse_slots(slot))
            for entry in timetable:
                if entry["day"] != day:
                    continue
                existing_slots = set(parse_slots(entry["time_slot"]))
                if new_slots & existing_slots:
                    if entry["faculty"] == faculty or entry["section"] == section:
                        return True
                if entry["subject"] == subject and entry["day"] == day:
                    return True
                if (
                    (entry["type"] == "PDP" and subject == "COMMUNICATION & ETHICS")
                    or (entry["type"] == "COE" and subject == "PROFESSIONAL DEVELOPMENT PROGRAM")
                ) and entry["day"] == day:
                    return True
            return False

        def choose_two_hour_block():
            pairs = [
                ("9:00–10:00", "10:00–11:00"),
                ("10:00–11:00", "11:00–12:00"),
                ("11:00–12:00", "12:00–1:00"),
                ("2:00–3:00", "3:00–4:00"),
            ]
            return random.choice(pairs)

        def available_day_slot(cls_type):
            if cls_type == "COE":
                return random.choice([
                    ("2:00–3:00", "3:00–4:00"),
                    ("11:00–12:00", "12:00–1:00")
                ])
            elif cls_type == "PDP":
                # Try single hours first, fallback later
                return random.choice([
                    ("9:00–10:00", "10:00–11:00"),
                    ("11:00–12:00", "12:00–1:00"),
                    ("2:00–3:00", "3:00–4:00")
                ])
            else:
                return choose_two_hour_block()

        grouped = {}
        for row in teaching_load:
            key = (row["Semester"], row["Section"].strip().upper())
            grouped.setdefault(key, []).append(row)

        # ---------------- Main Logic ----------------
        for (sem, section), subjects in grouped.items():
            print(f"\n🧾 Generating timetable for Sem {sem}, Section {section}")

            for subj_row in subjects:
                subj = subj_row["Subject_Name"].strip().upper()
                faculty = subj_row["Faculty_Name"]
                fcode = subj_row["Faculty_Code"]
                dept = subj_row["Department"]
                L, T, P, COE, PDP = (int(subj_row.get(k, 0)) for k in ["L", "T", "P", "COE", "PDP"])
                expected_counter[subj] = {"L": L, "T": T, "P": P, "COE": COE, "PDP": PDP}

                # ---------- General Class Placement ----------
                def place_class(cls_type, total_count):
                    for _ in range(total_count):
                        placed = False
                        for _ in range(600):
                            day = random.choice(days)
                            if cls_type in ["T", "P", "COE", "PDP"]:
                                s1, s2 = available_day_slot(cls_type)
                                slot = f"{s1}+{s2}"
                            else:
                                slot = random.choice(time_slots[:4])
                            if lunch_slot in parse_slots(slot):
                                continue
                            if is_conflict(faculty, section, day, slot, subj):
                                continue
                            room_choice = random.choice(
                                lab_rooms if cls_type in ["T", "P", "COE"] else lecture_rooms
                            )

                            # Regular placement
                            if cls_type in ["L", "COE"]:
                                timetable.append({
                                    "faculty": faculty, "faculty_code": fcode,
                                    "subject": subj, "department": dept,
                                    "room": room_choice, "day": day,
                                    "time_slot": slot, "year": sem,
                                    "section": section, "type": cls_type,
                                    "createdAt": datetime.utcnow(),
                                })
                            elif cls_type in ["T", "P"]:
                                # Group A1/A2 split with different faculty if possible
                                all_TP = [s for s in subjects if int(s.get(cls_type, 0)) > 0]
                                alt_subj_row = random.choice(
                                    [s for s in all_TP if s["Subject_Name"].strip().upper() != subj]
                                ) if len(all_TP) > 1 else subj_row
                                alt_subj = alt_subj_row["Subject_Name"].strip().upper()
                                alt_fac = alt_subj_row["Faculty_Name"]
                                alt_code = alt_subj_row["Faculty_Code"]

                                timetable.append({
                                    "faculty": faculty, "faculty_code": fcode,
                                    "subject": subj, "department": dept,
                                    "room": room_choice, "day": day,
                                    "time_slot": slot, "year": sem,
                                    "section": section, "batch": f"{section}-1",
                                    "type": cls_type, "createdAt": datetime.utcnow(),
                                })
                                timetable.append({
                                    "faculty": alt_fac, "faculty_code": alt_code,
                                    "subject": alt_subj, "department": dept,
                                    "room": room_choice, "day": day,
                                    "time_slot": slot, "year": sem,
                                    "section": section, "batch": f"{section}-2",
                                    "type": cls_type, "createdAt": datetime.utcnow(),
                                })
                            placed_counter[subj][cls_type] += 1
                            placed = True
                            break
                        if not placed:
                            print(f"⚠️ Could not place {cls_type} for {subj}")

                # ---------- PDP Special Placement ----------
                def place_pdp_class(total_count):
                    for _ in range(total_count):
                        placed = False
                        for _ in range(800):
                            day = random.choice(days)
                            # Try single-hour first
                            slot = random.choice(time_slots[:4])
                            if lunch_slot in parse_slots(slot):
                                continue
                            if is_conflict(faculty, section, day, slot, subj):
                                # try fallback 2-hour
                                s1, s2 = available_day_slot("PDP")
                                slot = f"{s1}+{s2}"
                                if is_conflict(faculty, section, day, slot, subj):
                                    continue
                            room_choice = random.choice(lecture_rooms)
                            timetable.append({
                                "faculty": faculty, "faculty_code": fcode,
                                "subject": subj, "department": dept,
                                "room": room_choice, "day": day,
                                "time_slot": slot, "year": sem,
                                "section": section, "type": "PDP",
                                "createdAt": datetime.utcnow(),
                            })
                            placed_counter[subj]["PDP"] += 1
                            placed = True
                            break
                        if not placed:
                            print(f"⚠️ Could not place PDP for {subj}")

                # ---------- Place Classes ----------
                place_class("L", L)
                place_class("T", T)
                place_class("P", P)
                place_class("COE", COE)
                place_pdp_class(PDP)

        # ---------------- Retry for Missing ----------------
        for attempt in range(1, 6):
            missing = []
            for subj, exp in expected_counter.items():
                for key in exp:
                    if placed_counter[subj][key] < exp[key]:
                        missing.append((subj, key, exp[key] - placed_counter[subj][key]))
            if not missing:
                break
            print(f"\n🔁 Retry Attempt {attempt}/5 for missing entries:")
            for subj, cls_type, remaining in missing:
                print(f"⏳ Retrying {cls_type} for {subj} ({remaining} left)")
                for _ in range(remaining):
                    for _ in range(400):
                        day = random.choice(days)
                        s1, s2 = available_day_slot(cls_type)
                        slot = f"{s1}+{s2}"
                        room_choice = random.choice(
                            lab_rooms if cls_type in ["T", "P", "COE"] else lecture_rooms
                        )
                        if is_conflict("AutoAssign", "A", day, slot, subj):
                            continue
                        timetable.append({
                            "faculty": "AutoAssign", "faculty_code": "AUTO",
                            "subject": subj, "department": "CSE", "room": room_choice,
                            "day": day, "time_slot": slot, "year": 3,
                            "section": "A", "type": cls_type, "createdAt": datetime.utcnow()
                        })
                        placed_counter[subj][cls_type] += 1
                        break

        # ---------------- Final Save ----------------
        unique = {
            (t["faculty"], t["subject"], t["section"], t["day"], t["time_slot"], t.get("batch", "")): t
            for t in timetable
        }
        timetable = list(unique.values())
        db["timetable"].insert_many(timetable)

        print(f"\n✅ Successfully generated {len(timetable)} entries.")
        print("\n📊 Subject-wise Comparison (Expected vs Placed):")
        print("------------------------------------------------------------")
        for subj, exp in expected_counter.items():
            placed = placed_counter[subj]
            print(f"{subj:<35} | "
                  f"L {placed['L']}/{exp['L']:<2} | "
                  f"T {placed['T']}/{exp['T']:<2} | "
                  f"P {placed['P']}/{exp['P']:<2} | "
                  f"COE {placed['COE']}/{exp['COE']:<2} | "
                  f"PDP {placed['PDP']}/{exp['PDP']:<2}")

        return {"success": True, "count": len(timetable)}

    except Exception as e:
        print(f"❌ Error generating timetable: {e}")
        return {"success": False, "status": str(e)}
