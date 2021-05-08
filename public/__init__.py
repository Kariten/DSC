# -*- coding: utf-8 -*-
from flask import Flask, url_for
from flask import render_template, request, redirect, session

import os
import json
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

    from . import db
    db.init_app(app)

    @app.route('/')
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        if request.method == 'POST':
            if request.form.get('username') == '':
                session['user'] = request.form.get('username')
                return redirect('/')

    @app.route('/index')
    @app.route('/manage')
    def manage():
        return render_template('/manage.html')

    @app.route('/add')
    def add():
        return render_template('add.html')

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

    @app.route('/selectdatabytag')
    def selectDatabyTag():
        tag = request.args.get("tag")
        page = request.args.get("page")
        limit = request.args.get("limit")
        res = [] # 结果服务字典列表
        # json源
        '''
        with open("public/static/service.json", "r", encoding="utf-8") as isfile:
            f_json = json.loads(isfile.read())
            if tag is None or tag == '':
                return ApiResult({"count": len(f_json['data']), "data": getPage(f_json['data'], page, limit)}).success(
                    "请求成功")
            for data in f_json['data']:
                if data['type'] == tag:
                    res.append(data)
        '''
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

        return ApiResult({"count": len(res), "data": getPage(res, page, limit)}).success("请求成功")
        

    @app.route('/selectdatabyinfo')
    def selectDatabyInfo():
        info = request.args.get("info")
        page = request.args.get("page")
        limit = request.args.get("limit")
        resultlist = getidbyinfo(info)
        res = []
        '''
        # json源
        with open("public/static/service.json", "r", encoding="utf-8") as isfile:
            f_json = json.loads(isfile.read())
            if info is None or info == '':
                return ApiResult({"count": len(f_json['data']), "data": getPage(f_json['data'], page, limit)}).success(
                    "请求成功")
            for data in f_json['data']:
                if data['id'] in resultlist:
                    res.append(data)
        '''
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

        return ApiResult({"count": len(res), "data": getPage(res, page, limit)}).success("请求成功")


    @app.route('/classification')
    def classification():
        return render_template('classification.html')

    @app.route('/myinfo')
    def myinfo():
        return render_template('myinfo.html')
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
