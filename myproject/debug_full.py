# myproject/debug_tools/debug_full.py
import subprocess
import os

scripts = [
    "debug_email.py",
    "debug_database.py",
    "debug_static.py",
    "debug_security.py",
]

for script in scripts:
    print(f"\n==============================")
    print(f"🚀 Running {script}")
    print(f"==============================\n")
    subprocess.run(["python", os.path.join("myproject", script)])
