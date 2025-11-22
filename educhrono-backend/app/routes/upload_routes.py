from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import pandas as pd
import io
import os
from app import db
from app.models.schemas import FacultyLoad, TeachingLoad, Room, Lab
from app.utils.role_check import require_roles

router = APIRouter()

# Folder where your templates are stored
TEMPLATE_FOLDER = os.path.join(os.path.dirname(__file__), "..", "templates")
TEMPLATE_FOLDER = os.path.abspath(TEMPLATE_FOLDER)

@router.get("/template/faculty-load")
def get_faculty_template():
    file_path = os.path.join(TEMPLATE_FOLDER, "faculty-load_template.xlsx")
    print("📂 TEMPLATE_FOLDER =", TEMPLATE_FOLDER)
    print("📄 Looking for file at:", file_path)
    
    if not os.path.exists(file_path):
        return {"detail": f"Template file not found at {file_path}"}
    
    return FileResponse(
        file_path,
        filename="faculty-load_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/template/teaching-load")
def get_teaching_template():
    file_path = os.path.join(TEMPLATE_FOLDER, "teaching-load_template.xlsx")
    if not os.path.exists(file_path):
        return {"detail": "Template file not found"}
    return FileResponse(file_path, filename="teaching-load_template.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@router.get("/template/lab-list")
def get_lab_template():
    file_path = os.path.join(TEMPLATE_FOLDER, "lab-list_template.xlsx")
    if not os.path.exists(file_path):
        return {"detail": "Template file not found"}
    return FileResponse(file_path, filename="lab-list_template.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@router.get("/template/room-list")
def get_room_template():
    file_path = os.path.join(TEMPLATE_FOLDER, "room-list_template.xlsx")
    if not os.path.exists(file_path):
        return {"detail": "Template file not found"}
    return FileResponse(file_path, filename="room-list_template.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# ===========================
# 🔹 Helper: Read Excel and Map Columns
# ===========================
def read_excel_with_mapping(file_bytes, file_type):
    df = pd.read_excel(io.BytesIO(file_bytes))
    df.columns = df.columns.str.strip()

    # ✅ Mappings for each file type
    mappings = {
        "faculty-load": {
            "Faculty Name": "Faculty_Name",
            "Faculty Code": "Faculty_Code",
            "Department": "Department",
            "Subject Code": "Subject_Code",
            "Subject Name": "Subject_Name",
            "L": "L",
            "T": "T",
            "P": "P",
            "Total Hours": "Total_Hours"
        },
        "teaching-load": {
            "Subject Code": "Subject_Code",
            "Subject Name": "Subject_Name",
            "L": "L",
            "T": "T",
            "P": "P",
            "Semester": "Semester",
            "Department": "Department",
            "Faculty Code": "Faculty_Code",
            "Faculty Name": "Faculty_Name",
            "Section": "Section"
        },
        "room-list": {
            "Room No": "Room_No",
            "Room Type": "Room_Type",
            "Capacity": "Capacity",
            "Department": "Department",
            "Assigned_Semester": "Assigned_Semester",
            "Assigned_Section": "Assigned_Section"
        },
        "lab-list": {
            "Lab No": "Lab_No",
            "Lab Name": "Lab_Name",
            "Capacity": "Capacity",
            "Department": "Department"
        }
    }

    if file_type not in mappings:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file_type}")

    mapping = mappings[file_type]
    df = df.rename(columns=mapping)

    # ✅ Ensure all required columns exist
    required_columns = list(mapping.values())
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing column(s): {', '.join(missing)}")

    # ✅ Add Section column if missing (only for teaching-load)
    if file_type == "teaching-load" and "Section" not in df.columns:
        df["Section"] = "A"

    df = df.fillna("")
    return df.to_dict(orient="records")


# ===========================
# 🔹 UPLOAD ROUTES
# ===========================

@router.post("/faculty-load")
async def upload_faculty_load(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = read_excel_with_mapping(contents, "faculty-load")
        db["faculty_load"].delete_many({})
        db["faculty_load"].insert_many(data)
        return {"success": True, "message": f"✅ Uploaded {len(data)} faculty records successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/teaching-load")
async def upload_teaching_load(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = read_excel_with_mapping(contents, "teaching-load")
        db["teaching_load"].delete_many({})
        db["teaching_load"].insert_many(data)
        return {"success": True, "message": f"✅ Uploaded {len(data)} teaching records successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/room-list")
async def upload_room_list(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = read_excel_with_mapping(contents, "room-list")
        db["room_list"].delete_many({})
        db["room_list"].insert_many(data)
        return {"success": True, "message": f"✅ Uploaded {len(data)} rooms successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lab-list")
async def upload_lab_list(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        data = read_excel_with_mapping(contents, "lab-list")
        db["lab_list"].delete_many({})
        db["lab_list"].insert_many(data)
        return {"success": True, "message": f"✅ Uploaded {len(data)} labs successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===========================
# 🔹 VIEW ROUTES (Admin / HOD / Teacher)
# ===========================

@router.get("/faculty-load/view")
def view_faculty_load(user=Depends(require_roles(["admin", "hod", "teacher"]))):
    query = {}
    if user["role"] == "hod":
        query = {"Department": user.get("department")}
    elif user["role"] == "teacher":
        query = {"Faculty_Code": {"$regex": user["email"].split("@")[0], "$options": "i"}}

    records = list(db["faculty_load"].find(query, {"_id": 0}))
    if not records:
        raise HTTPException(status_code=404, detail="No Faculty Load found.")
    return {"count": len(records), "data": records}


@router.get("/teaching-load/view")
def view_teaching_load(user=Depends(require_roles(["admin", "hod"]))):
    query = {}
    if user["role"] == "hod":
        query = {"Department": user.get("department")}
    records = list(db["teaching_load"].find(query, {"_id": 0}))
    if not records:
        raise HTTPException(status_code=404, detail="No Teaching Load found.")
    return {"count": len(records), "data": records}


@router.get("/room-list/view")
def view_room_list(user=Depends(require_roles(["admin", "hod"]))):
    records = list(db["room_list"].find({}, {"_id": 0}))
    if not records:
        raise HTTPException(status_code=404, detail="No Room List found.")
    return {"count": len(records), "data": records}


@router.get("/lab-list/view")
def view_lab_list(user=Depends(require_roles(["admin", "hod"]))):
    records = list(db["lab_list"].find({}, {"_id": 0}))
    if not records:
        raise HTTPException(status_code=404, detail="No Lab List found.")
    return {"count": len(records), "data": records}


# ✅ Debug
print("✅ Upload routes loaded: /upload/faculty-load, /upload/teaching-load, /upload/room-list, /upload/lab-list")
