from datetime import datetime
import random
from app import db

def generate_timetable():
    try:
        db["timetable"].delete_many({})
        print("🧹 Cleared old timetable data")

        # ---------------------------------------------------------------
        # BASE CONFIGURATION
        # ---------------------------------------------------------------
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        time_slots = ["9:00–10:00", "10:00–11:00", "11:00–12:00",
                      "12:00–1:00", "2:00–3:00", "3:00–4:00"]
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

        # ---------------------------------------------------------------
        # HELPER FUNCTIONS
        # ---------------------------------------------------------------
        def parse_slots(slot):
            """Return list of individual hour slots even for combined ones like 10–11+11–12"""
            return slot.split('+') if '+' in slot else [slot]

        def is_conflict(faculty, section, day, slot):
            """Check if faculty or section already has something in overlapping slot"""
            new_slots = set(parse_slots(slot))
            for entry in timetable:
                if entry["day"] != day:
                    continue
                existing_slots = set(parse_slots(entry["time_slot"]))
                if new_slots & existing_slots:  # any overlap
                    if entry["faculty"] == faculty or entry["section"] == section:
                        return True
            return False

        def subject_exists_today(section, day, subject):
            """Avoid repeating same subject same day"""
            for entry in timetable:
                if (entry["section"] == section and
                        entry["day"] == day and
                        entry["subject"].upper() == subject.upper()):
                    return True
            return False

        def choose_two_hour_block():
            valid_pairs = [
                ("9:00–10:00", "10:00–11:00"),
                ("10:00–11:00", "11:00–12:00"),
                ("11:00–12:00", "12:00–1:00"),
                ("2:00–3:00", "3:00–4:00"),
            ]
            return random.choice(valid_pairs)

        # ---------------------------------------------------------------
        # GROUP BY SEMESTER + SECTION
        # ---------------------------------------------------------------
        grouped = {}
        for row in teaching_load:
            key = (row["Semester"], row["Section"].strip().upper())
            grouped.setdefault(key, []).append(row)

        # ---------------------------------------------------------------
        # GENERATE FOR EACH SECTION
        # ---------------------------------------------------------------
        for (sem, section), subjects in grouped.items():
            L_count = T_count = P_count = COE_count = PDP_count = 0
            print(f"\n🧾 Generating timetable for Semester {sem}, Section {section}")

            # ===============================================================
            # 📗 LECTURES (1 hour each)
            # ===============================================================
            for row in subjects:
                L = int(row.get("L", 0))
                if L <= 0:
                    continue

                subj = row["Subject_Name"].strip().upper()
                faculty = row["Faculty_Name"]
                fcode = row["Faculty_Code"]
                dept = row["Department"]

                for _ in range(L):
                    for _ in range(100):
                        day = random.choice(days)
                        slot = random.choice(time_slots[:4])  # prefer morning
                        if slot == lunch_slot:
                            continue
                        if subject_exists_today(section, day, subj):
                            continue
                        if is_conflict(faculty, section, day, slot):
                            continue

                        timetable.append({
                            "faculty": faculty,
                            "faculty_code": fcode,
                            "subject": subj,
                            "department": dept,
                            "room": random.choice(lecture_rooms),
                            "day": day,
                            "time_slot": slot,
                            "year": sem,
                            "section": section,
                            "type": "L",
                            "createdAt": datetime.utcnow(),
                        })
                        L_count += 1
                        break

            # ===============================================================
            # 📘 TUTORIALS (2-hour block, split A1/A2)
            # ===============================================================
            tutorial_subjects = [r for r in subjects if int(r.get("T", 0)) > 0]
            for row in tutorial_subjects:
                subj = row["Subject_Name"].strip().upper()
                faculty = row["Faculty_Name"]
                fcode = row["Faculty_Code"]
                dept = row["Department"]
                alternate = random.choice(
                    [f for f in subjects if f["Faculty_Code"] != fcode]
                ) if len(subjects) > 1 else row

                for _ in range(int(row.get("T", 1))):
                    for _ in range(100):
                        day = random.choice(days)
                        s1, s2 = choose_two_hour_block()
                        if lunch_slot in [s1, s2]:
                            continue
                        if is_conflict(faculty, section, day, f"{s1}+{s2}"):
                            continue
                        timetable.extend([
                            {
                                "faculty": faculty,
                                "faculty_code": fcode,
                                "subject": subj,
                                "department": dept,
                                "room": random.choice(lecture_rooms),
                                "day": day,
                                "time_slot": f"{s1}+{s2}",
                                "year": sem,
                                "section": section,
                                "batch": f"{section}1",
                                "type": "T",
                                "createdAt": datetime.utcnow(),
                            },
                            {
                                "faculty": alternate["Faculty_Name"],
                                "faculty_code": alternate["Faculty_Code"],
                                "subject": alternate["Subject_Name"],
                                "department": alternate["Department"],
                                "room": random.choice(lecture_rooms),
                                "day": day,
                                "time_slot": f"{s1}+{s2}",
                                "year": sem,
                                "section": section,
                                "batch": f"{section}2",
                                "type": "T",
                                "createdAt": datetime.utcnow(),
                            },
                        ])
                        T_count += 1
                        break

            # ===============================================================
            # 🧪 PRACTICALS (Exclude COE & PDP)
            # ===============================================================
            practical_subjects = [
                r for r in subjects
                if int(r.get("P", 0)) > 0 and int(r.get("COE", 0)) == 0 and int(r.get("PDP", 0)) == 0
            ]
            for row in practical_subjects:
                subj = row["Subject_Name"].strip().upper()
                faculty = row["Faculty_Name"]
                fcode = row["Faculty_Code"]
                dept = row["Department"]
                alternate = random.choice(
                    [f for f in subjects if f["Faculty_Code"] != fcode]
                ) if len(subjects) > 1 else row

                for _ in range(int(row.get("P", 0))):
                    for _ in range(100):
                        day = random.choice(["Tuesday", "Wednesday", "Thursday", "Friday"])
                        s1, s2 = choose_two_hour_block()
                        if lunch_slot in [s1, s2]:
                            continue
                        if is_conflict(faculty, section, day, f"{s1}+{s2}"):
                            continue

                        timetable.extend([
                            {
                                "faculty": faculty,
                                "faculty_code": fcode,
                                "subject": subj,
                                "department": dept,
                                "room": random.choice(lab_rooms),
                                "day": day,
                                "time_slot": f"{s1}+{s2}",
                                "year": sem,
                                "section": section,
                                "batch": f"{section}1",
                                "type": "P",
                                "createdAt": datetime.utcnow(),
                            },
                            {
                                "faculty": alternate["Faculty_Name"],
                                "faculty_code": alternate["Faculty_Code"],
                                "subject": alternate["Subject_Name"],
                                "department": alternate["Department"],
                                "room": random.choice(lab_rooms),
                                "day": day,
                                "time_slot": f"{s1}+{s2}",
                                "year": sem,
                                "section": section,
                                "batch": f"{section}2",
                                "type": "P",
                                "createdAt": datetime.utcnow(),
                            },
                        ])
                        P_count += 1
                        break

            # ===============================================================
            # 🎓 COE (each 2-hr session)
            # ===============================================================
            coe_subjects = [r for r in subjects if int(r.get("COE", 0)) > 0]
            for row in coe_subjects:
                subj = row["Subject_Name"].strip().upper()
                faculty = row["Faculty_Name"]
                fcode = row["Faculty_Code"]
                dept = row["Department"]
                count = int(row.get("COE", 0))

                for _ in range(count):
                    for _ in range(100):
                        day = random.choice(days)
                        s1, s2 = choose_two_hour_block()
                        if is_conflict(faculty, section, day, f"{s1}+{s2}"):
                            continue
                        timetable.append({
                            "faculty": faculty,
                            "faculty_code": fcode,
                            "subject": subj,
                            "department": dept,
                            "room": random.choice(lab_rooms),
                            "day": day,
                            "time_slot": f"{s1}+{s2}",
                            "year": sem,
                            "section": section,
                            "type": "COE",
                            "createdAt": datetime.utcnow(),
                        })
                        COE_count += 1
                        break

            # ===============================================================
            # 🧠 PDP (each 1 hr session)
            # ===============================================================
            pdp_subjects = [r for r in subjects if int(r.get("PDP", 0)) > 0]
            for row in pdp_subjects:
                subj = row["Subject_Name"].strip().upper()
                faculty = row["Faculty_Name"]
                fcode = row["Faculty_Code"]
                dept = row["Department"]
                count = int(row.get("PDP", 0))

                for _ in range(count):
                    for _ in range(100):
                        day = random.choice(days)
                        slot = random.choice(time_slots[:4])
                        if slot == lunch_slot or is_conflict(faculty, section, day, slot):
                            continue
                        timetable.append({
                            "faculty": faculty,
                            "faculty_code": fcode,
                            "subject": subj,
                            "department": dept,
                            "room": random.choice(lecture_rooms),
                            "day": day,
                            "time_slot": slot,
                            "year": sem,
                            "section": section,
                            "type": "PDP",
                            "createdAt": datetime.utcnow(),
                        })
                        PDP_count += 1
                        break

            print(f"📊 Summary Sem {sem} {section}: "
                  f"L={L_count}, T={T_count}, P={P_count}, COE={COE_count}, PDP={PDP_count}")

        # ---------------------------------------------------------------
        # SAVE TO DB (deduplicated)
        # ---------------------------------------------------------------
        unique = {(t["faculty"], t["subject"], t["section"], t["day"], t["time_slot"]): t
                  for t in timetable}
        timetable = list(unique.values())

        db["timetable"].insert_many(timetable)
        print(f"✅ Successfully generated {len(timetable)} entries.")
        return {"success": True, "count": len(timetable)}

    except Exception as e:
        print(f"❌ Error generating timetable: {e}")
        return {"success": False, "status": str(e)}
