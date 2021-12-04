#!/usr/bin/python3
import sys
from htb import *
from ctfd import *

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("[!] Usage: ctfscrapper.py <url|ctf_id> <user|email> <password>")
        print("[!] Example: ctfscrapper.py https://demo.ctfd.io 'srrequiem@htb.com' 123456")
        sys.exit(1)
    ctfLinker = sys.argv[1]
    user = sys.argv[2]
    password = sys.argv[3]
    ctfType = "htb"
    ctfTypeSwitch = {
        "htb": HTB_CTF,
        "ctfd": CTFd_CTF
    }
    try:
        int(ctfLinker)
    except ValueError:
        ctfType = "ctfd"
    ctfTypeSwitch[ctfType](ctfLinker, user, password)