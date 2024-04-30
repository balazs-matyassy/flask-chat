import click
import pymysql
import pymysql.cursors
from flask import current_app, g


def get_connection():
    return pymysql.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        user=current_app.config['DB_USERNAME'],
        password=current_app.config['DB_PASSWORD'],
        database=current_app.config['DB_DATABASE'],
        cursorclass=pymysql.cursors.DictCursor
    )


def connect():
    if 'db' not in g:
        g.db = get_connection()


def disconnect(e):
    if 'db' in g:
        g.pop('db').close()


@click.command('install')
def install_command():
    with get_connection() as db:
        with db.cursor() as cursor:
            query = '''
                    DROP TABLE IF EXISTS `recipe`;
            '''

            cursor.execute(query)

            query = '''
                    CREATE TABLE `recipe`
                    (
                        `id`          INT          NOT NULL AUTO_INCREMENT,
                        `category`    VARCHAR(255) NOT NULL,
                        `name`        VARCHAR(255) NOT NULL,
                        `difficulty`  INT          NOT NULL,
                        PRIMARY KEY (`id`)
                    );
            '''

            cursor.execute(query)
            db.commit()

    click.echo('Application installation successful.')
