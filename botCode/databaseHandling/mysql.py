import os
import mysql.connector
import time
import logging
import threading
import requests
import hashlib
import helpers
from mysql.connector import cursor
from mysql.connector.connection import MySQLConnection
from databaseHandling.prototype import dbEntry
from databaseHandling.prototype import DatabaseHandler

DATABASE_RETRY_INTERVAL = 10

# TODO: get reponame from HTTP request for making it pretty (case-sensitive)

class MySQLHandler(DatabaseHandler):

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
            self.cursor.execute(f'SELECT * FROM entries WHERE chatID = "{chatId}"')
            self.db.commit()
            returnList = []
            for entry in self.cursor.fetchall():
                returnList.append(dbEntry(*entry))
            return returnList
    
    def addRepo(self, chatId: str, repoPath: str) -> str:
        entryContent, valid = helpers.repoValidation(repoPath)
        if valid != True:
            return "Error"
        try:
            logging.debug(entryContent.repoOwner + " " + entryContent.repoName)
            response = requests.get(f"https://api.github.com/repos/{entryContent.repoOwner}/{entryContent.repoName}/releases")
            assert response.status_code == 200
            with self.dbLock:
                self.cursor.execute(f'SELECT repoName FROM entries WHERE chatID = "{chatId}" AND repoName = "{entryContent.repoName}"')
                self.db.commit()
                if len(self.cursor.fetchall()) != 0:
                    return "Exists"
                releaseTagName = response.json()[0]["tag_name"]
                releaseID = response.json()[0]["id"]
                nameHash = hashlib.md5(entryContent.repoName.encode()).hexdigest()
                self.cursor.execute(f'INSERT INTO entries (chatID, repoOwner, repoName, nameHash, repoLink, currentReleaseTagName, currentReleaseID) VALUES ("{chatId}", "{entryContent.repoOwner}", "{entryContent.repoName}", "{nameHash}", "{entryContent.repoLink}", "{releaseTagName}", "{releaseID}")')
                self.db.commit()
        except Exception as exc:
            logging.error(exc)
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
