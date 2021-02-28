import os
from dotenv import load_dotenv

#Game import
import mysql.connector

class DBConnection:

    @classmethod
    def connection(cls):
        load_dotenv()
        botDB = mysql.connector.connect(host=os.getenv('HOST'), user=os.getenv('USERNAME'),
                                        password=os.getenv('PASSWORD'), database=os.getenv('DATABASE'))
        DBCursor = botDB.cursor()
        return (botDB, DBCursor)

    @classmethod
    def fetchUserData(cls, dataType: str, userID: str):
        botDB, DBCursor = cls.connection()
        vals = (userID, )
        sqlQuery = 'select * from userData where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        result = DBCursor.fetchone()
        DBCursor.close()
        botDB.close()

        if dataType == "userBalance":
            return result[1]
        elif dataType == "colorPref":
            return result[2]
        elif dataType == "sortPref":
            return result[3]

    @classmethod
    def updateUserBalance(cls, userID: str, balance: int):
        botDB, DBCursor = cls.connection()
        vals = (balance, userID)
        sqlQuery = 'update userData set userBalance = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        DBCursor.close()
        botDB.close()

    @classmethod
    def updateUserSortPref(cls, userID: str, sortPref: str):
        botDB, DBCursor = cls.connection()
        vals = (sortPref, userID)
        sqlQuery = 'update userData set sortPref = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        DBCursor.close()
        botDB.close()

    @classmethod
    def updateUserHandColor(cls, userID: str, color: str):
        botDB, DBCursor = cls.connection()
        vals = (color, userID)
        sqlQuery = 'update userData set colorPref = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        DBCursor.close()
        botDB.close()

    @classmethod
    def checkUserInDB(cls, userID: str):
        botDB, DBCursor = cls.connection()
        DBCursor.execute("select * from userData where userID = " + userID)
        result = DBCursor.fetchall()
        DBCursor.close()
        botDB.close()
        return len(result) != 0

    @classmethod
    def addUserToDB(cls, userID: str):
        botDB, DBCursor = cls.connection()
        query = """INSERT INTO userData (userID, userBalance, colorPref, sortPref) 
                VALUES (%s, %s, %s, %s) """
        dataTuple = (userID, 10000, "#00ff00", 'd')
        DBCursor.execute(query, dataTuple)
        botDB.commit()
        DBCursor.close()
        botDB.close()
