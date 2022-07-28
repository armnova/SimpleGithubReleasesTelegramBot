import hashlib
import logging
import boto3
import requests
import helpers
from collections import OrderedDict
from databaseHandling.prototype import DatabaseHandler, dbEntryNoID
from boto3.dynamodb.conditions import Key

class DynamoDBHandler(DatabaseHandler):

    def __init__(self, tableName: str) -> None:
        self.db = boto3.resource("dynamodb")
        self.table = self.db.Table(tableName)

    def getRepos(self, chatId: str) -> list:
        filterExp = Key("chatID").eq(str(chatId))
        response = self.table.query(KeyConditionExpression=filterExp)
        repoList = []
        for item in response["Items"]:
            repoList.append(dbEntryNoID(
                chatID = item["chatID"],
                nameHash = item["nameHash"],
                repoOwner= item["repoOwner"],
                repoName = item["repoName"],
                repoLink = item["repoLink"],
                currentReleaseTagName = item["currentReleaseTagName"],
                currentReleaseID = item["currentReleaseID"],
            ))
        return repoList
    
    def addRepo(self, chatId: str, repoPath: str) -> str:
        entryContent = helpers.repoValidation(repoPath)
        try:
            logging.debug(entryContent.repoOwner + " " + entryContent.repoName)
            response = requests.get(f"https://api.github.com/repos/{entryContent.repoOwner}/{entryContent.repoName}/releases")
            assert response.status_code == 200
            releaseTagName = response.json()[0]["tag_name"]
            releaseID = response.json()[0]["id"]
            nameHash = hashlib.md5(entryContent.repoName.encode()).hexdigest()
            entryDict = OrderedDict()
            entryDict["chatID"] = str(chatId)
            entryDict["nameHash"] = str(nameHash)
            entryDict["repoName"] = str(entryContent.repoName)
            entryDict["repoOwner"] = str(entryContent.repoOwner)
            entryDict["repoLink"] = str(entryContent.repoLink)
            entryDict["currentReleaseTagName"] = str(releaseTagName)
            entryDict["currentReleaseID"] = str(releaseID)
            self.table.put_item(Item=entryDict)
        except Exception as exc:
            logging.error(exc)
            return "Error"
    
    def removeRepo(self, chatId: str, nameHash: str):
        self.table.delete_item(Key={
            "chatID": str(chatId),
            "nameHash": str(nameHash)
        })

    def dbDump(self) -> list:
        response = self.table.scan()
        repoList = []
        for item in response["Items"]:
            repoList.append(dbEntryNoID(
                chatID = item["chatID"],
                nameHash = item["nameHash"],
                repoOwner= item["repoOwner"],
                repoName = item["repoName"],
                repoLink = item["repoLink"],
                currentReleaseTagName = item["currentReleaseTagName"],
                currentReleaseID = item["currentReleaseID"],
            ))
        return repoList

    def updateEntries(self, updateCommands: list):
        for entry in updateCommands:
            self.table.update_item(
                Key = {
                    "chatID": entry.chatID,
                    "nameHash": entry.nameHash
                },
                UpdateExpression = "SET currentReleaseTagName = :val1",
                ExpressionAttributeValues = {
                    ":val1" : entry.newTag
                }
            )
