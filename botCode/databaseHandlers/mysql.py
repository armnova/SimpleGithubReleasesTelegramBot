import os
from botCode.databaseHandling import DatabaseHandler
import mysql.connector
from mysql.connector import cursor
from mysql.connector.connection import MySQLConnection
from dataclasses import dataclass
import time
import logging
import threading
import re
import requests
import hashlib

DATABASE_RETRY_INTERVAL = 10

# TODO: get reponame from HTTP request for making it pretty (case-sensitive)

class MySQLHandler(DatabaseHandler):

    def __init__(self) -> None:
        logging.basicConfig(format="%(levelname)s @ %(asctime)s -> %(message)s", level=logging.WARNING, handlers=[logging.FileHandler("./logs/databaseHandling.log"), logging.StreamHandler()])

        #get database credentials from environment
        dbhost = os.environ.get("MYSQL_HOST")
        dbuser = os.environ.get("MYSQL_USER")
        dbpass = os.environ.get("MYSQL_PASSWORD")
        dbname = os.environ.get("MYSQL_DB")

        self.dbLock = threading.Lock()
        self.db = MySQLConnection()
        self.cursor = cursor.MySQLCursor()

        connectedToDatabase = False
        while not connectedToDatabase:
            try:
                self.db = mysql.connector.connect(host=dbhost, user=dbuser, password=dbpass, database = dbname)
                self.cursor = self.db.cursor(buffered=True)
                connectedToDatabase = True
                logging.info("Succesfully connected to database")
            except Exception as e:
                connectedToDatabase = False
                logging.critical("Connection to database failed, retrying in " + str(DATABASE_RETRY_INTERVAL) + " seconds: " + str(e))
                time.sleep(DATABASE_RETRY_INTERVAL)

    def getRepos(self, chatId: str) -> list:
        with self.dbLock:
            self.cursor.execute(f'SELECT * FROM entries WHERE chatID = "{chatId}"')
            self.db.commit()
            returnList = []
            for entry in self.cursor.fetchall():
                returnList.append(dbEntry(*entry))
            return returnList
    
    def addRepo(self, chatId: str, repoPath: str) -> str:
        owner = ""
        repo = ""
        repoLink = ""
        regexMatch = re.match("(?:https://)github.com[:/](.*)[:/](.*)", repoPath)
        if regexMatch:
            # get latest release version
            # insert into db: group 1 is the user+repo name
            ownerAndRepo = regexMatch.groups(1)
            owner = ownerAndRepo[0]
            repo = ownerAndRepo[1]
            repoLink = repoPath
        elif re.match("(.*)[/](.*)", repoPath):
            regexMatch = re.match("(.*)[/](.*)", repoPath)
            owner = regexMatch.groups(1)[0]
            repo = regexMatch.groups(1)[1]
            repoLink = f"https://github.com/{owner}/{repo}"
        else:
            return "Invalid"

        try:
            logging.debug(owner + " " + repo)
            response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases")
            assert response.status_code == 200
            with self.dbLock:
                self.cursor.execute(f'SELECT repoName FROM entries WHERE chatID = "{chatId}" AND repoName = "{repo}"')
                self.db.commit()
                if len(self.cursor.fetchall()) != 0:
                    return "Exists"
                releaseTagName = response.json()[0]["tag_name"]
                releaseID = response.json()[0]["id"]
                nameHash = hashlib.md5(repo.encode()).hexdigest()
                self.cursor.execute(f'INSERT INTO entries (chatID, repoOwner, repoName, nameHash, repoLink, currentReleaseTagName, currentReleaseID, previousReleaseID) VALUES ("{chatId}", "{owner}", "{repo}", "{nameHash}", "{repoLink}", "{releaseTagName}", "{releaseID}", "{releaseID}")')
                self.db.commit()
        except:
            return "Error"

        return "Succesful"
    
    def removeRepo(self, chatId: str, repoNameHash: str):
        with self.dbLock:
            self.cursor.execute(f'DELETE FROM entries WHERE chatID = "{chatId}" AND nameHash = "{repoNameHash}"')

    def dbDump(self) -> list:
        with self.dbLock:
            self.cursor.execute("SELECT * FROM entries")
            self.db.commit()
            returnList = []
            for entry in self.cursor.fetchall():
                returnList.append(dbEntry(*entry))
            return returnList

    def updateEntries(self, updateCommands: list):
        with self.dbLock:
            for entry in updateCommands:
                self.cursor.execute(entry)
            self.db.commit()
