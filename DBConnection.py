import os
from dotenv import load_dotenv

#Game import
import mysql.connector

load_dotenv()
host = os.getenv('HOST')
user = os.getenv('DBUSER')
password = os.getenv('DBPW')
database = os.getenv('DATABASE')

class DBConnection:
    global botDB, DBCursor

    @classmethod
    def connection(cls):
        global botDB, DBCursor
        botDB = mysql.connector.connect(host=host, user=user,
                                        password=password, database=database)
        DBCursor = botDB.cursor()
        return (botDB, DBCursor)

    @classmethod
    def fetchUserData(cls, dataType: str, userID: str):
        global botDB, DBCursor
        if botDB:
            pass
        else:
            botDB, DBCursor = cls.connection()
        vals = (userID, )
        sqlQuery = 'select * from userData where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        result = DBCursor.fetchone()

        if dataType == "userBalance":
            return result[1]
        elif dataType == "colorPref":
            return result[2]
        elif dataType == "sortPref":
            return result[3]
        elif dataType == "userWin":
            return result[4]

    @classmethod
    def fetchAllRankData(cls):
        global botDB, DBCursor
        if botDB:
            pass
        else:
            botDB, DBCursor = cls.connection()
        sqlQuery = 'select userID, userWin from userData order by userWin desc'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updateUserBalance(cls, userID: str, balance: int):
        global botDB, DBCursor
        if botDB:
            pass
        else:
            botDB, DBCursor = cls.connection()
        vals = (balance, userID)
        sqlQuery = 'update userData set userBalance = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()

    @classmethod
    def updateUserWin(cls, userID: str, win: int):
        global botDB, DBCursor
        if botDB:
            pass
        else:
            botDB, DBCursor = cls.connection()
        vals = (win, userID)
        sqlQuery = 'update userData set userWin = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()

    @classmethod
    def updateUserSortPref(cls, userID: str, sortPref: str):
        global botDB, DBCursor
        if botDB:
            pass
        else:
            botDB, DBCursor = cls.connection()
        vals = (sortPref, userID)
        sqlQuery = 'update userData set sortPref = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()

    @classmethod
    def updateUserHandColor(cls, userID: str, color: str):
        global botDB, DBCursor
        if botDB:
            pass
        else:
            botDB, DBCursor = cls.connection()
        vals = (color, userID)
        sqlQuery = 'update userData set colorPref = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()

    @classmethod
    def checkUserInDB(cls, userID: str):
        global botDB, DBCursor
        if botDB:
            pass
        else:
            botDB, DBCursor = cls.connection()
        DBCursor.execute("select * from userData where userID = " + userID)
        result = DBCursor.fetchall()
        return len(result) != 0

    @classmethod
    def addUserToDB(cls, userID: str):
        global botDB, DBCursor
        if botDB:
            pass
        else:
            botDB, DBCursor = cls.connection()
        query = """INSERT INTO userData (userID, userBalance, colorPref, sortPref, userWin) 
                VALUES (%s, %s, %s, %s, %s) """
        dataTuple = (userID, 10000, "#00ff00", 'd', 0)
        DBCursor.execute(query, dataTuple)
        botDB.commit()
