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


def getToken():
    random = Random()
    My_List = []
    for i in range(16):
        Method = random.choice(string.ascii_lowercase + string.digits)
        My_List.append(Method)
    return getHash("".join(My_List))[:15]


def userLogin(username, password):
    # password = getHash(rsa_decrypt(session['privatekey'], password).decode())

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


def UserResiger(username, password):
    return 1


if __name__ == '__main__':
    print(checkedToken("9aa0eda3d5d06c9"))
