import pickledb
from databaseHandling import DatabaseHandler

class PickleDBHandler(DatabaseHandler):

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
