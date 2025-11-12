from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload_routes, timetable_routes, auth_routes

app = FastAPI(title="EduChrono Backend", version="0.1.0")

origins = [
    "http://localhost",
    "http://localhost:5173",  # React frontend
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routes
app.include_router(upload_routes.router, prefix="/upload", tags=["Uploads"])
app.include_router(timetable_routes.router, prefix="/timetable", tags=["Timetable"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])

@app.get("/")
def home():
    return {"message": "EduChrono API Running 🚀"}
