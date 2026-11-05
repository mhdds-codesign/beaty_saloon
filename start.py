import uvicorn
import sys
import os
import subprocess
import signal

base = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(base, "backend")
frontend_path = os.path.join(base, "frontend")

if __name__ == "__main__":
    print("start running frontend...")
    frontend_subp = subprocess.Popen(
        "npm run dev",
        cwd=frontend_path,  # مسیر صحیح
        shell=True
    )

    os.chdir(backend_path)
    sys.path.insert(0, backend_path)  # مسیر صحیح
    print("start running backend...")
    try:
        uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=False)
    except KeyboardInterrupt:
        print("turning backend off...")
    finally:
        subprocess.run(['taskkill','/F','/T','/PID',str(frontend_subp.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("done!")