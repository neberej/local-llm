##
##    Kill port(s) used by python
##    Use it as python kill.py
##

import subprocess
import os
import signal

def get_pids_on_port(port):
    try:
        output = subprocess.check_output(['lsof', '-i', f':{port}'], text=True)
        lines = output.strip().split('\n')[1:]  # Skip the header
        pids = set()
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                command = parts[0]
                pid = int(parts[1])
                if command.lower().startswith('python'):
                    pids.add(pid)
        return pids
    except subprocess.CalledProcessError:
        return set()

def kill_pids(pids):
    for pid in pids:
        try:
            print(f"Killing PID {pid}")
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            print(f"PID {pid} not found")
        except PermissionError:
            print(f"No permission to kill PID {pid}")

if __name__ == "__main__":
    pids = get_pids_on_port(8000)
    if pids:
        kill_pids(pids)
    else:
        print("No Python process found on port 8000.")
