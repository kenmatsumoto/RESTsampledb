''' REST sample '''
#!flask/bin/python
import sqlite3
import json
from contextlib import closing
from flask import Flask, jsonify, abort, make_response, url_for, g, request, session, redirect, abort, render_template, flash

#DB settings
DATABASE = 'apppost.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#building app
app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APPPOST_SETTINGS', silent=True)

#connection
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

''' def init_db():
    db = g.db
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()
'''

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['POST'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

def task_to_json (task):
    json_task = {}
    json_task['id'] = task[0]
    json_task['title'] = task[1]
    json_task['description'] = task[2]
    return json_task

def show_public_tasks_in_db():
    db = g.db
    cur = db.execute('select * from tasks')
    result = cur.fetchall()
    new_tasks = []
    for row in result:
        new_tasks.append(task_to_json(row))
    print (new_tasks)
    return new_tasks

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    response = jsonify(show_public_tasks_in_db())

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=True)