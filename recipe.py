from flask import g


class Recipe:
    def __init__(self, category='', name='', difficulty=1, recipe_id=None):
        self.id = recipe_id
        self.category = category
        self.name = name
        self.difficulty = difficulty

    @property
    def difficulty_description(self):
        if self.difficulty == 1:
            return 'Very easy'
        elif self.difficulty == 2:
            return 'Easy'
        elif self.difficulty == 3:
            return 'Medium'
        elif self.difficulty == 4:
            return 'Difficult'
        elif self.difficulty == 5:
            return 'Very difficult'

        return 'Unknown'

    @property
    def form(self):
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'difficulty': self.difficulty
        }

    @form.setter
    def form(self, data):
        if 'category' in data:
            self.category = data['category'].strip().capitalize()

        if 'name' in data:
            self.name = data['name'].strip().capitalize()

        if 'difficulty' in data:
            try:
                self.difficulty = int(data['difficulty'])

                if self.difficulty < 1:
                    self.difficulty = 1
                elif self.difficulty > 5:
                    self.difficulty = 5
            except ValueError:
                self.difficulty = 1

    def validate(self):
        errors = []

        if not self.category:
            errors.append('Category missing.')

        if not self.name:
            errors.append('Name missing.')

        return errors

    @staticmethod
    def create(data):
        if not data:
            return None

        recipe = Recipe(recipe_id=data['id'])
        recipe.form = data

        return recipe


def find_all_recipes():
    with g.db.cursor() as cursor:
        query = '''
                SELECT `id`, `category`,`name`, `difficulty`
                FROM `recipe`
                ORDER BY `category`, `name`;
        '''

        cursor.execute(query)

        return [Recipe.create(data) for data in cursor.fetchall()]


def find_recipe_by_id(recipe_id):
    with g.db.cursor() as cursor:
        query = '''
                SELECT `id`, `category`,`name`, `difficulty`
                FROM `recipe`
                WHERE `id` = %s;
        '''
        args = (recipe_id,)

        cursor.execute(query, args)

        return Recipe.create(cursor.fetchone())


def find_all_recipes_by_name_like(name):
    with g.db.cursor() as cursor:
        query = '''
                SELECT `id`, `category`,`name`, `difficulty`
                FROM `recipe`
                WHERE `name` LIKE %s
                ORDER BY `category`, `name`;
        '''
        args = (f'%{name}%',)

        cursor.execute(query, args)

        return [Recipe.create(data) for data in cursor.fetchall()]


def save_recipe(recipe):
    with g.db.cursor() as cursor:
        if not recipe.id:
            query = '''
                    INSERT INTO `recipe`
                        (`category`, `name`, `difficulty`)
                    VALUES(%s, %s, %s);
            '''
            args = (
                recipe.category,
                recipe.name,
                recipe.difficulty
            )

            cursor.execute(query, args)
            g.db.commit()

            recipe.id = cursor.lastrowid
        else:
            query = '''
                    UPDATE `recipe`
                    SET `category` = %s,
                        `name` = %s,
                        `difficulty` = %s
                    WHERE `id` = %s;
            '''
            args = (
                recipe.category,
                recipe.name,
                recipe.difficulty,
                recipe.id
            )

            cursor.execute(query, args)
            g.db.commit()

    return recipe


def delete_recipe_by_id(recipe_id):
    with g.db.cursor() as cursor:
        query = '''
                DELETE FROM `recipe`
                WHERE `id` = %s;
        '''
        args = (recipe_id,)

        cursor.execute(query, args)
        g.db.commit()
