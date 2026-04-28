"""
Launcher script — starts both FastAPI backend and Streamlit frontend.
Usage: python run.py
"""

import subprocess
import sys
import os
import time
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    processes = []

    try:
        # Start FastAPI backend
        backend_cmd = [
            sys.executable, "-m", "uvicorn",
            "backend.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ]
        print("🚀 Starting FastAPI backend on http://localhost:8000 ...")
        backend = subprocess.Popen(backend_cmd, cwd=ROOT_DIR)
        processes.append(backend)

        time.sleep(2)  # Let backend initialize

        # Start Streamlit frontend
        frontend_cmd = [
            sys.executable, "-m", "streamlit", "run",
            os.path.join(ROOT_DIR, "frontend", "app.py"),
            "--server.port", "8501",
            "--server.headless", "true",
        ]
        print("🎨 Starting Streamlit frontend on http://localhost:8501 ...")
        frontend = subprocess.Popen(frontend_cmd, cwd=ROOT_DIR)
        processes.append(frontend)

        print("\n✅ Both services running!")
        print("   Backend:  http://localhost:8000/docs")
        print("   Frontend: http://localhost:8501\n")

        # Wait for either process to exit
        while True:
            for p in processes:
                if p.poll() is not None:
                    raise KeyboardInterrupt
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait(timeout=5)
        print("Done.")


if __name__ == "__main__":
    main()
