import flask
from flask import request, jsonify, redirect, url_for
import sqlite3
from sqlite3 import Error

characters = [
    {'id': 0, 'name': 'Julian'}, {'id': 1, 'name': 'Thomas'}, {'id': 2, 'name': 'Mikhail'}, {'id': 3, 'name': 'Harid'},
    {'id': 4, 'name': 'Sarah'}, {'id': 5, 'name': 'Ellen'}, {'id': 6, 'name': 'Monica'}, {'id': 7, 'name': 'Katarina'},
    {'id': 8, 'name': 'Bai Meiling'}, {'id': 9, 'name': 'Black'}, {'id': 10, 'name': 'Boston'},
    {'id': 11, 'name': 'Fairy'}, {'id': 12, 'name': '(Fake) Robin'}, {'id': 13, 'name': 'Fullbright'},
    {'id': 14, 'name': 'Herman'}, {'id': 15, 'name': 'Leonid'}, {'id': 16, 'name': 'Muse'}, {'id': 17, 'name': 'Nora'},
    {'id': 18, 'name': 'Paul'}, {'id': 19, 'name': 'Poet'}, {'id': 20, 'name': 'Robin'}, {'id': 21, 'name': 'Sharl'},
    {'id': 22, 'name': 'Shonen'}, {'id': 23, 'name': 'Snowman'}, {'id': 24, 'name': 'Tatyana'},
    {'id': 25, 'name': 'Tiberius'}, {'id': 26, 'name': 'Undine'}, {'id': 27, 'name': 'Wood'},
    {'id': 28, 'name': 'Yan Fan'}, {'id': 29, 'name': 'Zhi Lin'}, {'id': 30, 'name': 'Zo'}
]


def sql_connection():
    try:
        con = sqlite3.connect('RSdatabase.db')
        return con
    except Error:
        print(Error)


def sql_table(con):
    cursorObj = con.cursor()
    cursorObj.execute('CREATE TABLE IF NOT EXISTS characters(id integer PRIMARY KEY, name text)')
    con.commit()


def sql_insert(con, entities):
    cursorObj = con.cursor()
    try:
        for i in entities:
            cursorObj.execute('INSERT INTO characters(id, name) VALUES(?, ?)', i)
        con.commit()
        return True
    except Error:
        return


def sql_update(con, entities):
    cursorObj = con.cursor()
    try:
        for i in entities:
            cursorObj.execute('UPDATE characters SET name=? WHERE id=?', i)
        con.commit()
        return True
    except Error:
        return


def sql_delete(con, entities):
    cursorObj = con.cursor()
    try:
        for i in entities:
            cursorObj.execute('DELETE FROM characters WHERE id=?', i[0])
        con.commit()
        return True
    except Error:
        return


def sql_clear(con):
    cursorObj = con.cursor()
    cursorObj.execute('DELETE FROM characters')
    con.commit()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def initialize_table():
    con = sql_connection()
    sql_table(con)

    entities = []
    for i in characters:
        entities.append([i['id'], i['name']])

    sql_clear(con)
    sql_insert(con, entities)
    con.close()


initialize_table()

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Romancing Saga 3 Database</h1>
<p>An API containing all recruitable characters from Romancing Sage 3.</p>'''


@app.route('/api/v1/resources/characters/all', methods=['GET'])
def api_all():
    con = sql_connection()
    con.row_factory = dict_factory
    cursorObj = con.cursor()
    results = cursorObj.execute('SELECT * FROM characters').fetchall()
    con.close()

    return jsonify(results)


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/success')
def update_success():
    return "Update Successful!", 200


@app.route('/invalid_update')
def invalid_update():
    return "Invalid Update! Try another ID.", 400

@app.route('/record_created')
def record_created():
    return "Record created successfully!", 201


@app.route('/api/v1/resources/characters', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    name = query_parameters.get('name')

    query = 'SELECT * FROM characters WHERE'
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if name:
        query += ' name=? AND'
        to_filter.append(name)
    if not id and not name:
        return page_not_found(404)

    query = query[:-4] + ';'

    con = sql_connection()
    con.row_factory = dict_factory
    cursorObj = con.cursor()
    results = cursorObj.execute(query, to_filter).fetchall()
    con.close()

    return jsonify(results)


@app.route('/upload', methods=['PUT'])
def create_record():
    record = request.args
    entity = [[record.get('id'), record.get('name')]]
    print(entity)

    con = sql_connection()
    result = sql_insert(con, entity)
    con.close()
    if result:
        return redirect(url_for('record_created'))
    else:
        return redirect(url_for('invalid_update'))


@app.route('/update', methods=['PUT'])
def update_record():
    record = request.args
    entity = [[record.get('id'), record.get('name')]]

    con = sql_connection()
    result = sql_update(con, entity)
    con.close()
    if result:
        return redirect(url_for('update_success'))
    else:
        return redirect(url_for('invalid_update'))


@app.route('/delete', methods=['DELETE'])
def delete_record():
    record = request.args
    entity = [[record.get('id'), record.get('name')]]

    con = sql_connection()
    result = sql_delete(con, entity)
    con.close()
    if result:
        return redirect(url_for('update_success'))
    else:
        return redirect(url_for('invalid_update'))


app.run()