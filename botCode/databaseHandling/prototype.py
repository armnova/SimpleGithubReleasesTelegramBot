from dataclasses import dataclass
from email.policy import strict
from typing import Tuple

DATABASE_RETRY_INTERVAL = 10

# TODO: get reponame from HTTP request for making it pretty (case-sensitive)

@dataclass
class dbEntry():
    id: int
    chatID: str
    repoOwner: str
    repoName: str
    nameHash: str
    repoLink: str
    currentReleaseTagName: str
    currentReleaseID: str

@dataclass
class dbEntryNoID():
    chatID: str
    repoOwner: str
    repoName: str
    nameHash: str
    repoLink: str
    currentReleaseTagName: str
    currentReleaseID: str

@dataclass
class dbEntryUpdate():
    chatID: str
    nameHash: str
    newTag: str

class DatabaseHandler():

    def __init__(self) -> None:
        pass

    def getRepos(self, chatId: str) -> list:
        pass
    
    def addRepo(self, chatId: str, repoPath: str) -> str:
        pass
    
    def removeRepo(self, chatId: str, repoNameHash: str):
        pass

    def dbDump(self) -> list:
        pass

    def updateEntries(self, updateCommands: list):
        pass
