import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_verify(quest_num, pubkey, success=False):
    db = get_db()
    db.execute('INSERT INTO sq{}_verification (quest_pk, success)'.format(quest_num) +
               ' VALUES (?, ?)',
               (pubkey, 1 if success else 0))
    db.commit()

def insert_clue(quest_num, columns=(), values=()):
    db=get_db()
    db.execute(f'INSERT INTO sq{quest_num}_clues {(*columns,)} VALUES {(*values,)}')
    db.commit()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_sq03_db():
    db = get_db()
    with current_app.open_resource('sq/side_quest_03_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

def init_sq04_db():
    db = get_db()
    with current_app.open_resource('sq/side_quest_04_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

def init_sq05_db():
    db = get_db()
    with current_app.open_resource('sq/side_quest_05_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

def init_sq06_db():
    db = get_db()
    with current_app.open_resource('sq/side_quest_06_schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

@click.command('init-sq03-db')
@with_appcontext
def init_sq03_db_command():
    """Clear the existing data and create new tables."""
    init_sq03_db()
    click.echo('Initialized the sq03 tables')

@click.command('init-sq04-db')
@with_appcontext
def init_sq04_db_command():
    """Clear the existing data and create new tables."""
    init_sq04_db()
    click.echo('Initialized the sq04 tables')

@click.command('init-sq05-db')
@with_appcontext
def init_sq05_db_command():
    """Clear the existing data and create new tables."""
    init_sq05_db()
    click.echo('Initialized the sq05 tables')

@click.command('init-sq06-db')
@with_appcontext
def init_sq06_db_command():
    """Clear the existing data and create new tables."""
    init_sq06_db()
    click.echo('Initialized the sq06 tables')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_sq03_db_command)
    app.cli.add_command(init_sq04_db_command)
    app.cli.add_command(init_sq05_db_command)
    app.cli.add_command(init_sq06_db_command)
