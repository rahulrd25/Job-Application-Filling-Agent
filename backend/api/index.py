import sys
import os

# Add the current directory to sys.path so we can import 'app'
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
    from app.main import app
except Exception as e:
    print(f"CRITICAL IMPORT ERROR: {str(e)}")
    # Create a dummy app to prevent 500 crash and show error
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/{catchall:path}")
    def error_handler(catchall: str):
        return {"error": "Import Failed", "detail": str(e)}

# This is required for Vercel to find the app instance
handler = app
