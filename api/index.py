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

# Vercel expects a handler function
from fastapi import Request
from fastapi.responses import JSONResponse
import json

async def handler(request: Request):
    """Handle incoming requests"""
    # Route to FastAPI app
    from mangum import Mangum
    
    # Create Mangum handler
    handler = Mangum(app, lifespan="off")
    
    # Process the request
    response = await handler(request.scope, request.receive, request.send)
    return response

# For Vercel, we need to export the app directly
# Vercel will use the app object
from mangum import Mangum
lambda_handler = Mangum(app, lifespan="off")