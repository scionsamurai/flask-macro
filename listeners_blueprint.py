import json, keyboard
from flask import Blueprint, request
from flask_login import login_required

from utils import render_svelte, json_serial, init_macros, check_user
from sqlutils import pull_listeners, delete_listener, add_listener, update_listener

listeners = Blueprint('listeners', __name__)

@listeners.route('/')
@login_required
def word_listeners():
    # threading.Thread(target=do_something).start()
    rows = pull_listeners()
    return render_svelte('listeners', extra_data=json.dumps({'listeners':rows, 'current_user':check_user(),}, default=json_serial))

@listeners.route('/add', methods=('GET', 'POST'))
@login_required
def add_listeners():
    if request.method == 'POST':
        add_listener()
        return "success!"

@listeners.route('/delete', methods=('GET', 'POST'))
@login_required
def delete_listeners():
    if request.method == 'POST':
        jsonResponse = json.loads(request.data.decode('utf-8'))
        listen_for_string = jsonResponse['listen_for_string']

        delete_listener(listen_for_string)
        return "success!"

@listeners.route('/update', methods=('GET', 'POST'))
@login_required
def update_listeners():
    if request.method == 'POST':
        jsonResponse = json.loads(request.data.decode('utf-8'))
        column_to_update = jsonResponse['column_to_update']
        update_to_value = jsonResponse['update_to_value']
        where = jsonResponse['where']
        where_equals = jsonResponse['where_equals']

        update_listener(column_to_update, update_to_value, where, where_equals)

        keyboard.unhook_all_hotkeys()
        init_macros()
        return "success!"
