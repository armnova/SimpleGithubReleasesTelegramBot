import os
import mysql.connector
from mysql.connector import cursor
from mysql.connector.connection import MySQLConnection
import time
import logging
import threading

DATABASE_RETRY_INTERVAL = 10

logging.basicConfig(format="%(levelname)s @ %(asctime)s -> %(message)s", level=logging.DEBUG, handlers=[logging.FileHandler("./logs/databaseHandling.log"), logging.StreamHandler()])

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
            self.cursor.execute(f"SELECT repo, currentVersion FROM entries WHERE chat_id = {chatId}")
            self.db.commit()
            return self.cursor.fetchall()