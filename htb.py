import requests
import os
import datetime

class HTB_CTF:
    def __init__(self, email, password, ctfID):
        self.baseUrl = "https://ctf-api.hackthebox.com/api"
        self.accessToken = self.login(email, password)
        self.categories = self.getCategories()
        self.ctf = self.getCtfInfo(ctfID)
        self.setCtfFolderPath(self.ctf['name'])
        self.setWorkableChalls()
        self.createMarkdownFile()

    def login(self, email, password):
        url = self.baseUrl + "/login"
        res = requests.post(url, data={"email": email, "password": password, "remember": True})
        return res.json()["message"]["access_token"]

    def htbGetRequest(self, url):
        res = requests.get(self.baseUrl + url, headers={'Authorization': f'Bearer {self.accessToken}'})
        return res.json()

    def getCategories(self):
        return self.htbGetRequest("/challengeCategories")

    def getCtfInfo(self, ctfID):
        return self.htbGetRequest(f"/ctf/{ctfID}")

    def setCtfFolderPath(self, ctfName):
        ctfFolderName = f"htb_{ctfName}_{str(datetime.datetime.now().year)}".lower().replace(" ", "_")
        self.folderPath = f"./CTFS/{ctfFolderName}"
        try:
            os.makedirs(f"{self.folderPath}/files")
        except FileExistsError:
            pass

    def getChallengeDownload(self, challID):
        res = requests.get(f"{self.baseUrl}/challenge/download/{challID}", headers={'Authorization': f'Bearer {self.accessToken}'})
        return res.content

    def downloadChallengeFile(self, challenge):
        challFile = open(f"{self.folderPath}/files/{challenge['filename']}", "wb")
        challFile.write(self.getChallengeDownload(challenge['id']))
        challFile.close()

    def createMarkdownFile(self):
        markdownText = f"# {self.ctf['name']}\n\n"
        for markdownCategory in self.workableChalls.keys():
            markdownText += f"## {markdownCategory}\n\n"
            for chall in self.workableChalls[markdownCategory]:
                markdownText += f"### {chall['name']}\n\n"
                markdownText += f"#### Stats\n\n"
                markdownText += f"| Attribute | Info |\n"
                markdownText += f"|---|---|\n"
                markdownText += f"| Difficulty | {chall['difficulty']} |\n"
                markdownText += f"| Description | {chall['description']} |\n"
                markdownDownloadText = f"| File | - |\n\n"
                if chall['filename'] != "":
                    markdownDownloadText = f"| File | [Download](./files/{chall['filename']}) |\n\n"
                markdownText += markdownDownloadText
                markdownText += f"#### Solution\n\n"
        ctfFile = open(f"{self.folderPath}/README.md", "w")
        ctfFile.write(markdownText)
        ctfFile.close()

    def setWorkableChalls(self):
        self.workableChalls = {}
        for chall in self.ctf['challenges']:
            challCatID = chall['challenge_category_id']
            #if chall['filename'] != "":
                #self.downloadChallengeFile(chall)
            for category in self.categories:
                if category['id'] == challCatID:
                    if category['name'] not in self.workableChalls:
                        self.workableChalls[category['name']] = []
                    cleanChall = { "name": chall['name'], "difficulty": chall['difficulty'], "description": chall['description'], "filename": chall['filename']}
                    self.workableChalls[category['name']].append(cleanChall)
                    break