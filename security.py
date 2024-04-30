import functools

from flask import session, g, redirect, url_for

from user import find_user_by_id


def load_current_user():
    if not session.get('user_id'):
        g.user = None
    else:
        g.user = find_user_by_id(session.get('user_id'))


def is_fully_authenticated(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user:
            return redirect(url_for('login'))

        return view(**kwargs)

    return wrapped_view
