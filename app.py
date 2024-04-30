from flask import Flask, render_template, abort, request, flash, redirect, url_for, g, session

from forms import EntityForm
from persistence import connect, disconnect, install_command
from recipe import (Recipe, find_all_recipes, find_recipe_by_id, find_all_recipes_by_name_like,
                    save_recipe, delete_recipe_by_id)
from security import load_current_user, is_fully_authenticated
from user import User, find_user_by_username


app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev'  # flash üzenetekhez kell
app.config['DB_HOST'] = 'localhost'
app.config['DB_PORT'] = 3306
app.config['DB_USERNAME'] = 'root'
app.config['DB_PASSWORD'] = 'password'
app.config['DB_DATABASE'] = 'chat'

app.cli.add_command(install_command)
app.before_request(connect)
app.teardown_appcontext(disconnect)
app.before_request(load_current_user)
app.jinja_env.globals['is_fully_authenticated'] = lambda: g.user is not None


@app.route('/login', methods=('GET', 'POST'))
def login():
    if g.user:
        return redirect(url_for('list_all_recipes'))

    credentials = User()
    form = EntityForm(credentials)

    if form.validate_on_submit():
        user = find_user_by_username(credentials.username)

        if user and user.password == credentials.password:
            session['user_id'] = user.id
            flash('Login successful.')

            return redirect(url_for('list_all_recipes'))
        else:
            form.errors.append('Wrong username or password.')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout successful.')

    return redirect(url_for('list_all_recipes'))


@app.route('/')
def list_all_recipes():
    if request.args.get('search'):
        recipes = find_all_recipes_by_name_like(request.args.get('search'))
    else:
        recipes = find_all_recipes()

    return render_template('recipes_list.html', recipes=recipes)


@app.route('/view/<int:recipe_id>')
def view_recipe(recipe_id):
    recipe = find_recipe_by_id(recipe_id) or abort(404)

    return render_template('recipe_view.html', recipe=recipe)


@app.route('/create', methods=('GET', 'POST'))
@is_fully_authenticated
def create_recipe():
    recipe = Recipe()
    form = EntityForm(recipe)

    if form.validate_on_submit():
        save_recipe(recipe)
        flash('Recipe created.')

        return redirect(url_for('list_all_recipes'))

    return render_template('recipe_form.html', form=form)


@app.route('/edit/<int:recipe_id>', methods=('GET', 'POST'))
@is_fully_authenticated
def edit_recipe(recipe_id):
    recipe = find_recipe_by_id(recipe_id) or abort(404)
    form = EntityForm(recipe)

    if form.validate_on_submit():
        save_recipe(recipe)
        flash('Recipe saved.')

        return redirect(url_for('edit_recipe', recipe_id=recipe.id))

    return render_template('recipe_form.html', form=form)


@app.route('/delete/<int:recipe_id>', methods=('POST',))
@is_fully_authenticated
def delete_recipe(recipe_id):
    find_recipe_by_id(recipe_id) or abort(404)
    delete_recipe_by_id(recipe_id)
    flash('Recipe deleted.')

    return redirect(url_for('list_all_recipes'))


if __name__ == '__main__':
    app.run()
