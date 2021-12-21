#!/usr/bin/python3
import requests
import os
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse

class CTFd_CTF:
    def __init__(self, ctfLink, user, password):
        self.baseUrl = ctfLink
        self.session = self.login(user, password)
        self.challenges = self.getChallenges()
        self.setCtfFolderPath(self.ctfName)
        self.setWorkableChalls()
        self.createMarkdownFile()

    def login(self, user, password):
        session = requests.Session()
        url = f"{self.baseUrl}/login"
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'lxml')
        nonce = soup.find('input', {'name':'nonce'}).get('value')
        self.ctfName = soup.title.string
        session.post(url, data={"name": user, "password": password, "_submit": "Submit", "nonce": nonce})
        return session

    def getRequest(self, url):
        res = self.session.get(f"{self.baseUrl}{url}")
        resJson = res.json()
        if resJson["success"] is True:
            return resJson["data"]
        raise Exception("[!] Something went wrong making get request!")

    def getChallenges(self):
        return self.getRequest("/api/v1/challenges")
        
    def getChallengeInfo(self, challID):
        return self.getRequest(f"/api/v1/challenges/{challID}")

    def setCtfFolderPath(self, ctfName):
        timeNow = datetime.datetime.now()
        timeNowMonthYear = f"{str(timeNow.year)}{str(timeNow.month)}"
        ctfFolderName = f"{timeNowMonthYear}_{ctfName}".lower().replace(" ", "_")
        self.folderPath = f"./CTFS/{ctfFolderName}"
        try:
            os.makedirs(f"{self.folderPath}/files")
        except FileExistsError:
            pass

    def getChallengeDownload(self, challUrl):
        res = self.session.get(f"{self.baseUrl}{challUrl}")
        return res.content

    def downloadChallengeFile(self, challenge):
        url = urlparse(challenge['url'])
        realFilename = os.path.basename(url.path)
        cleanFilename = f"{challenge['filename']}_{realFilename}".lower().replace(" ", "_")
        challFile = open(f"{self.folderPath}/files/{cleanFilename}", "wb")
        challFile.write(self.getChallengeDownload(challenge['url']))
        challFile.close()

    def createMarkdownFile(self):
        markdownText = f"# {self.ctfName}\n\n"
        for markdownCategory in self.workableChalls.keys():
            markdownText += f"## {markdownCategory}\n\n"
            for chall in self.workableChalls[markdownCategory]:
                markdownText += f"### {chall['name']}\n\n"
                markdownText += f"#### Stats\n\n"
                markdownText += f"| Attribute | Info |\n"
                markdownText += f"|---|---|\n"
                markdownText += f"| Description | {chall['description']} |\n"
                markdownFilesText = f" "
                for challFile in chall['files']:
                    markdownFilesText += f"[{challFile}](./files/{challFile}) "
                markdownDownloadText = f"| Files | {markdownFilesText} |\n\n"
                markdownText += markdownDownloadText
                markdownText += f"#### Solution\n\n"
        ctfFile = open(f"{self.folderPath}/README.md", "w")
        ctfFile.write(markdownText)
        ctfFile.close()

    def setWorkableChalls(self):
        self.workableChalls = {}
        for chall in self.challenges:
            challInfo = self.getChallengeInfo(chall['id'])
            self.workableChalls[challInfo['category']] = []
            cleanChallFiles = []
            for challFile in challInfo['files']:
                filename = f"{challInfo['category']}_{challInfo['name']}"
                self.downloadChallengeFile({ "url": challFile, "filename": filename })
                cleanChallFiles.append(filename)
            cleanChall = { "name": challInfo['name'], "description": challInfo['description'], "files": cleanChallFiles}
            self.workableChalls[challInfo['category']].append(cleanChall)
