from app import db
import random
from datetime import datetime


def generate_timetable():
    try:
        db["timetable"].delete_many({})
        print("🧹 Cleared old timetable")

        # ---------------------------------------------------------------
        #  BASE CONFIGURATION
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
            lab_rooms = ["CSE-LAB1", "CSE-LAB2", "CSE-LAB3", "CSE-LAB4"]

        timetable = []

        # ---------------------------------------------------------------
        #  HELPER FUNCTIONS
        # ---------------------------------------------------------------
        def is_conflict(faculty, section, day, slot):
            """Check teacher or section time conflict"""
            for entry in timetable:
                if entry["day"] == day and entry["time_slot"] == slot:
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

        def choose_day():
            """Weighted random days (avoid Saturday overflow)"""
            return random.choice(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Friday", "Saturday"]
            )

        def choose_two_hour_block():
            """Get consecutive 2-hour blocks"""
            valid_pairs = [
                ("9:00–10:00", "10:00–11:00"),
                ("10:00–11:00", "11:00–12:00"),
                ("11:00–12:00", "12:00–1:00"),
                ("2:00–3:00", "3:00–4:00"),
            ]
            return random.choice(valid_pairs)

        # ---------------------------------------------------------------
        #  GROUP BY SECTION & SEMESTER
        # ---------------------------------------------------------------
        grouped = {}
        for row in teaching_load:
            key = (row["Semester"], row["Section"].strip().upper())
            grouped.setdefault(key, []).append(row)

        # ---------------------------------------------------------------
        #  GENERATE FOR EACH SECTION
        # ---------------------------------------------------------------
        for (sem, section), subjects in grouped.items():
            section_hours = 0
            print(f"\n🧾 Generating timetable for Semester {sem}, Section {section}")

            # ----------- LECTURES (L = 1 hr) -----------
            for row in subjects:
                L = int(row.get("L", 0))
                if L <= 0 or int(row.get("COE", 0)) > 0 or int(row.get("PDP", 0)) > 0:
                    continue
                subj = row["Subject_Name"].strip().upper()
                faculty = row["Faculty_Name"]
                fcode = row["Faculty_Code"]
                dept = row["Department"]

                for _ in range(L):
                    for _ in range(100):
                        day = choose_day()
                        slot = random.choice(time_slots[:4])  # Prefer before lunch
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
                        section_hours += 1
                        break

            # ----------- TUTORIALS (T = 2 hrs split) -----------
            tutorial_subjects = [r for r in subjects if int(r.get("T", 0)) > 0]
            for row in tutorial_subjects:
                subj = row["Subject_Name"].strip().upper()
                faculty = row["Faculty_Name"]
                fcode = row["Faculty_Code"]
                dept = row["Department"]
                alternate = random.choice(
                    [f for f in subjects if f["Faculty_Code"] != fcode]) if len(subjects) > 1 else row

                for _ in range(1):  # 1 tutorial per week
                    for _ in range(100):
                        day = choose_day()
                        s1, s2 = choose_two_hour_block()
                        if lunch_slot in [s1, s2] or is_conflict(faculty, section, day, s1):
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
                                "batch": f"{section}A1",
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
                                "batch": f"{section}A2",
                                "type": "T",
                                "createdAt": datetime.utcnow(),
                            }
                        ])
                        section_hours += 2
                        break

            # ----------- PRACTICALS (P = 2 hrs × 2 per week) -----------
            practical_subjects = [r for r in subjects if int(r.get("P", 0)) > 0]
            for row in practical_subjects:
                subj = row["Subject_Name"].strip().upper()
                faculty = row["Faculty_Name"]
                fcode = row["Faculty_Code"]
                dept = row["Department"]
                alternate = random.choice(
                    [f for f in subjects if f["Faculty_Code"] != fcode]) if len(subjects) > 1 else row

                for _ in range(2):  # 2 lab sessions per week
                    for _ in range(100):
                        day = random.choice(["Tuesday", "Wednesday", "Thursday", "Friday"])
                        s1, s2 = choose_two_hour_block()
                        if lunch_slot in [s1, s2]:
                            continue
                        if is_conflict(faculty, section, day, s1):
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
                                "batch": f"{section}A1",
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
                                "batch": f"{section}A2",
                                "type": "P",
                                "createdAt": datetime.utcnow(),
                            }
                        ])
                        section_hours += 2
                        break

            # ----------- COE (2 hrs) & PDP (1 hr) -----------
            coe_records = [r for r in subjects if int(r.get("COE", 0)) > 0]
            pdp_records = [r for r in subjects if int(r.get("PDP", 0)) > 0]
            used_days = set()

            # COE
            for row in coe_records:
                faculty = row["Faculty_Name"]
                subj = row["Subject_Name"].strip().upper()
                fcode = row["Faculty_Code"]
                dept = row["Department"]
                for _ in range(100):
                    day = random.choice(days)
                    if day in used_days:
                        continue
                    s1, s2 = choose_two_hour_block()
                    if is_conflict(faculty, section, day, s1):
                        continue
                    timetable.append({
                        "faculty": faculty,
                        "faculty_code": fcode,
                        "subject": subj,
                        "department": dept,
                        "room": random.choice(lecture_rooms),
                        "day": day,
                        "time_slot": f"{s1}+{s2}",
                        "year": sem,
                        "section": section,
                        "type": "COE",
                        "createdAt": datetime.utcnow(),
                    })
                    used_days.add(day)
                    section_hours += 2
                    break

            # PDP
            for row in pdp_records:
                faculty = row["Faculty_Name"]
                subj = row["Subject_Name"].strip().upper()
                fcode = row["Faculty_Code"]
                dept = row["Department"]
                for _ in range(100):
                    day = random.choice([d for d in days if d not in used_days])
                    slot = random.choice(time_slots[:4])  # morning preferred
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
                        "type": "PDP",
                        "createdAt": datetime.utcnow(),
                    })
                    used_days.add(day)
                    section_hours += 1
                    break

            print(f"✅ Total hours scheduled for Sem {sem} {section}: {section_hours}")
            if section_hours > 36:
                print(f"⚠️ Section {section} exceeded 36 hours, trimming extra entries.")
                timetable = timetable[:-abs(section_hours - 36)]

        # ---------------------------------------------------------------
        #  SAVE TO DATABASE
        # ---------------------------------------------------------------
        unique = {(t["faculty"], t["subject"], t["section"], t["day"], t["time_slot"]): t
                  for t in timetable}
        timetable = list(unique.values())

        db["timetable"].insert_many(timetable)
        print(f"✅ Successfully generated {len(timetable)} timetable entries.")
        return {"success": True, "count": len(timetable)}

    except Exception as e:
        print(f"❌ Error generating timetable: {e}")
        return {"success": False, "status": str(e)}


# def generate_timetable():
#     try:
#         db["timetable"].delete_many({})
#         print("🧹 Old timetable cleared")

#         # --- Day & Slot configuration
#         days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
#         first_half = ["9:00–10:00", "10:00–11:00", "11:00–12:00", "12:00–1:00"]
#         second_half = ["2:00–3:00", "3:00–4:00"]
#         lunch_slot = "1:00–2:00"

#         teaching_load = list(db["teaching_load"].find({}, {"_id": 0}))
#         room_list = list(db["room_list"].find({}, {"_id": 0}))
#         lab_list = list(db["lab_list"].find({}, {"_id": 0}))

#         if not teaching_load:
#             return {"success": False, "status": "No teaching load found"}

#         lecture_rooms = [r["Room_No"] for r in room_list if "Room" in r.get("Room_Type", "")]
#         lab_rooms = [l["Lab_No"] for l in lab_list]
#         if not lecture_rooms:
#             lecture_rooms = ["CSE-101", "CSE-102", "CSE-103"]
#         if not lab_rooms:
#             lab_rooms = ["CSE-LAB1", "CSE-LAB2", "CSE-LAB3", "CSE-LAB4"]

#         timetable = []

#         # --- COE / PDP detection
#         coe_records = [r for r in teaching_load if "COE" in r["Subject_Name"].upper()]
#         pdp_records = [r for r in teaching_load if "PDP" in r["Subject_Name"].upper()]

#         # --- Slot preference
#         def slot_priority(force_morning=True):
#             """Prefer first half unless explicitly random."""
#             available = first_half if force_morning else (first_half + second_half)
#             return random.choice(available)

#         # --- Conflict check
#         def is_conflict(faculty, section, day, slot):
#             return any(
#                 e["day"] == day and e["time_slot"] == slot and (
#                     e["faculty"] == faculty or e.get("section") == section
#                 )
#                 for e in timetable
#             )

#         def subject_exists_today(section, day, subject):
#             return any(
#                 e["section"] == section and e["day"] == day and e["subject"].upper() == subject.upper()
#                 for e in timetable
#             )

#         # --- Helper: pick valid day (no Monday/Saturday bias)
#         def choose_day(preferred_days=None):
#             if not preferred_days:
#                 preferred_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
#             # Ensure Monday/Saturday not always empty → slightly higher probability midweek
#             weighted_days = ["Monday"] + ["Tuesday", "Wednesday", "Thursday", "Friday"] * 2 + ["Saturday"]
#             return random.choice(weighted_days if preferred_days == days else preferred_days)

#         print("🧠 Generating timetable...")

#         # =====================================================================
#         # 📗 Regular LECTURES (Morning preference)
#         # =====================================================================
#         for row in teaching_load:
#             subj = row["Subject_Name"].strip().upper()
#             dept = row["Department"]
#             section = row["Section"].strip().upper()
#             sem = int(row["Semester"])
#             faculty = row.get("Faculty_Name", "")
#             fcode = row.get("Faculty_Code", "")
#             L, T, P = int(row["L"]), int(row["T"]), int(row["P"])

#             if "COE" in subj or "PDP" in subj:
#                 continue

#             for i in range(L):
#                 for _ in range(100):
#                     day = choose_day()
#                     slot = slot_priority(force_morning=True)
#                     if slot == lunch_slot:
#                         continue
#                     if subject_exists_today(section, day, subj):
#                         continue
#                     if is_conflict(faculty, section, day, slot):
#                         continue
#                     timetable.append({
#                         "faculty": faculty,
#                         "faculty_code": fcode,
#                         "subject": subj,
#                         "department": dept,
#                         "room": random.choice(lecture_rooms),
#                         "day": day,
#                         "time_slot": slot,
#                         "year": sem,
#                         "section": section,
#                         "type": "L",
#                         "createdAt": datetime.utcnow(),
#                     })
#                     break

#         # =====================================================================
#         # 📘 Tutorials (A1/A2 Different Faculty)
#         # =====================================================================
#         for row in teaching_load:
#             subj = row["Subject_Name"].strip().upper()
#             if "COE" in subj or "PDP" in subj:
#                 continue
#             section = row["Section"].strip().upper()
#             sem = int(row["Semester"])
#             faculty = row.get("Faculty_Name", "")
#             fcode = row.get("Faculty_Code", "")
#             dept = row["Department"]
#             T = int(row["T"])
#             if T <= 0:
#                 continue
#             alternate = random.choice([f for f in teaching_load if f["Faculty_Code"] != fcode])

#             for t in range(T):
#                 for _ in range(100):
#                     day = choose_day()
#                     slot = slot_priority()
#                     if slot == lunch_slot or is_conflict(faculty, section, day, slot):
#                         continue
#                     # A1 / A2
#                     timetable.append({
#                         "faculty": faculty,
#                         "faculty_code": fcode,
#                         "subject": subj,
#                         "department": dept,
#                         "room": random.choice(lecture_rooms),
#                         "day": day,
#                         "time_slot": slot,
#                         "year": sem,
#                         "section": section,
#                         "batch": f"{section}1",
#                         "type": "T",
#                         "createdAt": datetime.utcnow(),
#                     })
#                     timetable.append({
#                         "faculty": alternate["Faculty_Name"],
#                         "faculty_code": alternate["Faculty_Code"],
#                         "subject": alternate["Subject_Name"],
#                         "department": alternate["Department"],
#                         "room": random.choice(lecture_rooms),
#                         "day": day,
#                         "time_slot": slot,
#                         "year": sem,
#                         "section": section,
#                         "batch": f"{section}2",
#                         "type": "T",
#                         "createdAt": datetime.utcnow(),
#                     })
#                     break
#         # =====================================================================
#         # 🧪 Labs (A1/A2) - Final Fixed
#         # =====================================================================
#         for row in [r for r in teaching_load if int(r.get("P", 0)) > 0]:
#             subj = row["Subject_Name"].strip().upper()

#             # ✅ Skip COE / PDP by name or code pattern
#             if any(keyword in subj for keyword in ["COE", "COMMUNICATION", "ETHIC", "PDP", "DEVELOPMENT"]):
#                 continue

#             section = row["Section"].strip().upper()
#             sem = int(row["Semester"])
#             faculty = row["Faculty_Name"]
#             fcode = row["Faculty_Code"]
#             dept = row["Department"]
#             P = int(row["P"])

#             # ✅ Choose alternate faculty safely
#             alt_candidates = [f for f in teaching_load if f["Faculty_Code"] != fcode]
#             alternate = random.choice(alt_candidates) if alt_candidates else row

#             for _ in range(P):
#                 for _ in range(100):
#                     day = random.choice(["Tuesday", "Wednesday", "Thursday", "Friday"])

#                     # ✅ Expand slot choice to both halves
#                     if random.random() < 0.7:
#                         slots = ["9:00–10:00", "10:00–11:00", "11:00–12:00", "12:00–1:00"]
#                     else:
#                         slots = ["2:00–3:00", "3:00–4:00"]

#                     start_idx = random.choice(range(len(slots) - 1))
#                     s1, s2 = slots[start_idx], slots[start_idx + 1]

#                     # ✅ Conflict check only for faculty
#                     faculty_conflict = any(
#                         e["day"] == day and e["time_slot"] in [s1, s2] and e["faculty"] == faculty
#                         for e in timetable
#                     )
#                     if faculty_conflict:
#                         continue

#                     # ✅ A1 Lab Entry
#                     timetable.append({
#                         "faculty": faculty,
#                         "faculty_code": fcode,
#                         "subject": subj,
#                         "department": dept,
#                         "room": random.choice(lab_rooms),
#                         "day": day,
#                         "time_slot": f"{s1}+{s2}",
#                         "year": sem,
#                         "section": section,
#                         "batch": f"{section}1",
#                         "type": "P",
#                         "createdAt": datetime.utcnow(),
#                     })

#                     # ✅ A2 Lab Entry
#                     timetable.append({
#                         "faculty": alternate["Faculty_Name"],
#                         "faculty_code": alternate["Faculty_Code"],
#                         "subject": alternate["Subject_Name"],
#                         "department": alternate["Department"],
#                         "room": random.choice(lab_rooms),
#                         "day": day,
#                         "time_slot": f"{s1}+{s2}",
#                         "year": sem,
#                         "section": section,
#                         "batch": f"{section}2",
#                         "type": "P",
#                         "createdAt": datetime.utcnow(),
#                     })
#                     break

#         # ✅ Debug check
#         lab_entries = [t for t in timetable if t["type"] == "P" and t["year"] == 3 and t["section"] == "A"]
#         print(f"🧪 Labs generated for Sem 3 Section A: {len(lab_entries)}")


#         # =====================================================================
#         # 🎓 COE / PDP (Lecture-Only Proper Handling)
#         # =====================================================================
#         def schedule_special(subject_key, freq, exclude_days=set()):
#             subjects = [
#                 r for r in teaching_load
#                 if subject_key in r["Subject_Name"].upper()
#                 or subject_key in r.get("Subject_Code", "").upper()
#             ]
#             used_days = set()
#             for rec in subjects:
#                 L, T, P = int(rec.get("L", 0)), int(rec.get("T", 0)), int(rec.get("P", 0))
#                 if L <= 0 or T > 0 or P > 0:
#                     continue  # ✅ Only pure lecture subjects
#                 faculty, fcode, dept = rec["Faculty_Name"], rec["Faculty_Code"], rec["Department"]
#                 sem, section = int(rec["Semester"]), rec["Section"].strip().upper()
#                 for _ in range(freq):
#                     for _ in range(100):
#                         day = random.choice([d for d in days if d not in exclude_days and d not in used_days])
#                         slot = random.choice(first_half)
#                         if slot == lunch_slot or is_conflict(faculty, section, day, slot):
#                             continue
#                         timetable.append({
#                             "faculty": faculty,
#                             "faculty_code": fcode,
#                             "subject": rec["Subject_Name"].upper(),
#                             "department": dept,
#                             "room": random.choice(lecture_rooms),
#                             "day": day,
#                             "time_slot": slot,
#                             "year": sem,
#                             "section": section,
#                             "type": "L",
#                             "createdAt": datetime.utcnow(),
#                         })
#                         used_days.add(day)
#                         break
#             return used_days


#         # ✅ Use proper frequencies
#         used_days_for_coe = schedule_special("COE", freq=3)
#         used_days_for_pdp = schedule_special("PDP", freq=2, exclude_days=used_days_for_coe)

#         # =====================================================================
#         # 🧹 Remove Duplicates
#         # =====================================================================
#         unique = {(t["faculty"], t["subject"], t["section"], t["day"], t["time_slot"]): t for t in timetable}
#         timetable = list(unique.values())

#         db["timetable"].insert_many(timetable)
#         print(f"✅ Timetable generated successfully with {len(timetable)} entries.")
#         return {"success": True, "count": len(timetable)}
#     except Exception as e:
#         print(f"❌ Error generating timetable: {e}")
#         return {"success": False, "status": str(e)}
