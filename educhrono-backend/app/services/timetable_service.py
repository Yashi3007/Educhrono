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
            "12:00–1:00", "2:00–3:00", "3:00–4:00", "4:00–5:00"
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
            lab_rooms = ["CSE-LAB1", "CSE-LAB2", "CSE-LAB3", "CSE-LAB4"]

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
                # Prevent overlap with same faculty or section
                if new_slots & existing_slots:
                    if entry["faculty"] == faculty or entry["section"] == section:
                        return True
                # Prevent same subject duplication on same day
                if entry["subject"] == subject and entry["day"] == day:
                    return True
            return False

        def choose_two_hour_block():
            pairs = [
                ("9:00–10:00", "10:00–11:00"),
                ("10:00–11:00", "11:00–12:00"),
                ("11:00–12:00", "12:00–1:00"),
                ("2:00–3:00", "3:00–4:00"),
                ("3:00–4:00", "4:00–5:00"),
            ]
            return random.choice(pairs)

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

                # ---------- Class Placement ----------
                def place_class(cls_type, total_count):
                    for _ in range(total_count):
                        placed = False
                        for _ in range(800):
                            day = random.choice(days)
                            # ⏱ Duration rules
                            if cls_type in ["P", "COE"]:
                                s1, s2 = choose_two_hour_block()
                                slot = f"{s1}+{s2}"
                            else:
                                slot = random.choice(time_slots)

                            if lunch_slot in parse_slots(slot):
                                continue
                            if is_conflict(faculty, section, day, slot, subj):
                                continue

                            # 🏫 Room assignment based on type
                            if cls_type in ["L", "T", "PDP"]:
                                room_source = lecture_rooms
                            else:  # P, COE
                                room_source = lab_rooms

                            # 🧩 Batch-wise handling
                            if cls_type in ["T", "P"]:
                                # Select 2 different rooms for A1/A2
                                if len(room_source) >= 2:
                                    room_a1, room_a2 = random.sample(room_source, 2)
                                else:
                                    room_a1 = room_a2 = random.choice(room_source)

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
                                    "room": room_a1, "day": day,
                                    "time_slot": slot, "year": sem,
                                    "section": section, "batch": f"{section}-1",
                                    "type": cls_type, "createdAt": datetime.utcnow(),
                                })
                                timetable.append({
                                    "faculty": alt_fac, "faculty_code": alt_code,
                                    "subject": alt_subj, "department": dept,
                                    "room": room_a2, "day": day,
                                    "time_slot": slot, "year": sem,
                                    "section": section, "batch": f"{section}-2",
                                    "type": cls_type, "createdAt": datetime.utcnow(),
                                })
                            else:
                                # Single group classes (L, COE, PDP)
                                room_choice = random.choice(room_source)
                                timetable.append({
                                    "faculty": faculty, "faculty_code": fcode,
                                    "subject": subj, "department": dept,
                                    "room": room_choice, "day": day,
                                    "time_slot": slot, "year": sem,
                                    "section": section, "type": cls_type,
                                    "createdAt": datetime.utcnow(),
                                })

                            placed_counter[subj][cls_type] += 1
                            placed = True
                            break
                        if not placed:
                            print(f"⚠️ Could not place {cls_type} for {subj}")

                # ---------- PDP Placement ----------
                def place_pdp_class(total_count):
                    placed_days = set()
                    attempts = 0
                    while len(placed_days) < total_count and attempts < 600:
                        attempts += 1
                        day = random.choice(days)
                        if day in placed_days:
                            continue
                        slot = random.choice(time_slots)
                        if lunch_slot in parse_slots(slot):
                            continue
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
                        placed_days.add(day)
                        placed_counter[subj]["PDP"] += 1
                    if len(placed_days) < total_count:
                        print(f"⚠️ Only placed {len(placed_days)} of {total_count} PDP classes for {subj}")

                # ---------- Place All ----------
                place_class("L", L)
                place_class("T", T)
                place_class("P", P)
                place_class("COE", COE)
                place_pdp_class(PDP)

        # ---------------- Save to DB ----------------
        unique = {
            (t["faculty"], t["subject"], t["section"], t["day"], t["time_slot"], t.get("batch", "")): t
            for t in timetable
        }
        timetable = list(unique.values())
        db["timetable"].insert_many(timetable)

        print(f"\n✅ Successfully generated {len(timetable)} entries.")
        print("\n📊 Subject-wise Comparison (Expected vs Placed):")
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
