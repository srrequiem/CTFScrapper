#!/usr/bin/python3
import requests
import os
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.error import HTTPError

class CTFd_CTF:
    def __init__(self, base_url, user="", password="", token=""):
        self.base_url = base_url
        self.session = self.login(user, password, token)
        self.challenges = self._get_challenges()
        self._set_ctf_folderpath(self.ctf_name)
        self._set_workable_challs()
        self._create_markdown_file()

    def login(self, user, password, token):
        session = requests.Session()
        url = f"{self.base_url}/login"
        res = session.get(url)
        try:
            soup = BeautifulSoup(res.text, 'lxml')
            nonce = soup.find('input', {'name':'nonce'}).get('value')
            self.ctf_name = soup.title.string
            if token:
                session.cookies.set("session", token)
            else:
                session.post(url, data={"name": user, "password": password, "_submit": "Submit", "nonce": nonce})
        except HTTPError as hp:
            print("[!] Authentication failure")
            self.token = input("Session: ")
            session.cookies.set("session", self.token)

        return session

    def _get_request(self, url):
        res = self.session.get(f"{self.base_url}{url}")
        res_json = res.json()
        if "success" not in res_json:
            raise Exception("[!] Something went wrong making get request!")
        return res_json["data"]

    def _get_challenges(self):
        return self._get_request("/api/v1/challenges")
        
    def _get_challenge_info(self, chall_id):
        return self._get_request(f"/api/v1/challenges/{chall_id}")

    def _set_ctf_folderpath(self, ctfName):
        time_now = datetime.datetime.now()
        time_now_month_year = f"{str(time_now.year)}{str(time_now.month)}{str(time_now.day)}"
        ctf_folder_name = f"{time_now_month_year}_{ctfName}".lower().replace(" ", "_")
        self.folder_path = f"./CTFS/{ctf_folder_name}"
        try:
            os.makedirs(f"{self.folder_path}/files")
        except FileExistsError:
            pass

    def _get_challenge_download(self, chall_url):
        res = self.session.get(f"{self.base_url}{chall_url}")
        return res.content

    def _download_challenge_file(self, challenge):
        url = urlparse(challenge['url'])
        real_file_name = os.path.basename(url.path)
        chars_to_remove = "/ "
        clean_file_name = f"{challenge['filename']}_{real_file_name}".lower().translate({ord(c): "_" for c in chars_to_remove})
        chall_file = open(f"{self.folder_path}/files/{clean_file_name}", "wb")
        chall_file.write(self._get_challenge_download(challenge['url']))
        chall_file.close()

    def _create_markdown_file(self):
        md_text = f"# {self.ctf_name}\n\n"
        for md_category in self.workable_challs.keys():
            md_text += f"## {md_category}\n\n"
            for chall in self.workable_challs[md_category]:
                md_text += f"### {chall['name']}\n\n"
                md_text += f"#### Stats\n\n"
                md_text += f"| Attribute | Info |\n"
                md_text += f"|---|---|\n"
                md_text += f"| Description | {chall['description']} |\n"
                md_files_text = f" "
                for chall_file in chall['files']:
                    md_files_text += f"[{chall_file}](./files/{chall_file}) "
                md_download_text = f"| Files | {md_files_text} |\n\n"
                md_text += md_download_text
                md_text += f"#### Solution\n\n"
        ctf_file = open(f"{self.folder_path}/README.md", "w")
        ctf_file.write(md_text)
        ctf_file.close()

    def _set_workable_challs(self):
        self.workable_challs = {}
        for chall in self.challenges:
            chall_info = self._get_challenge_info(chall['id'])
            self.workable_challs[chall_info['category']] = []
            clean_chall_files = []
            for chall_file in chall_info['files']:
                filename = f"{chall_info['category']}_{chall_info['name']}"
                self._download_challenge_file({ "url": chall_file, "filename": filename })
                clean_chall_files.append(filename)
            clean_chall = { "name": chall_info['name'], "description": chall_info['description'], "files": clean_chall_files}
            self.workable_challs[chall_info['category']].append(clean_chall)
