from fastapi import APIRouter, HTTPException
from app.services.timetable_service import generate_timetable as generate_timetable_service
from app import db

# Create router instance
router = APIRouter()

# ✅ 1. Route to trigger timetable generation
@router.post("/generate")
async def generate_timetable_api():
    try:
        result = generate_timetable_service()
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("status", "Error generating timetable"))
        return {
            "message": "✅ Timetable generated successfully.",
            "total_entries": result.get("count", 0),
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ✅ 2. View all generated timetable entries
@router.get("/list")
async def list_generated_timetable():
    """
    Returns all generated timetable entries.
    """
    data = list(db["timetable"].find({}, {"_id": 0}))
    if not data:
        raise HTTPException(status_code=404, detail="No timetable found.")
    return {"success": True, "count": len(data), "data": data}


# ✅ Student Timetable API
@router.get("/student/{semester}/{section}")
def get_student_timetable(semester: int, section: str):
    # Fetch both section-specific classes and common COE/PDP classes for 3–6 semester students
    query = {
        "$or": [
            {"year": semester, "section": section},  # normal timetable
            {"year": semester, "type": {"$in": ["coe", "pdp"]}}  # include COE & PDP
        ]
    }

    data = list(db["timetable"].find(query, {"_id": 0}))

    return {
        "success": True,
        "semester": semester,
        "section": section,
        "data": data
    }


# ✅ 4. Faculty timetable
@router.get("/faculty/{faculty_name}")
def get_faculty_timetable(faculty_name: str):
    data = list(db["timetable"].find({"faculty": faculty_name}, {"_id": 0}))
    return {"faculty": faculty_name, "timetable": data}


# ============================================
# 📄 Download Timetable PDF (role-based)
# ============================================
@router.get("/download/{role}/{identifier}")
def download_timetable(role: str, identifier: str):
    """
    role = admin | hod | faculty | student
    identifier:
        - admin → "all"
        - hod → department name
        - faculty → faculty name
        - student → "semester-section" (e.g., "3-A")
    """
    query = {}
    filename = "timetable.pdf"

    if role == "admin":
        data = list(db["timetable"].find({}, {"_id": 0}))
        filename = "Full_Timetable.pdf"

    elif role == "hod":
        query = {"department": identifier}
        data = list(db["timetable"].find(query, {"_id": 0}))
        filename = f"HOD_{identifier}_Timetable.pdf"

    elif role == "faculty":
        query = {"faculty": identifier}
        data = list(db["timetable"].find(query, {"_id": 0}))
        filename = f"Faculty_{identifier.replace(' ', '_')}.pdf"

    elif role == "student":
        sem, section = identifier.split("-")
        query = {"year": int(sem), "section": section}
        data = list(db["timetable"].find(query, {"_id": 0}))
        filename = f"Student_Sem{sem}_Sec{section}.pdf"
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    if not data:
        raise HTTPException(status_code=404, detail="No timetable found for given filters")

    # Group data by Day and Slot
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    slots = ["9:00–10:00", "10:00–11:00", "11:00–12:00", "12:00–1:00", "2:00–3:00", "3:00–4:00"]

    grid = {day: {slot: "" for slot in slots} for day in days}
    for entry in data:
        day = entry["day"]
        slot = entry["time_slot"]
        subject = entry["subject"]
        faculty = entry.get("faculty", "")
        room = entry.get("room", "")
        grid[day][slot] = f"{subject}\n{faculty}\n({room})"

    # Generate PDF
    pdf = FPDF("L", "mm", "A4")
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)

    # Header
    pdf.cell(0, 10, "SaanMaan Institute Timetable", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Generated on {datetime.now().strftime('%d-%b-%Y %I:%M %p')}", ln=True, align="C")

    # Title based on role
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"View: {role.title()} ({identifier})", ln=True, align="C")

    # Table Header
    pdf.set_font("Helvetica", "B", 10)
    col_width = 270 / len(slots)
    row_height = 10

    pdf.cell(25, row_height, "Day", border=1, align="C")
    for slot in slots:
        pdf.cell(col_width, row_height, slot, border=1, align="C")
    pdf.ln(row_height)

    # Table Rows
    pdf.set_font("Helvetica", "", 9)
    for day in days:
        pdf.cell(25, row_height * 3, day, border=1, align="C")
        for slot in slots:
            text = grid[day][slot]
            if text == "":
                text = "-"
            y_before = pdf.get_y()
            x_before = pdf.get_x()
            pdf.multi_cell(col_width, 5, text, border=1, align="C")
            pdf.set_xy(x_before + col_width, y_before)
        pdf.ln(row_height * 3)

    # Save PDF
    output_path = f"/tmp/{filename}"
    pdf.output(output_path)
    return FileResponse(output_path, filename=filename, media_type="application/pdf")
    
# ✅ Debug print to verify router loaded
print("✅ Timetable routes loaded successfully (generate/list/student/faculty).")
