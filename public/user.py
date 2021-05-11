from flask import session
import string
from public import db
from util.hash import rsa_decrypt, getHash
from random import Random
import time
from datetime import datetime


def checkedToken(token):
    query = "select * from LoginStatus where token='{}'".format(token)
    conn = db.get_db()
    c = conn.cursor()
    try:
        token_data = c.execute(query).fetchone()
    except IOError:
        return False
        conn.close()
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
        return None
        conn.close()
    if token_data is None:
        return None
    userId = token_data['userId']
    try:
        userInfo = c.execute("select * from User where id='{}'".format(userId)).fetchone()
    except:
        db.close_db()
        return None
    db.close_db()
    user = UserModel()
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
        return 0
        conn.close()
    if userInfo is None:
        return 101
    if userInfo['pwd'] != password:
        return 102

    token = getToken()

    query2 = "select * from LoginStatus where userId={}".format(userInfo['id'])
    try:
        res = c.execute(query2).fetchone()
        if res is not None:
            update_sql = "UPDATE LoginStatus SET token='{}',loginTime='{}' WHERE userId='{}'".format(token,
                                                                                                     time.strftime(
                                                                                                         "%Y-%m-%d %H:%M:%S",
                                                                                                         time.localtime()),
                                                                                                     int(userInfo[
                                                                                                             'id']))
            c.execute(update_sql)
            conn.commit()
            return token
        query_insert = 'INSERT INTO LoginStatus VALUES ("{}","{}","{}")'.format(token, int(userInfo['id']),
                                                                                time.strftime("%Y-%m-%d %H:%M:%S",
                                                                                              time.localtime()))
        c.execute(query_insert)
        conn.commit()

    except IOError:
        conn.close()
    conn.close()
    return token


def userLogout(token):
    conn = db.get_db()
    c = conn.cursor()
    try:
        c.execute("delete from LoginStatus where token='{}'".format(token))
        print("删除成功")
        conn.commit()
    except IOError:
        db.close_db()
    db.close_db()
    return 1


def UpdateUserInfo(token, updateUser):
    user = getUserInfo(token)
    user.updateUser(updateUser)

    conn = db.get_db()
    c = conn.cursor()
    try:
        query = "UPDATE User SET username='{}', info='{}' WHERE id='{}'".format(user.username, user.info, user.userId)
        c.execute(query)
        conn.commit()
        db.close_db()
        return user
    except IOError:
        db.close_db()
        return None


def UserResiger(username, password):
    return 1


class UserModel:
    username = ''
    userId = ''
    password = ''
    info = ''

    def __init__(self):
        pass

    def setPassword(self, password):
        self.password = getHash(rsa_decrypt(session['privatekey'], password).decode()[1:-1])

    def getUserInfoFromDB(self, user):
        self.username = user['username']
        self.info = user['info']
        self.password = user['pwd']
        self.userId = user['id']

    def getUserVo(self):
        return {'username': self.username, 'userId': self.userId, 'info': self.info}

    def updateUser(self, newUser):
        self.username = newUser.username if newUser.username is not '' else self.username
        self.info = newUser.info if newUser.info is not '' else self.info
        self.password = newUser.password if newUser.password is not '' else self.password


if __name__ == '__main__':
    print(checkedToken("9aa0eda3d5d06c9"))
