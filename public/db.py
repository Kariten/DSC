import sqlite3
import sys
import click
import json
from flask import current_app, g
from flask.cli import with_appcontext

# 为flask提供数据库连接
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# 为main内代码提供数据库连接
def getdb():
    conn = sqlite3.connect('public/classification.db',detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def resetServ():
    conn = getdb()
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS Serv")
    conn.commit()
    c.execute('''
    CREATE TABLE Serv(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        servname TEXT UNIQUE NOT NULL,
        servtype TEXT NOT NULL,
        servinfo TEXT,
        serventrance TEXT
    )
    ''')
    conn.commit()
    with open("public/static/service.json",'r',encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
        # print(load_dict)
    load_dict['smallberg'] = [8200,{1:[['Python',81],['shirt',300]]}]
    # print(load_dict)
    # print(type(load_dict['data'][0]))
    for serv in load_dict['data']:
        query = 'INSERT INTO Serv VALUES ({id},"{name}","{type}","{info}","{entrance}")'.format(**serv)
        print(query)
        c.execute(query)
        conn.commit()
    conn.close()

def showServ():
    conn = getdb()
    c = conn.cursor()
    cursor = c.execute("SELECT * from Serv").fetchall()
    print(type(cursor[0]))
    for row in cursor:
        for item in row:
            print(item)
        print()
    conn.close()

def resetUser():
    conn = getdb()
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS User")
    conn.commit()
    c.execute('''
    CREATE TABLE User(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        pwd TEXT NOT NULL,
        info TEXT
    )
    ''')
    users = [
        {
            'id':0,
            'username':"admin",
            'pwd':"123456",
            'info':"大数据 云计算 服务器"
        },
        {
            'id':1,
            'username':"guest",
            'pwd':"123456",
            'info':"安全 备份 分布式"
        }
    ]
    for user in users:
        query = 'INSERT INTO User VALUES ({id},"{username}","{pwd}","{info}")'.format(**user)
        print(query)
        c.execute(query)
        conn.commit()
    conn.close()

if __name__ == "__main__":

    if sys.argv == 'reset':
        resetServ()
        resetUser()