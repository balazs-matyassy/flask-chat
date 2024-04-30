import json


class User:
    def __init__(self, username='', password='', user_id=None):
        self.id = user_id
        self.username = username
        self.password = password

    @property
    def form(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password
        }

    @form.setter
    def form(self, data):
        if 'username' in data:
            self.username = data['username'].strip().lower()

        if 'password' in data:
            self.password = data['password']

    def validate(self):
        errors = []

        if not self.username:
            errors.append('Username missing.')

        if not self.password:
            errors.append('Password missing.')

        return errors

    @staticmethod
    def create(data):
        user = User(user_id=data.get('id'))

        if 'username' in data:
            user.username = data['username']

        if 'password' in data:
            user.password = data['password']

        return user


def find_all_users():
    with open('users.json', encoding='utf-8') as file:
        users = []

        for data in json.load(file):
            users.append(User.create(data))

        return users


def find_user_by_id(user_id):
    for user in find_all_users():
        if user.id == user_id:
            return user

    return None


def find_user_by_username(username):
    for user in find_all_users():
        if user.username == username:
            return user

    return None
