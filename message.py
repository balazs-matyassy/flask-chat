from flask import g


class Message:
    def __init__(self, title='', body='', message_id=None):
        self.id = message_id
        self.title = title
        self.body = body

    @property
    def form(self):
        return {
            'id': self.id,
            'title': self.title,
            'body': self.body
        }

    @form.setter
    def form(self, data):
        if 'title' in data:
            self.title = data['title'].strip()

        if 'body' in data:
            self.body = data['body'].strip()

    def validate(self):
        errors = []

        if not self.title:
            errors.append('Title missing.')

        if not self.body:
            errors.append('Body missing.')

        return errors

    @staticmethod
    def create(data):
        if not data:
            return None

        message = Message(message_id=data['id'])
        message.form = data

        return message


def find_all_messages():
    with g.db.cursor() as cursor:
        query = '''
                SELECT `id`, `title`,`body`
                FROM `message`
                ORDER BY `id` DESC;
        '''

        cursor.execute(query)

        return [Message.create(data) for data in cursor.fetchall()]


def find_message_by_id(message_id):
    with g.db.cursor() as cursor:
        query = '''
                SELECT `id`, `title`,`body`
                FROM `message`
                WHERE `id` = %s;
        '''
        args = (message_id,)

        cursor.execute(query, args)

        return Message.create(cursor.fetchone())


def find_all_messages_by_title_like(title):
    with g.db.cursor() as cursor:
        query = '''
                SELECT `id`, `title`,`body`
                FROM `message`
                WHERE `title` LIKE %s
                ORDER BY `id` DESC;
        '''
        args = (f'%{title}%',)

        cursor.execute(query, args)

        return [Message.create(data) for data in cursor.fetchall()]


def save_message(message):
    with g.db.cursor() as cursor:
        if not message.id:
            query = '''
                    INSERT INTO `message`
                        (`title`, `body`)
                    VALUES(%s, %s);
            '''
            args = (
                message.title,
                message.body
            )

            cursor.execute(query, args)
            g.db.commit()

            message.id = cursor.lastrowid
        else:
            query = '''
                    UPDATE `message`
                    SET `title` = %s,
                        `body` = %s
                    WHERE `id` = %s;
            '''
            args = (
                message.title,
                message.body,
                message.id
            )

            cursor.execute(query, args)
            g.db.commit()

    return message


def delete_message_by_id(message_id):
    with g.db.cursor() as cursor:
        query = '''
                DELETE FROM `message`
                WHERE `id` = %s;
        '''
        args = (message_id,)

        cursor.execute(query, args)
        g.db.commit()
