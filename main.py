import sys
from htb import *

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("[!] Usage: main.py <htb|ctfd|echoctf> <url|ctf_id> <user|email> <password>")
        print("[!] Example: main.py htb 249 'srrequiem@htb.com' 123456")
        sys.exit(1)
    ctfType = sys.argv[1]
    ctfLinker = sys.argv[2]
    user = sys.argv[3]
    password = sys.argv[4]
    switch = {
        "htb": HTB_CTF
    }
    switch[ctfType](user, password, ctfLinker)