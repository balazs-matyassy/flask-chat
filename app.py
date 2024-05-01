from flask import Flask, render_template, abort, request, flash, redirect, url_for, g, session

from forms import EntityForm
from message import find_all_messages_by_title_like, find_all_messages, find_message_by_id, Message, save_message
from persistence import connect, disconnect, install_command
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
        return redirect(url_for('list_all_messages'))

    credentials = User()
    form = EntityForm(credentials)

    if form.validate_on_submit():
        user = find_user_by_username(credentials.username)

        if user and user.password == credentials.password:
            session['user_id'] = user.id
            flash('Login successful.')

            return redirect(url_for('list_all_messages'))
        else:
            form.errors.append('Wrong username or password.')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logout successful.')

    return redirect(url_for('list_all_messages'))


@app.route('/')
def list_all_messages():
    if request.args.get('search'):
        messages = find_all_messages_by_title_like(request.args.get('search'))
    else:
        messages = find_all_messages()

    return render_template('messages_list.html', messages=messages)


@app.route('/create', methods=('GET', 'POST'))
@is_fully_authenticated
def create_message():
    message = Message()
    form = EntityForm(message)

    if form.validate_on_submit():
        save_message(message)
        flash('Message created.')

        return redirect(url_for('list_all_messages'))

    return render_template('message_form.html', form=form)


@app.route('/edit/<int:message_id>', methods=('GET', 'POST'))
@is_fully_authenticated
def edit_message(message_id):
    message = find_message_by_id(message_id) or abort(404)
    form = EntityForm(message)

    if form.validate_on_submit():
        save_message(message)
        flash('Message saved.')

        return redirect(url_for('edit_message', message_id=message.id))

    return render_template('message_form.html', form=form)


@app.route('/delete/<int:message_id>', methods=('POST',))
@is_fully_authenticated
def delete_message(message_id):
    find_message_by_id(message_id) or abort(404)
    delete_message_by_id(message_id)
    flash('Message deleted.')

    return redirect(url_for('list_all_messages'))


if __name__ == '__main__':
    app.run()
