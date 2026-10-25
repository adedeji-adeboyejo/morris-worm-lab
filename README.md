# Morris Worm Attack Lab

A contained, educational re-implementation of the 1988 Morris Worm, built as part of the SEED Labs "Morris Worm Attack" assignment (https://seedsecuritylabs.org/Labs_20.04/Networking/Morris_Worm/) for COMP 3670: Computer Networks.

## Overview
 
The Morris worm (November 1988) was one of the oldest computer worms distributed via the Internet, and
the first to gain significant mainstream media attention. 
The techniques used by the Morris Worm involves two main parts:
- Attack: The attack part exploits a vulnerability (or a few of them), so a worm can get
entry to another computer. 
- Self-duplication: The self-duplication part is to send a copy of itself to the compromised machine,
and then launch the attack from there.

This lab helps to gain a better understanding of the behavior of worms, by writing
a simple worm and testing it in a contained environment. We do this through a series of tasks:
 
1. Exploit a known buffer-overflow vulnerability in a provided server to gain remote code execution on one hardcoded host.
2. Have the exploit payload pull down a full copy of the worm onto the newly compromised host once the exploit succeeds.
3. Make the worm pick new targets and repeat the attack, automatically spreading from host to host.
4. Add a self-infection check so the worm doesn't spawn endless copies of itself and DoS the network.
5. Release it in an emulated network and observe it spread exponentially across the network via the map visualization.

Everything runs inside the SEED Internet Emulator, which models hosts, routers, and autonomous systems as Docker containers and provides a live map for visualizing traffic and infection spread.

## Environment & Prerequisites
