from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app import db
from app.services.timetable_service import generate_timetable
from fpdf import FPDF
from datetime import datetime

router = APIRouter()

# ====================================================================================
# ✅ 1. GENERATE TIMETABLE ROUTE (Saves into DB)
# ====================================================================================
@router.post("/generate")
async def generate_timetable_api():
    try:
        result = generate_timetable()

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("message"))

        return {
            "success": True,
            "message": "✅ Timetable generated successfully",
            "total_entries": result.get("count", 0)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================================================================
# ✅ 2. FETCH COMPLETE TIMETABLE
# ====================================================================================
@router.get("/list")
async def fetch_timetable():
    try:
        data = list(db["timetable"].find({}, {"_id": 0}))
        return {"success": True, "total": len(data), "timetable": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================================================================
# ✅ 3. CLEAR TIMETABLE COLLECTION
# ====================================================================================
@router.delete("/clear")
async def clear_timetable():
    try:
        db["timetable"].delete_many({})
        return {"success": True, "message": "Timetable cleared."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ====================================================================================
# ✅ 4. FACULTY TIMETABLE
# ====================================================================================
@router.get("/faculty/{faculty_name}")
def get_faculty_timetable(faculty_name: str):
    data = list(db["timetable"].find({"Faculty": faculty_name}, {"_id": 0}))
    return {
        "success": True,
        "faculty": faculty_name,
        "total": len(data),
        "timetable": data
    }


# ====================================================================================
# ✅ 5. STUDENT TIMETABLE
# ====================================================================================
@router.get("/student/{semester}/{section}")
def get_student_timetable(semester: int, section: str):

    query = {"Semester": semester, "Section": section}
    data = list(db["timetable"].find(query, {"_id": 0}))

    return {
        "success": True,
        "semester": semester,
        "section": section,
        "total": len(data),
        "timetable": data
    }


# ====================================================================================
# ✅ 6. DOWNLOAD PDF (Admin, HOD, Faculty, Student)
# ====================================================================================
@router.get("/download/{role}/{identifier}")
def download_timetable(role: str, identifier: str):

    filename = ""
    data = []

    # -------------------- ADMIN --------------------
    if role == "admin":
        data = list(db["timetable"].find({}, {"_id": 0}))
        filename = "Full_Timetable.pdf"

    # -------------------- HOD --------------------
    elif role == "hod":
        # Only if department field exists
        data = list(db["timetable"].find({"Department": identifier}, {"_id": 0}))
        filename = f"HOD_{identifier}.pdf"

    # -------------------- FACULTY --------------------
    elif role == "faculty":
        data = list(db["timetable"].find({"Faculty": identifier}, {"_id": 0}))
        filename = f"Faculty_{identifier.replace(' ', '_')}.pdf"

    # -------------------- STUDENT --------------------
    elif role == "student":
        sem, section = identifier.split("-")
        data = list(db["timetable"].find(
            {"Semester": int(sem), "Section": section}, {"_id": 0}
        ))
        filename = f"Student_Sem{sem}_Sec{section}.pdf"

    else:
        raise HTTPException(status_code=400, detail="Invalid role supplied")

    if not data:
        raise HTTPException(status_code=404, detail="No timetable found for given filters")

    # -------------------- Create Grid --------------------
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    slots = [
        "09:00-10:00",
        "10:00-11:00",
        "11:00-12:00",
        "12:00-13:00",
        "14:00-15:00",
        "15:00-16:00",
        "16:00-17:00"
    ]

    grid = {day: {slot: "" for slot in slots} for day in days}

    for entry in data:
        day = entry["Day"]
        slot = entry["Slot"]
        subject = entry["Subject"]
        faculty = entry["Faculty"]
        room = entry.get("Room", "")

        grid[day][slot] = f"{subject}\n{faculty}\n({room})"

    # -------------------- Generate PDF --------------------
    pdf = FPDF("L", "mm", "A4")
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 10, "EduChrono Timetable", ln=True, align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%d-%b-%Y %I:%M %p')}", ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"View: {role.title()} ({identifier})", ln=True, align="C")

    col_width = 260 / len(slots)
    row_height = 10

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(25, row_height, "Day", border=1, align="C")

    for slot in slots:
        pdf.cell(col_width, row_height, slot, border=1, align="C")

    pdf.ln(row_height)

    pdf.set_font("Helvetica", "", 9)
    for day in days:
        pdf.cell(25, row_height * 3, day, border=1, align="C")

        for slot in slots:
            text = grid[day][slot] or "-"
            x = pdf.get_x()
            y = pdf.get_y()

            pdf.multi_cell(col_width, 5, text, border=1, align="C")
            pdf.set_xy(x + col_width, y)

        pdf.ln(row_height * 3)

    path = f"/tmp/{filename}"
    pdf.output(path)

    return FileResponse(path, filename=filename, media_type="application/pdf")
