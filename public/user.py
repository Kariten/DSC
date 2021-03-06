from flask import session
import string
from public import db
from util.hash import rsa_decrypt, getHash
from random import Random
import time
from datetime import datetime


def checkedUserName(userName):
    query = "select * from User where username='{}'".format(userName)
    conn = db.get_db()
    c = conn.cursor()
    try:
        userInfo = c.execute(query).fetchone()
    except:
        return False
    if userInfo is None:
        return False
    return True


def checkedToken(token):
    query = "select * from LoginStatus where token='{}'".format(token)
    conn = db.get_db()
    c = conn.cursor()
    try:
        token_data = c.execute(query).fetchone()
    except IOError:
        conn.close()
        return False
    if token_data is None:
        return False
    time_1_struct = datetime.now()
    time_2_struct = datetime.strptime(token_data['LoginTime'], "%Y-%m-%d %H:%M:%S")

    seconds = (time_1_struct - time_2_struct).seconds

    if seconds <= 3600:
        return True

    try:
        c.execute("delete from LoginStatus where token='{}'".format(token))
        conn.commit()
    except IOError:
        db.close_db()
    db.close_db()
    return False


def getUserInfo(token):
    query = "select * from LoginStatus where token='{}'".format(token)
    conn = db.get_db()
    c = conn.cursor()
    try:
        token_data = c.execute(query).fetchone()
    except:
        conn.close()
        return None
    if token_data is None:
        return None
    userId = token_data['userId']

    try:
        userService = c.execute("select * from UserType where userid='{}'".format(userId)).fetchall()
    except:
        db.close_db()
        return None

    try:
        userInfo = c.execute("select * from User where id='{}'".format(userId)).fetchone()
    except:
        db.close_db()
        return None
    db.close_db()
    user = UserModel()
    serviceList = []
    for i in userService:
        serviceList.append(i['typeid'])
    user.setService(serviceList)
    user.getUserInfoFromDB(userInfo)
    return user


def getToken():
    random = Random()
    My_List = []
    for i in range(16):
        Method = random.choice(string.ascii_lowercase + string.digits)
        My_List.append(Method)
    return getHash("".join(My_List))[:15]


def userLogin(username, password):
    password = getHash(rsa_decrypt(session['privatekey'], password).decode()[1:-1])
    conn = db.get_db()
    c = conn.cursor()
    query = "select * from User where username='{}'".format(username)

    try:
        userInfo = c.execute(query).fetchone()
    except:
        conn.close()
        return 0
    if userInfo is None:
        return 101
    if userInfo['pwd'] != password:
        return 102

    token = getToken()
    userid = str(userInfo['id'])
    query2 = "select * from LoginStatus where userId={}".format(userInfo['id'])
    try:
        res = c.execute(query2).fetchone()
        if res is not None:
            update_sql = "UPDATE LoginStatus SET token='{}',loginTime='{}' WHERE userId='{}'".format(token,
                                                                                                     time.strftime(
                                                                                                         "%Y-%m-%d "
                                                                                                         "%H:%M:%S",
                                                                                                         time.localtime()),
                                                                                                     int(userInfo[
                                                                                                             'id']))
            c.execute(update_sql)
            conn.commit()
            return token, userid
        query_insert = 'INSERT INTO LoginStatus VALUES ("{}","{}","{}")'.format(token, int(userInfo['id']),
                                                                                time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                              time.localtime()))
        c.execute(query_insert)
        conn.commit()

    except IOError:
        conn.close()
    return token, userid


def userLogout(token):
    conn = db.get_db()
    c = conn.cursor()
    try:
        c.execute("delete from LoginStatus where token='{}'".format(token))
        print("????????????")
        conn.commit()
    except IOError:
        db.close_db()
    db.close_db()
    return 1


def updateService(service):
    userId = getUserInfo(session['token']).userId
    conn = db.get_db()
    c = conn.cursor()
    try:
        c.execute("delete from UserType where userid='{}'".format(userId))
        conn.commit()
    except TypeError:
        db.close_db()
        return None
    try:
        for i in service:
            query = "INSERT INTO UserType(userid, typeid) VALUES({}, {})".format(int(userId), int(i))
            c.execute(query)
        conn.commit()
        db.close_db()
    except TypeError:
        conn.rollback()
        db.close_db()
        return None
    return 1


def UpdateUserInfo(token, updateUser):
    user = getUserInfo(token)

    if checkedUserName(updateUser.username):
        if user.username != updateUser.username:
            return "???????????????"
    print(updateUser.password)
    user.updateUser(updateUser)
    print(user.password)

    conn = db.get_db()
    c = conn.cursor()
    try:
        query = "UPDATE User SET username='{}', info='{}', lable='{}',pwd='{}' WHERE id='{}'".format(user.username, user.info, user.lable, user.password, user.userId)
        c.execute(query)
        conn.commit()
        db.close_db()
        return user
    except IOError:
        db.close_db()
        return None


def UserResiger(user):
    if checkedUserName(user.username):
        return "???????????????"
    conn = db.get_db()
    c = conn.cursor()
    try:
        query = 'INSERT INTO User (username,pwd) VALUES ("{}","{}")'.format(user.username, user.password)
        c.execute(query)
        conn.commit()
        query = "SELECT * FROM User WHERE username='{}'".format(user.username)
        user = UserModel()
        user.getUserInfoFromDB(c.execute(query).fetchone())
        db.close_db()
        return user
    except IOError:
        db.close_db()
        return None



class UserModel:
    username = ''
    userId = ''
    password = ''
    lable = ''
    info = ''
    service = {}

    def __init__(self):
        pass

    def setPassword(self, password):
        if rsa_decrypt(session['privatekey'], password).decode()[1:-1] is not '':
            self.password = getHash(rsa_decrypt(session['privatekey'], password).decode()[1:-1])

    def getUserInfoFromDB(self, user):
        self.username = user['username']
        self.info = user['info']
        self.lable = user['lable']
        self.password = user['pwd']
        self.userId = user['id']

    def getUserVo(self):
        return {'username': self.username, 'userId': self.userId, 'info': self.info, 'lable': self.lable, 'service': self.service}

    def updateUser(self, newUser):
        self.username = newUser.username if newUser.username is not '' else self.username
        self.info = newUser.info if newUser.info is not '' else self.info
        self.lable = newUser.lable if newUser.lable is not '' else self.lable
        self.password = newUser.password if newUser.password is not '' else self.password

    def setService(self, data):
        self.service = {}
        for i in data:
            self.service['{}'.format(str(i))] = "on"
