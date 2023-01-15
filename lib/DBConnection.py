import os,sys
from dotenv import load_dotenv

#Game import
#import mysql.connector
import oracledb

global enable_db
enable_db = True

if enable_db:
    
    if str(sys.platform).startswith('win'):
        print('Windows local test begin')
        oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_6")
    else:
        # pyoracleclient (removed from requirements.txt)
        '''import pyoracleclient as pyoc
        pyoc.get_client(version='21.8.0.0.0', sys='linux', url=None)
        load_dotenv()
        pyoc.add_custom_tns(os.getenv('DSNSTR'))'''
        
        oracledb.init_oracle_client(lib_dir=r"/home/oracle/instantclient_21_6", config_dir=r"/home/Wallet_benai")
        


    load_dotenv()
    dsnStr = os.getenv('DSNSTR')
    #host = os.getenv('HOST')
    user = os.getenv('ORACLE_DB_USER') #os.getenv('DBUSER')
    password = os.getenv('ORACLE_DB_PASSWORD') #os.getenv('DBPW')
    #database = os.getenv('DATABASE')

class DBDisabled(Exception):
    pass

class DBConnection:
    if enable_db:
        #botDB = mysql.connector.connect(host=host, user=user,
                                        #password=password, database=database)
        botDB = oracledb.connect(user=user, password=password,
                                dsn=dsnStr)
        #botDB = oracledb.SessionPool(user=user, password=password,
                                #dsn=dsnStr, min=5, max=5, increment=0)

    @classmethod
    def enableDBOrElseRaise(cls):
        if not enable_db:
            raise DBDisabled("DB connection is disabled.")

    '''@classmethod
    def connection(cls):
        cls.enableDBOrElseRaise()
        #if DBConnection.botDB.is_connected():
        connection = None
        try:
            connection = DBConnection.botDB.acquire() #DBConnection.botDB.is_healthy(): #DBConnection.botDB.ping() is None:
            if connection is None:
                raise
        #else:
        except Exception as e:
            print('DB connection is not alive')
            try:
                DBConnection.botDB = oracledb.SessionPool(user=user, password=password,
                                dsn=dsnStr, min=10, max=10, increment=0)
                connection = DBConnection.botDB.acquire()
            except Exception as e:
                print('DB connection is not alive, second attempt failed, abort')
                return
        finally:
            return (connection, connection.cursor())'''
        
    @classmethod
    def connection(cls):
        cls.enableDBOrElseRaise()
        #if DBConnection.botDB.is_connected():
        connection = DBConnection.botDB
        try:
            #DBConnection.botDB.is_healthy(): 
            connection.ping()
        #else:
        except Exception as e:
            print('DB connection is not alive')
            try:
                DBConnection.botDB = oracledb.connect(user=user, password=password,
                                dsn=dsnStr)
                connection = DBConnection.botDB
            except Exception as e:
                print('DB connection is not alive, second attempt failed, abort')
                return
        finally:
            return (connection, connection.cursor())

    @classmethod
    def fetchUserData(cls, dataType: str, userID: str):
        cls.enableDBOrElseRaise()
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
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        vals = (userID, )
        sqlQuery = 'select mcName from userData where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        result = DBCursor.fetchone()
        return result

    @classmethod
    def fetchAllRankData(cls):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        sqlQuery = 'select userID, userWin from userData order by userWin desc'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        #DBCursor.close()
        #botDB.close()
        return result

    @classmethod
    def fetchAllMoneyData(cls):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        sqlQuery = 'select userID, userBalance from userData order by userBalance desc'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updateUserBalance(cls, userID: str, balance: int):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        vals = (balance, userID)
        sqlQuery = 'update userData set userBalance = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserWin(cls, userID: str, win: int):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        vals = (win, userID)
        sqlQuery = 'update userData set userWin = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserSortPref(cls, userID: str, sortPref: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        vals = (sortPref, userID)
        sqlQuery = 'update userData set sortPref = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserHandColor(cls, userID: str, color: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        vals = (color, userID)
        sqlQuery = 'update userData set colorPref = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()
        #DBCursor.close()
        #botDB.close()

    @classmethod
    def updateUserMcName(cls, userID: str, mcName: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        vals = (mcName, userID)
        sqlQuery = 'update userData set mcName = :1 where userID = :1'
        DBCursor.execute(sqlQuery, vals)
        botDB.commit()

    @classmethod
    def checkUserInDB(cls, userID: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        DBCursor.execute("select * from userData where userID = " + userID)
        result = DBCursor.fetchall()
        #DBCursor.close()
        #botDB.close()
        return len(result) != 0

    @classmethod
    def addUserToDB(cls, userID: str):
        cls.enableDBOrElseRaise()
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
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """INSERT INTO serverlist (id, pw, game, port, remarks) 
                VALUES (:1, :1, :1, :1, :1) """
        dataTuple = (id, pw, game, port, remarks)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def updateServer(cls, id: str, pw: str, game: str, port: str, remarks: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """UPDATE serverlist
                SET pw=:1, game=:1, port=:1, remarks=:1
                WHERE id=:1 """
        dataTuple = (pw, game, port, remarks, id)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def updateServerPw(cls, id: str, pw: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """UPDATE serverlist
                SET pw=:1
                WHERE id=:1 """
        dataTuple = (pw, id)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def deleteServer(cls, id: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """DELETE FROM serverlist
                WHERE id=:1 """
        data = (id,)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def selectServer(cls, id: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        vals = (id, )
        sqlQuery = """SELECT id, pw, game, port, remarks
                FROM serverlist
                WHERE id = :1"""
        DBCursor.execute(sqlQuery, vals)
        return DBCursor.fetchone()

    @classmethod
    def selectAllServer(cls):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        sqlQuery = 'select id, pw, game, port, remarks from serverlist order by game, remarks'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def getCaseNo(cls):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        sqlQuery = 'select case_no from CovLocate fetch first 1 row only'
        DBCursor.execute(sqlQuery)
        result = DBCursor.fetchall()
        return result

    @classmethod
    def updateCaseNo(cls, case_no: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """UPDATE CovLocate
                SET case_no=:1"""
        data = (case_no,)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def getPublishedAt(cls, pointType: str):
        cls.enableDBOrElseRaise()
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
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """UPDATE Points
                SET publishedAt=:1
                WHERE type=:1"""
        data = (publishedAt, pointType)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def insertLol(cls, region: str, remarks: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """INSERT INTO Points (type, remarks) 
                VALUES (:1, :1) """
        dataTuple = (region, remarks)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    @classmethod
    def deleteLol(cls, region: str, remarks: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """DELETE FROM Points
                WHERE type=:1 and remarks=:1 """
        data = (region,remarks)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def getLolPublishedAt(cls, region: str, remarks: str):
        cls.enableDBOrElseRaise()
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
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """UPDATE Points
                SET publishedAt=:1
                WHERE type=:1 and remarks = :1"""
        data = (publishedAt, region, remarks)
        DBCursor.execute(query, data)
        botDB.commit()

    @classmethod
    def getLolSummonerNames(cls, region: str):
        cls.enableDBOrElseRaise()
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
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query =  """select remarks
                    from Points
                    where type = :1 and active = :1"""
        data = (type,active)
        DBCursor.execute(query, data)
        result = DBCursor.fetchall()
        return result

    # create playlist with playlist_name and userid across 2 tables
    @classmethod
    def createPlaylist(cls, userid: str, playlist_name: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()

        # insert into playlist
        query = """INSERT INTO playlist (playlist_name, owner_user_id) 
                VALUES (:1, :1) """
        dataTuple = (playlist_name,userid)
        DBCursor.execute(query, dataTuple)

        # get playlist id
        query =  """select playlist_id
                    from playlist
                    where playlist_name = :1"""
        data = (playlist_name,)
        DBCursor.execute(query, data)
        playlist_id = DBCursor.fetchall()[0][0]

        # insert into user_music_playlist
        query = """INSERT INTO user_music_playlist (userid, playlist_id) 
                VALUES (:1, :1) """
        dataTuple = (userid, playlist_id)
        DBCursor.execute(query, dataTuple)

        botDB.commit()

    # get playlist id and check if user owns it
    # get playlist
    @classmethod
    def getPlaylistAndCheckIfUserOwns(cls, userid: str, playlist_id: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query =  """select p.playlist_name
                    from user_music_playlist ump
                    inner join playlist p on ump.playlist_id = p.playlist_id and p.playlist_id = :1 and p.owner_user_id = :1
                    where ump.userid = :1"""
        data = (playlist_id, userid, userid)
        DBCursor.execute(query, data)
        return DBCursor.fetchall()

    # get playlist
    @classmethod
    def getPlaylist(cls, userid: str = None, playlist_id: int = None):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()

        # get all playlist globally
        if userid is None and playlist_id is None:
            query =  """select *
                        from playlist
                        order by playlist_id"""
            DBCursor.execute(query)
            return DBCursor.fetchall()

        # get all playlist of specific user
        elif userid is not None and playlist_id is None:
            query =  """select p.*
                        from user_music_playlist ump
                        inner join playlist p on ump.playlist_id = p.playlist_id
                        where userid = :1
                        order by p.playlist_id"""
            data = (userid,)
            DBCursor.execute(query, data)
            return DBCursor.fetchall()
        
        elif userid is None and playlist_id is not None:
            query =  """select mp.*, p.playlist_name, p.owner_user_id
                        from user_music_playlist ump
                        inner join playlist p on ump.playlist_id = p.playlist_id and p.playlist_id = :1
                        inner join music_playlist mp on mp.playlist_id = p.playlist_id
                        order by mp.id"""
            data = (playlist_id,)
            DBCursor.execute(query, data)
            return DBCursor.fetchall()

        else:
            query =  """select mp.*, p.playlist_name, p.owner_user_id
                        from user_music_playlist ump
                        inner join playlist p on ump.playlist_id = p.playlist_id and p.playlist_id = :1
                        inner join music_playlist mp on mp.playlist_id = p.playlist_id
                        where userid = :1
                        order by mp.id"""
            data = (playlist_id, userid)
            DBCursor.execute(query, data)
            return DBCursor.fetchall()

    # insert music into existing playlist
    @classmethod
    def insertPlaylist(cls, playlist_id: int, music_name: str, music_uploader: str, video_id: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query = """INSERT INTO music_playlist (playlist_id, music_name, music_uploader, video_id) 
                VALUES (:1, :1, :1, :1) """
        dataTuple = (playlist_id, music_name, music_uploader, video_id)
        DBCursor.execute(query, dataTuple)
        botDB.commit()

    # delete owning playlist
    @classmethod
    def deletePlaylist(cls, playlist_id: int):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()

        query = """DELETE FROM user_music_playlist
                WHERE playlist_id=:1 """
        data = (playlist_id,)
        DBCursor.execute(query, data)

        query = """DELETE FROM music_playlist
                WHERE playlist_id=:1 """
        data = (playlist_id,)
        DBCursor.execute(query, data)

        query = """DELETE FROM playlist
                WHERE playlist_id=:1 """
        data = (playlist_id,)
        DBCursor.execute(query, data)

        botDB.commit()
        
    # delete music from owning playlist
    @classmethod
    def deleteMusicFromPlaylist(cls, playlist_id: int, music_id: int):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        
        query =  """select music_name
                    from music_playlist
                    where id = :1"""
        data = (music_id,)
        DBCursor.execute(query, data)
        music_name = DBCursor.fetchall()

        query = """DELETE FROM music_playlist
                WHERE playlist_id=:1 and id=:1"""
        data = (playlist_id,music_id)
        DBCursor.execute(query, data)

        botDB.commit()
        
        return music_name
    
    # update owning playlist name
    @classmethod
    def updateMyPlaylistName(cls, playlist_id: int, playlist_new_name: str):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()

        query = """UPDATE playlist
                SET playlist_name = :1
                WHERE playlist_id=:1"""
        data = (playlist_new_name,playlist_id)
        DBCursor.execute(query, data)

        botDB.commit()
        
        return playlist_new_name
    
    # TODO
    @classmethod
    def selectAllPlaylistId(cls):
        cls.enableDBOrElseRaise()
        botDB, DBCursor = cls.connection()
        query =  """select playlist_id
                    from playlist
                    order by playlist_id"""
        DBCursor.execute(query)
        playlist_ids = DBCursor.fetchall()
        return playlist_ids