import os,sys
from dotenv import load_dotenv

#Game import
#import mysql.connector
import oracledb

if str(sys.platform).startswith('win'):
    print('Windows local test begin')
    oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_6")
#else:
    #cx_Oracle.init_oracle_client(config_dir="/home/ubuntu/Wallet_benai")
    


load_dotenv()
dsnStr = os.getenv('DSNSTR')
#host = os.getenv('HOST')
user = os.getenv('ORACLE_DB_USER') #os.getenv('DBUSER')
password = os.getenv('ORACLE_DB_PASSWORD') #os.getenv('DBPW')
#database = os.getenv('DATABASE')

class DBConnection:
    #botDB = mysql.connector.connect(host=host, user=user,
                                    #password=password, database=database)
    botDB = oracledb.connect(user=user, password=password,
                               dsn=dsnStr)

    @classmethod
    def connection(cls):
        #if DBConnection.botDB.is_connected():
        try:
            if DBConnection.botDB.ping() is None:
                pass
            else:
                raise ValueError('DB connection is not alive')
        #else:
        except Exception as e:
            print('DB connection is not alive')
            DBConnection.botDB = oracledb.connect(user=user, password=password,
                               dsn=dsnStr)
        finally:
            DBCursor = DBConnection.botDB.cursor()
            return (DBConnection.botDB, DBCursor)

    @classmethod
    def fetchUserData(cls, dataType: str, userID: str):
        botDB, DBCursor = cls.connection()
        vals = (userID, )
        sqlQuery = 'select * from userData where userID = :1'
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
        sqlQuery = 'select mcName from userData where userID = :1'
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
        sqlQuery = 'update userData set userBalance = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserWin(cls, userID: str, win: int):
        botDB, DBCursor = cls.connection()
        vals = (win, userID)
        sqlQuery = 'update userData set userWin = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserSortPref(cls, userID: str, sortPref: str):
        botDB, DBCursor = cls.connection()
        vals = (sortPref, userID)
        sqlQuery = 'update userData set sortPref = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserHandColor(cls, userID: str, color: str):
        botDB, DBCursor = cls.connection()
        vals = (color, userID)
        sqlQuery = 'update userData set colorPref = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserMcName(cls, userID: str, mcName: str):
        botDB, DBCursor = cls.connection()
        vals = (mcName, userID)
        sqlQuery = 'update userData set mcName = :1 where userID = :1'
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
                VALUES (:1, :1, :1, :1, :1) """
        dataTuple = (userID, 10000, "#00ff00", 'd', 0)
        DBCursor.execute(query, dataTuple)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def createServer(cls, id: str, pw: str, game: str, port: str, remarks: str):
        botDB, DBCursor = cls.connection()
        query = """INSERT INTO serverlist (id, pw, game, port, remarks) 
                VALUES (:1, :1, :1, :1, :1) """
        dataTuple = (id, pw, game, port, remarks)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def updateServer(cls, id: str, pw: str, game: str, port: str, remarks: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE serverlist
                SET pw=:1, game=:1, port=:1, remarks=:1
                WHERE id=:1 """
        dataTuple = (pw, game, port, remarks, id)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def updateServerPw(cls, id: str, pw: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE serverlist
                SET pw=:1
                WHERE id=:1 """
        dataTuple = (pw, id)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def deleteServer(cls, id: str):
        botDB, DBCursor = cls.connection()
        query = """DELETE FROM serverlist
                WHERE id=:1 """
        data = (id,)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def selectServer(cls, id: str):
        botDB, DBCursor = cls.connection()
        vals = (id, )
        sqlQuery = """SELECT id, pw, game, port, remarks
                FROM serverlist
                WHERE id = :1"""
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
        sqlQuery = 'select case_no from CovLocate fetch first 1 row only'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updateCaseNo(cls, case_no: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE CovLocate
                SET case_no=:1"""
        data = (case_no,)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def getPublishedAt(cls, pointType: str):
        botDB, DBCursor = cls.connection()
        query =  """select publishedAt
                    from Points
                    where type = :1"""
        data = (pointType,)
        DBCursor.execute(query, data)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updatePublishedAt(cls, publishedAt: str, pointType: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE Points
                SET publishedAt=:1
                WHERE type=:1"""
        data = (publishedAt, pointType)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def insertLol(cls, region: str, remarks: str):
        botDB, DBCursor = cls.connection()
        query = """INSERT INTO Points (type, remarks) 
                VALUES (:1, :1) """
        dataTuple = (region, remarks)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def deleteLol(cls, region: str, remarks: str):
        botDB, DBCursor = cls.connection()
        query = """DELETE FROM Points
                WHERE type=:1 and remarks=:1 """
        data = (region,remarks)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def getLolPublishedAt(cls, region: str, remarks: str):
        botDB, DBCursor = cls.connection()
        query =  """select publishedAt
                    from Points
                    where type = :1 and remarks = :1"""
        data = (region,remarks)
        DBCursor.execute(query, data)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updateLolPublishedAt(cls, region: str, publishedAt: str, remarks: str):
        botDB, DBCursor = cls.connection()
        query = """UPDATE Points
                SET publishedAt=:1
                WHERE type=:1 and remarks = :1"""
        data = (publishedAt, region, remarks)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def getLolSummonerNames(cls, region: str):
        botDB, DBCursor = cls.connection()
        query =  """select remarks
                    from Points
                    where type = :1"""
        data = (region,)
        DBCursor.execute(query, data)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def getRemarks(cls, type: str, active: str):
        botDB, DBCursor = cls.connection()
        query =  """select remarks
                    from Points
                    where type = :1 and active = :1"""
        data = (type,active)
        DBCursor.execute(query, data)
        result = DBCursor.fetchall()
        return result