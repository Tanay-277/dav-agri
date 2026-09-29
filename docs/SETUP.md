# DAV — Local Setup & Development Guide

Follow these steps to run the DAV platform locally on your machine.

---

## 1. Prerequisites
* **Node.js:** v18+ (Verified on v24.18.0)
* **Python:** 3.10+ (Verified on Python 3.13.7)
* **npm:** v9+ (Verified on npm 11.16.0)

---

## 2. Backend Setup & Startup

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd C:\Users\harsh\.gemini\antigravity\scratch\dav\backend
   ```
2. Install Python dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Initialize the database and seed initial demo data:
   ```bash
   python app/database/init_db.py
   ```
4. Start the FastAPI ASGI server:
   ```bash
   # Option A (Standard uvicorn command with hot-reload):
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

   # Option B (Direct python execution):
   python main.py
   ```
   The backend server will start at `http://127.0.0.1:8000`.
   * Root API Health: `http://127.0.0.1:8000/`
   * Interactive Swagger UI: `http://127.0.0.1:8000/docs` (or `http://127.0.0.1:8000/api/v1/docs`)

---

## 3. Frontend Setup & Startup

1. Open a second terminal and navigate to the frontend directory:
   ```bash
   cd C:\Users\harsh\.gemini\antigravity\scratch\dav\frontend
   ```
2. Install dependencies:
   ```bash
   npm.cmd install
   ```
3. Start the Vite development server:
   ```bash
   npm.cmd run dev
   ```
   Open `http://localhost:5173` in your browser.

---

## 4. Running the Automated Test Suite

To run the complete automated test suite on the backend:
```bash
cd C:\Users\harsh\.gemini\antigravity\scratch\dav\backend
python -m pytest tests/ -v
```

To run frontend type checking and production build:
```bash
cd C:\Users\harsh\.gemini\antigravity\scratch\dav\frontend
npm.cmd run build
```
