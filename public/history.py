from datetime import datetime

from public import db
from collections import Counter


def getFreqTimesByUserId(userId):
    conn = db.get_db()
    c = conn.cursor()
    try:
        query = "select * from HistoryRecored where userId={} and recordType={}}".format(userId, 1)
        records = c.execute(query).fetchall()
        conn.commit()
    except IOError:
        conn.rollback()
        db.close_db()
        return None

    try:
        query = "select * from Serv"
        servList = c.execute(query).fetchall()
        conn.commit()
        db.close_db()
    except IOError:
        conn.rollback()
        db.close_db()
        return None
    indexMap = {}
    for i in servList:
        indexMap[i['servname']] = i['id']

    resList = []
    for record in records:
        resList.append(indexMap[record["recordName"]])
    return Counter(resList)


def getRecordByUserId(userId):
    conn = db.get_db()
    c = conn.cursor()
    try:
        query = "select * from HistoryRecored where userId={}".format(userId)
        records = c.execute(query).fetchall()
        conn.commit()
        db.close_db()
    except IOError:
        conn.rollback()
        db.close_db()
        return None

    resList = []
    for record in records:
        history = HistoryRecord(recordName=record['recordName'], recordUrl=record['visitedUrl'],
                                recordType=record['recordType'], userId=record['userId'])
        history.recordTime = record['visitedTime']
        resList.append(history)
    return resList


class HistoryRecord:
    recordName = ''
    recordUrl = ''
    recordType = 0
    userId = -1
    recordTime = ''

    def __init__(self, recordName, recordUrl, recordType, userId):
        self.userId = userId
        self.recordType = recordType
        self.recordUrl = recordUrl
        self.recordName = recordName
        pass

    def addRecord(self):
        conn = db.get_db()
        c = conn.cursor()
        self.recordTime = datetime.now()
        try:
            query = "INSERT INTO HistoryRecored(userid, recordName,visitedUrl,recordType,visitedTime) VALUES({}, {}," \
                    "{},{},{}})".format(self.userId, self.recordName, self.recordUrl, self.recordType, self.recordTime)
            c.execute(query)
            conn.commit()
            db.close_db()
        except IOError:
            conn.rollback()
            db.close_db()
            return None
        return 1
