import subprocess
import sys
import time
import os

def run_commands():
    # Define paths
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, 'backend')
    
    print("Starting Healthcare RAG System...")
    print("====================================")
    
    try:
        # Start the backend (FastAPI) as a subprocess
        print("Starting Backend Server (FastAPI) on port 8000...")
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=backend_dir
        )
        
        # Give the backend a couple of seconds to start up
        time.sleep(2)
        
        # Start the frontend (Streamlit) as a subprocess
        print("Starting Frontend Server (Streamlit)...")
        frontend_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend/app.py"],
            cwd=root_dir
        )
        
        print("\nSystem is running!")
        print("--> App URL (Click this link): http://localhost:8501")
        print("\nPress Ctrl+C to stop both servers.")
        
        # Wait for both processes to complete (or for user to press Ctrl+C)
        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers stopped successfully.")

if __name__ == "__main__":
    run_commands()
