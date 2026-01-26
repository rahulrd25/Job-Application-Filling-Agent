import sys
import os

# Add the current directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from app.main import app

# This is required for Vercel to find the app instance
handler = app
