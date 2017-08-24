''' REST sample '''
#!flask/bin/python
import sqlite3
import json
from cerberus import Validator
from contextlib import closing
from flask import Flask, jsonify, abort, make_response, url_for, g, request, session, redirect, abort, render_template, flash
from datetime import datetime, date
from pprint import pprint

# API version
VERSION = "v1.0"

# DB settings
DATABASE = 'apppost.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# building app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APPPOST_SETTINGS', silent=True)
CONTEXT_ROOT = "/todo/api/" + VERSION


def connect_db():
    """ connection作成用 """
    return sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_COLNAMES)


@app.before_request
def before_request():
    """ 【フレームワーク用】リクエスト受信時の初期化処理 """
    if getattr(g, 'gcnt', None) is not None:
        g.gcnt += 1
        g.scnt += 1
    else:
        g.gcnt = 0
        g.scnt = 0
    print("before %d  %d " % (g.gcnt, g.scnt))
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """ 【フレームワーク用】リクエスト終了時のお掃除処理 """
    db = getattr(g, 'db', None)
    gcnt = getattr(g, 'gcnt', None)
    scnt = getattr(g, 'scnt', None)
    print("tear %d  %d " % (gcnt, scnt))
    if db is not None:
        db.close()


@app.errorhandler(404)
def not_found(error):
    """ 【フレームワーク用】エラー時の処理 """
    return make_response(jsonify({'error': 'Not found'}), 404)


def select_for_object(query_string):
    """ 【共通処理】query_stringの実行結果をオブジェクト（連想配列）に変換して返す処理 """
    db = g.db
    cur = db.execute(query_string)
    column_names = [rec[0] for rec in cur.description]
    new_tasks = [
        {column_names[idx]:row[idx]
         for idx in range(len(column_names))
         } for row in cur.fetchall()]
    print(new_tasks)
    return new_tasks


def update_for_object(update_string):
    """ 【共通処理】updateの実行結果のカウント返す処理 """
    db = g.db
    cur = db.execute(update_string)
    print(new_tasks)
    return new_tasks


@app.route(CONTEXT_ROOT + '/tasks', methods=['GET'])
def get_tasks():
    """ 【API】全タスクリストを返却する """
    response = jsonify(select_for_object('select * from tasks'))
    return response


@app.route(CONTEXT_ROOT + '/tasks', methods=['POST'])
def add_tasks():
    """ 【API】タスクを追加する """

    # Validation Definition
    schema = {
        'end_date': {
            'type': 'date',
            'required': True,
            'empty': False,
        },
        'item': {
            'type': 'string',
            'required': True,
            'empty': False,
        }
    }

    # Create Validation Object
    v = Validator(schema)

    # Initialize response
    response = ""

    try:
        # Change the data type for validation of end_date
        data = {"end_date": datetime.strptime(request.json.get('end_date'), '%Y-%m-%d'), "item": request.json.get('item')}
        if v.validate(data) == False:
            #response = "Argument Error"
            return response 
    except ValueError:
        #response = "An error occurred"
        return response
    except TypeError:
        #response = "An error occurred"
        return response

    # Inject request data into database
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("insert into tasks (end_date,item,update_record_date) values (?,?,?)" , (data.get("end_date"), data.get("item"), datetime.now()))
        conn.commit()
        #response = "Data has been injected"
        return response
    except sqlite3.Error as e:
        #response = "An error occurred:" % e.args[0]
        return response

@app.route(CONTEXT_ROOT + '/tasks', methods=['PUT'])
def upd_tasks(task):
    """ 【API】タスクを更新する """
    response = jsonify(update_for_object(
        'update tasks set status=%d where task_id=%d' % (int(task.status), int(task.task_id))))
    return response


@app.route(CONTEXT_ROOT + '/tasks', methods=['DELETE'])
def del_tasks():
    """ 【API】タスクを削除する """
    response = jsonify(update_for_object(
        'delete from tasks where task_id=%s' % (int(task.task_id))))
    return response


if __name__ == '__main__':
    app.run(debug=True)
