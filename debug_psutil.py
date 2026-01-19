import psutil
import os

pid = os.getpid()
p = psutil.Process(pid)
print(f"Name: '{p.name()}'")
print(f"Exe: '{p.exe()}'")
