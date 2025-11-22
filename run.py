#!/usr/bin/env python
"""
Quick run script for the Streamlit app
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the Streamlit application"""
    app_path = Path(__file__).parent / "app" / "main.py"
    
    if not app_path.exists():
        print(f"Error: {app_path} not found!")
        sys.exit(1)
    
    print("🚀 Starting Banking Product Analyzer MVP...")
    print(f"📍 Running: streamlit run {app_path}")
    print("💻 Access at: http://localhost:8501")
    
    subprocess.run([
        "streamlit",
        "run",
        str(app_path),
        "--logger.level=info"
    ])

if __name__ == "__main__":
    main()
