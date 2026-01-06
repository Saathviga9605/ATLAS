#!/usr/bin/env python
"""
Startup script for Autonomous Compliance AI for Visa
"""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_integrated:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
