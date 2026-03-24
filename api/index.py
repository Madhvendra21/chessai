"""
Vercel Serverless Function Entry Point
Routes API requests to the appropriate backend handlers
"""
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import and run the FastAPI app
from backend.api.index import app

# Vercel handler using Mangum
from mangum import Mangum

handler = Mangum(app, lifespan="off")