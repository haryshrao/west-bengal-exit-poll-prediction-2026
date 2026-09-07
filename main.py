"""
Entry point for the Exit Poll Prediction System.
Run this file to start the local FastAPI server.

Usage:
    python main.py
"""

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  EXIT POLL PREDICTION SYSTEM")
    print("  Starting server at http://localhost:8000")
    print("=" * 60)
    uvicorn.run("app.app:app", host="127.0.0.1", port=8000, reload=True)
