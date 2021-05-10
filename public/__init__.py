# -*- coding: utf-8 -*-
import requests
from flask import Flask, url_for, abort
from flask import render_template, request, redirect, session

import os
import json

from public.user import checkedToken, userLogin, userLogout
from util.hash import generate_key
from util.imageCode import getImgCode
from util.result import ApiResult
from util.page import getPage
from util.lda import getidbyinfo


def create_app():
    app = Flask(__name__)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "classification.db")
    app.config.from_mapping(
        SECRETE_KEY='123456',
        DATABASE=db_path
    )
    # existing code omitted

    app.config["SECRET_KEY"] = 'TPmi4aLWRbyVq8zu9v82dWYW1'

    from . import db
    db.init_app(app)

    @app.errorhandler(404)
    def error(e):
        # return render_template('exception/404.html')
        return render_template('404.html')

    # 拦截器入口
    @app.before_request
    def before_login():
        token = request.args.get("token")

        if token is None:
            try:
                token = session['token']
                print(token)
            except KeyError:
                print(error)
        else:
            session['token'] =token

        if request.path == "/":
            return render_template('login.html')

        # 未登录允许的url入口

        login_url = ["/register", "/login",  "/static", "/imgCode","/test"]

        # 合法的url入口
        allow_url = ["/logout" , "/classify", "/classification", "/myinfo", "/api", "/add", "/manage", "/index"]

        for url in login_url:
            if request.path.startswith(url):
                return None

        for url in allow_url:
            if request.path.startswith(url):
                if not checkedToken(token):
                    return render_template('login.html')
                else:
                    return None
            continue
        abort(404)

        if checkedToken(token):
            return render_template('login.html')

    @app.route('/')
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        if request.method == 'POST':
            username = request.json.get('username')
            password = request.json.get('password')
            # code = request.json.get("code")
            # if not code == session['imageCode']:
            #     return ApiResult('').fault("验证码错误")
            # print(password)
            token = userLogin(username, password)
            session['token'] = token
            if token in [0, 101, 102]:
                return ApiResult('').fault("用户名和密码不正确")
            if token is None:
                return ApiResult().fault("登录失败")

            return ApiResult({"token": token}).success("登录成功")

    @app.route('/api/getpublicKey', methods=["GET"])
    def getPublickey():
        privatekey, publickey = generate_key()
        session['privatekey'] = privatekey
        print(session['privatekey'])
        return ApiResult({'publickey': publickey}).success("")

    @app.route('/logout', methods=['GET'])
    def logout():
        token = session['token']
        userLogout(token)
        session.pop('token')
        return ApiResult('').success("登出成功")

    @app.route('/imgCode')
    def imgCode():
        return getImgCode()

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('register.html')

    @app.route('/index')
    @app.route('/manage')
    def manage():
        return render_template('/manage.html')

    @app.route('/add', methods=['GET', 'POST'])
    def add():
        if request.method == 'GET':
            return render_template('add.html')
        elif request.method == 'POST':
            servname = request.json.get('servname')
            servtype = request.json.get('type')
            servinfo = request.json.get('info')
            serventrance = request.json.get('serventrance')
            print(servname, servtype, servinfo, serventrance)
            conn = db.get_db()
            c = conn.cursor()
            try:
                query = "INSERT INTO Serv (servname, servtype, servinfo, serventrance) VALUES ('{}','{}','{}','{}')".format(
                    servname, servtype, servinfo, serventrance)
                c.execute(query)
                conn.commit()
                db.close_db()
                return ApiResult('').success('提交成功')
            except:
                db.close_db()
                return ApiResult('').fault('提交失败')

    @app.route('/classify', methods=['GET', 'POST'])
    def classify():
        if request.method == 'POST':
            name = request.form['name']
            age = request.form['age']
            retdict = {'name': name, 'age': age}
            retjson = json.dumps(retdict)
            print(retjson)
            return render_template('classify.html', name=name, age=age)
        else:
            return render_template('classify.html')

    @app.route('/api/selectdatabytag')
    def selectDatabyTag():
        tag = request.args.get("tag")
        page = request.args.get("page")
        limit = request.args.get("limit")
        res = []  # 结果服务字典列表
        # json源
        #
        # with open("public/static/service.json", "r", encoding="utf-8") as isfile:
        #     f_json = json.loads(isfile.read())
        #     if tag is None or tag == '':
        #         return ApiResult({"count": len(f_json['data']), "data": getPage(f_json['data'], page, limit)})\
        #             .success("请求成功")
        #     for data in f_json['data']:
        #         if data['type'] == tag:
        #             res.append(data)
        #
        # db源
        conn = db.get_db()
        c = conn.cursor()
        query = "SELECT * FROM Serv"
        servs = c.execute(query).fetchall()
        for serv in servs:
            if tag is None or tag == '' or serv[2] == tag:
                res.append({
                    "id": serv[0],
                    "name": serv[1],
                    "type": serv[2],
                    "info": serv[3],
                    "entrance": serv[4]
                })
        db.close_db()
        return ApiResult({"count": len(res), "data": getPage(res, page, limit)}).success("请求成功")

    @app.route('/api/selectdatabyinfo')
    def selectDatabyInfo():
        info = request.args.get("info")
        page = request.args.get("page")
        limit = request.args.get("limit")
        resultlist = getidbyinfo(info)
        res = []

        # json源
        # with open("public/static/service.json", "r", encoding="utf-8") as isfile:
        #     f_json = json.loads(isfile.read())
        #     if info is None or info == '':
        #         return ApiResult({"count": len(f_json['data']), "data": getPage(f_json['data'], page, limit)})\
        #             .success("请求成功")
        #     for data in f_json['data']:
        #         if data['id'] in resultlist:
        #             res.append(data)
        #
        # db源
        conn = db.get_db()
        c = conn.cursor()
        query = "SELECT * FROM Serv"
        servs = c.execute(query).fetchall()
        for serv in servs:
            if info is None or info == '' or serv[0] in resultlist:
                res.append({
                    "id": serv[0],
                    "name": serv[1],
                    "type": serv[2],
                    "info": serv[3],
                    "entrance": serv[4]
                })
        db.close_db()
        return ApiResult({"count": len(res), "data": getPage(res, page, limit)}).success("请求成功")

    @app.route('/classification')
    def classification():
        return render_template('classification.html')

    @app.route('/myinfo')
    def myinfo():
        return render_template('myinfo.html')

    @app.route('/test', methods=['GET', 'POST'])
    def test():
        print(checkedToken("9aa0eda3d5d06c9"))
        return '1'

    '''
    # 测试输出
    with app.test_request_context():
        print(url_for('manage'))
        print(url_for('login'))
        print(url_for('static', filename='login.css'))
        # print(url_for('check'))
        print(app.instance_path)
    '''
    return app
