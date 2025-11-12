from pydantic import BaseModel, Field
from typing import Optional


# ===============================================
# 🧑‍🏫 Faculty Load Schema (faculty-load_template.xlsx)
# ===============================================
class FacultyLoad(BaseModel):
    Faculty_Name: str = Field(..., alias="Faculty Name")
    Faculty_Code: str = Field(..., alias="Faculty Code")
    Department: str
    Subject_Code: str = Field(..., alias="Subject Code")
    Subject_Name: str = Field(..., alias="Subject Name")
    L: int
    T: int
    P: int
    Total_Hours: int = Field(..., alias="Total Hours")

    class Config:
        populate_by_name = True  # Allows using both alias and field names


# ===============================================
# 📚 Teaching Load Schema (teaching-load_template.xlsx)
# ===============================================
class TeachingLoad(BaseModel):
    Subject_Code: str = Field(..., alias="Subject Code")
    Subject_Name: str = Field(..., alias="Subject Name")
    L: int
    T: int
    P: int
    Semester: int
    Department: str
    Faculty_Code: str = Field(..., alias="Faculty Code")
    Faculty_Name: str = Field(..., alias="Faculty Name")

    class Config:
        populate_by_name = True


# ===============================================
# 🏫 Room Schema (room-list_template.xlsx)
# ===============================================
class Room(BaseModel):
    Room_No: str = Field(..., alias="Room No")
    Room_Type: str = Field(..., alias="Room Type")
    Capacity: int
    Department: str

    class Config:
        populate_by_name = True


# ===============================================
# 🔬 Lab Schema (lab-list_template.xlsx)
# ===============================================
class Lab(BaseModel):
    Lab_No: str = Field(..., alias="Lab No")
    Lab_Name: str = Field(..., alias="Lab Name")
    Capacity: int
    Department: str

    class Config:
        populate_by_name = True
