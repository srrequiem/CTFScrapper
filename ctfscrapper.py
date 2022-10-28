#!/usr/bin/python3
import sys
import argparse
from htb import *
from ctfd import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog = 'CTFScrapper', description='Gather CTF challege files and info')
    parser.add_argument('url_id', type=str, help='CTFd url or HTB event ID')
    parser.add_argument('-u', '--username', type=str, help='Username you used to sign up')
    parser.add_argument('-p', '--password', type=str, help='Password you used to sign up')
    parser.add_argument('-t', '--token', type=str, help='Cookie session or Bearer token')
    args = parser.parse_args()
    ctfType = "htb"
    ctfTypeSwitch = {
        "htb": HTB_CTF,
        "ctfd": CTFd_CTF
    }
    try:
        int(args.url_id)
    except ValueError:
        ctfType = "ctfd"
    ctfTypeSwitch[ctfType](args.url_id, user=args.username, password=args.password, token=args.token)