import os
from dataclasses import dataclass
import time
import logging
import threading
import re
import requests
import hashlib

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
    previousReleaseID: str

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
