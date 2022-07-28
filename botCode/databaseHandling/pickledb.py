import hashlib
import pickledb
import requests
import helpers
import logging
from dataclasses import dataclass
from databaseHandling.prototype import DatabaseHandler, dbEntry

class PickleDBHandler(DatabaseHandler):

    def __init__(self, databaseFile: str) -> None:
        self.db = pickledb.load(databaseFile, auto_dump=True)

    def getRepos(self, chatId: str) -> list:
        repos = self.db.lgetall(chatId)
        return repos
    
    def addRepo(self, chatId: str, repoPath: str) -> str:
        entryContent = helpers.repoValidation(repoPath)
        stringChatID = str(chatId)
        if entryContent.repoName == "":
            return "Error"
        try:
            if not self.db.exists(stringChatID):
                self.db.lcreate(stringChatID)
            if self.db.llen(stringChatID) != 0:
                userRepos = self.getRepos(stringChatID)
                for repo in userRepos:
                    if repo.repoName == entryContent.repoName:
                        return "Exists"
            response = requests.get(f"https://api.github.com/repos/{entryContent.repoOwner}/{entryContent.repoName}/releases")
            assert response.status_code == 200
            entryContent.currentReleaseTagName = response.json()[0]["tag_name"]
            entryContent.currentReleaseID = str(response.json()[0]["id"])
            entryContent.nameHash = hashlib.md5(entryContent.repoName.encode()).hexdigest()
            self.db.ladd(stringChatID, entryContent)
            return "Succesful"
        except:
            return "Error"

    def removeRepo(self, chatId: str, repoNameHash: str):
        userRepos = self.getRepos(chatId)
        counter = 0
        for repo in userRepos:
            if repo.nameHash == repoNameHash:
                self.db.lpop(chatId, counter)
                return
            counter += 1

    def dbDump(self) -> list:
        return self.db.getall()

    def updateEntries(self, updateCommands: list):
        pass
