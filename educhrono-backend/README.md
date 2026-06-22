# ⚙️ EduChrono Backend

This is the FastAPI-based backend for the **EduChrono** Timetable Management System.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Virtual Environment (recommended)

### Installation
1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.
You can view the interactive documentation at `http://127.0.0.1:8000/docs`.

## 🛠️ Tech Stack
- **FastAPI**: Web framework
- **Google OR-Tools**: Optimization for timetable generation
- **Pandas & OpenPyXL**: Data processing for Excel templates
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server
- **Python-Docx**: Document generation

## 📂 Folder Structure
- `app/main.py`: Entry point of the application.
- `app/routes/`: API endpoint definitions (Auth, Upload, Timetable).
- `app/models/`: Pydantic schemas and data models.
- `app/services/`: Core business logic (Timetable generation algorithms).
- `app/utils/`: Utility functions (File handling, logging, etc.).

## 🔌 API Endpoints
- `/auth`: Handles user registration and login.
- `/upload`: Endpoints for uploading load and room templates.
- `/timetable`: Endpoints for generating and retrieving timetables.
