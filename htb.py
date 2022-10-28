#!/usr/bin/python3
import requests
import os
import datetime

class HTB_CTF:
    def __init__(self, ctf_id, user="", password="", token=""):
        self.base_url = "https://ctf.hackthebox.com/api"
        if not token:
            token = input("Bearer token: ")
        self.token = token
        self.categories = self._get_categories()
        self.ctf = self._get_ctf_info(ctf_id)
        self._set_ctf_folderpath(self.ctf['name'])
        self._set_workable_challs()
        self._create_markdown_file()

    def _htb_get_request(self, url):
        res = requests.get(self.base_url + url, headers={'Authorization': f'Bearer {self.token}'})
        return res.json()

    def _get_categories(self):
        return self._htb_get_request("/public/challengeCategories")

    def _get_ctf_info(self, ctf_id):
        return self._htb_get_request(f"/ctf/{ctf_id}")

    def _set_ctf_folderpath(self, ctf_name):
        time_now = datetime.datetime.now()
        time_now_month_year = f"{str(time_now.year)}{str(time_now.month)}{str(time_now.day)}"
        ctf_foldername = f"{time_now_month_year}_htb_{ctf_name}".lower().replace(" ", "_")
        self.folder_path = f"./CTFS/{ctf_foldername}"
        try:
            os.makedirs(f"{self.folder_path}/files")
        except FileExistsError:
            pass

    def _get_challenge_download(self, chall_id):
        res = requests.get(f"{self.base_url}/challenge/download/{chall_id}", headers={'Authorization': f'Bearer {self.token}'})
        return res.content

    def _download_challege_file(self, challenge):
        chall_file = open(f"{self.folder_path}/files/{challenge['filename']}", "wb")
        chall_file.write(self._get_challenge_download(challenge['id']))
        chall_file.close()

    def _create_markdown_file(self):
        md_text = f"# {self.ctf['name']}\n\n"
        for md_category in self.workable_challs.keys():
            md_text += f"## {md_category}\n\n"
            for chall in self.workable_challs[md_category]:
                md_text += f"### {chall['name']}\n\n"
                md_text += f"#### Stats\n\n"
                md_text += f"| Attribute | Info |\n"
                md_text += f"|---|---|\n"
                md_text += f"| Difficulty | {chall['difficulty']} |\n"
                md_text += f"| Description | {chall['description']} |\n"
                md_download_text = f"| File | - |\n\n"
                if chall['filename'] != "":
                    md_download_text = f"| File | [{chall['filename']}](./files/{chall['filename']}) |\n\n"
                md_text += md_download_text
                md_text += f"#### Solution\n\n"
        ctf_file = open(f"{self.folder_path}/README.md", "w")
        ctf_file.write(md_text)
        ctf_file.close()

    def _set_workable_challs(self):
        self.workable_challs = {}
        for chall in self.ctf['challenges']:
            chall_cat_id = chall['challenge_category_id']
            if chall['filename'] != "":
                self._download_challege_file(chall)
            for category in self.categories:
                if category['id'] == chall_cat_id:
                    if category['name'] not in self.workable_challs:
                        self.workable_challs[category['name']] = []
                    clean_chall = { "name": chall['name'], "difficulty": chall['difficulty'], "description": chall['description'], "filename": chall['filename']}
                    self.workable_challs[category['name']].append(clean_chall)
                    break