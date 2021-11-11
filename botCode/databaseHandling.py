import os
import mysql.connector
from mysql.connector import cursor
from mysql.connector.connection import MySQLConnection
from dataclasses import dataclass
import time
import logging
import threading
import re
import requests

DATABASE_RETRY_INTERVAL = 10

logging.basicConfig(format="%(levelname)s @ %(asctime)s -> %(message)s", level=logging.DEBUG, handlers=[logging.FileHandler("./logs/databaseHandling.log"), logging.StreamHandler()])

@dataclass
class dbEntry():
    id: int
    chatID: str
    repoName: str
    repoLink: str
    currentReleaseTagName: str
    currentReleaseID: str
    previousReleaseID: str

class DatabaseHandler():

    def __init__(self) -> None:
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
            self.cursor.execute(f'SELECT repoName, currentReleaseTagName, repoLink FROM entries WHERE chatID = "{chatId}"')
            self.db.commit()
            entryList = []
            #for row in self.cursor.fetchall():
            #    entry = dbEntry(row)
            returnList = self.cursor.fetchall()
            return returnList
    
    def addRepo(self, chatId: str, repoLink: str) -> str:
        regexMatch = re.match("(?:https://)github.com[:/](.*)[:/](.*)", repoLink)
        if regexMatch:
            # get latest release version
            # insert into db: group 1 is the user+repo name
            ownerAndRepo = regexMatch.groups(1)
            owner = ownerAndRepo[0]
            repo = ownerAndRepo[1]
            try:
                response = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases")
                assert response.status_code == 200
                with self.dbLock:
                    self.cursor.execute(f'SELECT repoName FROM entries WHERE chatID = "{chatId}" AND repoName = "{repo}"')
                    self.db.commit()
                    if len(self.cursor.fetchall()) != 0:
                        return "Exists"

                    #logging.debug(response.json()[0])

                    releaseTagName = response.json()[0]["tag_name"]
                    releaseID = response.json()[0]["id"]
                    self.cursor.execute(f'INSERT INTO entries (chatID, repoName, repoLink, currentReleaseTagName, currentReleaseID, previousReleaseID) VALUES ("{chatId}", "{repo}", "{repoLink}", "{releaseTagName}", "{releaseID}", "{releaseID}")')
                    self.db.commit()
            except:
                raise
            return "Succesful"

        elif re.match("(.*)[/](.*)", repoLink):
            # owner/repo

            pass
        else:
            return "Invalid"