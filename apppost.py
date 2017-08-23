''' REST sample '''
#!flask/bin/python
import sqlite3
import json
from contextlib import closing
from flask import Flask, jsonify, abort, make_response, url_for, g, request, session, redirect, abort, render_template, flash

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


def connect_db():
    """ connection作成用 """
    return sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_COLNAMES)


@app.before_request
def before_request():
    """ 【フレームワーク用】リクエスト受信時の初期化処理 """
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    """ 【フレームワーク用】リクエスト終了時のお掃除処理 """
    db = getattr(g, 'db', None)
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


@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    """ 【API】全タスクリストを返却する """
    response = jsonify(select_for_object('select * from tasks'))
    return response


if __name__ == '__main__':
    app.run(debug=True)
