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
    botDB = mysql.connector.connect(host=host, user=user,
                                    password=password, database=database)

    @classmethod
    def connection(cls):
        if DBConnection.botDB.is_connected():
            pass
        else:
            #print("Not connected")
            DBConnection.botDB = mysql.connector.connect(host=host, user=user,
                                            password=password, database=database)

        DBCursor = DBConnection.botDB.cursor()
        return (DBConnection.botDB, DBCursor)

    @classmethod
    def fetchUserData(cls, dataType: str, userID: str):
        botDB, DBCursor = cls.connection()
        vals = (userID, )
        sqlQuery = 'select * from userData where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        result = DBCursor.fetchone()
        #DBCursor.close()
        #botDB.close()

        if dataType == "userBalance":
            return result[1]
        elif dataType == "colorPref":
            return result[2]
        elif dataType == "sortPref":
            return result[3]
        elif dataType == "userWin":
            return result[4]

    @classmethod
    def fetchUserMcName(cls, userID: str):
        botDB, DBCursor = cls.connection()
        vals = (userID, )
        sqlQuery = 'select mcName from userData where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        result = DBCursor.fetchone()
        return result

    @classmethod
    def fetchAllRankData(cls):
        botDB, DBCursor = cls.connection()
        sqlQuery = 'select userID, userWin from userData order by userWin desc'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        #DBCursor.close()
        #botDB.close()
        return result

    @classmethod
    def fetchAllMoneyData(cls):
        botDB, DBCursor = cls.connection()
        sqlQuery = 'select userID, userBalance from userData order by userBalance desc'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updateUserBalance(cls, userID: str, balance: int):
        botDB, DBCursor = cls.connection()
        vals = (balance, userID)
        sqlQuery = 'update userData set userBalance = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserWin(cls, userID: str, win: int):
        botDB, DBCursor = cls.connection()
        vals = (win, userID)
        sqlQuery = 'update userData set userWin = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserSortPref(cls, userID: str, sortPref: str):
        botDB, DBCursor = cls.connection()
        vals = (sortPref, userID)
        sqlQuery = 'update userData set sortPref = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserHandColor(cls, userID: str, color: str):
        botDB, DBCursor = cls.connection()
        vals = (color, userID)
        sqlQuery = 'update userData set colorPref = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserMcName(cls, userID: str, mcName: str):
        botDB, DBCursor = cls.connection()
        vals = (mcName, userID)
        sqlQuery = 'update userData set mcName = %s where userID = %s'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()

    @classmethod
    def checkUserInDB(cls, userID: str):
        botDB, DBCursor = cls.connection()
        DBCursor.execute("select * from userData where userID = " + userID)
        result = DBCursor.fetchall()
        #DBCursor.close()
        #botDB.close()
        return len(result) != 0

    @classmethod
    def addUserToDB(cls, userID: str):
        botDB, DBCursor = cls.connection()
        query = """INSERT INTO userData (userID, userBalance, colorPref, sortPref, userWin) 
                VALUES (%s, %s, %s, %s, %s) """
        dataTuple = (userID, 10000, "#00ff00", 'd', 0)
        DBCursor.execute(query, dataTuple)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def createServer(cls, id: str, pw: str, game: str, port: str, remarks: str):
        botDB, DBCursor = cls.connection()
        query = """INSERT INTO serverlist (id, pw, game, port, remarks) 
                VALUES (%s, %s, %s, %s, %s) """
        dataTuple = (id, pw, game, port, remarks)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def updateServer(cls, id: str, pw: str, game: str, port: str, remarks: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE serverlist
                SET pw=%s, game=%s, port=%s, remarks=%s
                WHERE id=%s """
        dataTuple = (pw, game, port, remarks, id)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def updateServerPw(cls, id: str, pw: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE serverlist
                SET pw=%s
                WHERE id=%s """
        dataTuple = (pw, id)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def deleteServer(cls, id: str):
        botDB, DBCursor = cls.connection()
        query = """DELETE FROM serverlist
                WHERE id=%s """
        data = (id,)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def selectServer(cls, id: str):
        botDB, DBCursor = cls.connection()
        vals = (id, )
        sqlQuery = """SELECT id, pw, game, port, remarks
                FROM serverlist
                WHERE id = %s"""
        DBCursor.execute(sqlQuery, vals)
        return DBCursor.fetchone()

    @classmethod
    def selectAllServer(cls):
        botDB, DBCursor = cls.connection()
        sqlQuery = 'select id, pw, game, port, remarks from serverlist order by game, remarks'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def getCaseNo(cls):
        botDB, DBCursor = cls.connection()
        sqlQuery = 'select case_no from CovLocate limit 1'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updateCaseNo(cls, case_no: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE CovLocate
                SET case_no=%s"""
        data = (case_no,)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def getPublishedAt(cls, pointType: str):
        botDB, DBCursor = cls.connection()
        query =  """select publishedAt
                    from Points
                    where type = %s"""
        data = (pointType,)
        DBCursor.execute(query, data)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updatePublishedAt(cls, publishedAt: str, pointType: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE Points
                SET publishedAt=%s
                WHERE type=%s"""
        data = (publishedAt, pointType)
        DBCursor.execute(query, data)
        botDB.commit()