import os, json, keyboard, time
from flask import Flask, request, url_for, redirect, send_from_directory
from flask_login import login_user, LoginManager, logout_user, login_required

from listeners_blueprint import listeners

from werkzeug.exceptions import abort
from datetime import date, datetime
import pandas as pd, numpy as np
from random import randrange

from utils import redirect_back, render_svelte, json_serial, init_macros, check_user, get_image_loc
from sqlutils import pull_macros, pull_commands, delete_macro, delete_command, move_command, update_macro, update_commands, add_func, create_macro, User

class MyFlaskApp(Flask):
  def run(self, host=None, port=None, debug=None, load_dotenv=True, **options):
    if not self.debug or os.getenv('WERKZEUG_RUN_MAIN') == 'true':
      with self.app_context():
        # rows = pull_macros()
        init_macros()
        
    super(MyFlaskApp, self).run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

app = MyFlaskApp(__name__)
app.register_blueprint(listeners, url_prefix='/word_listeners')
app.secret_key = "sassdfsdfs3sdfdfdadsf2423442sdfasdf2fb3443b4"
# app.debug=True
login_manager = LoginManager(app)
login_manager.init_app(app)

@app.route('/')
@login_required
def index():
    # threading.Thread(target=do_something).start()
    rows = pull_macros()
    return render_svelte('index', extra_data=json.dumps({'macro':rows, 'current_user':check_user(),}, default=json_serial))

@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    error_x = False
    if request.method == 'POST':
        title = request.form['name'] ## activation_key
        tags = request.form['tags']
        description = request.form['description']
        activation_key = request.form['activation_key']
        interval = request.form['interval']
        enabled = request.form['enabled']
        added_bool = create_macro(title, tags, description, activation_key, interval, enabled)
        if added_bool:
            return redirect(url_for('index'))
        else:
            error_x = f'{title} already in use!'
            render_svelte('create', extra_data=json.dumps({'current_user':check_user(),'error': error_x,}, default=json_serial))
    return render_svelte('create', extra_data=json.dumps({'current_user':check_user(),'error': error_x,}, default=json_serial))

@app.route('/<string:page_title>')
@login_required
def data(page_title):
    # page, file_list = get_page_data(page_title)
    macro_info = pull_macros(pull=page_title)
    commands = pull_commands(page_title)
    return render_svelte('macropage', title=page_title, extra_data=json.dumps({'macro':macro_info, 'command_list':commands, 'current_user':check_user(),}, default=json_serial))

@app.route('/add_function/', methods=('GET', 'POST'))
@login_required
def add_function():
    if request.method == 'POST':
        jsonResponse = json.loads(request.data.decode('utf-8'))
        macro_name = jsonResponse['macro_name']
        comm_type = jsonResponse['comm_type']
        comm_value = jsonResponse['comm_value']

        add_func(macro_name, comm_type, comm_value)
        return "success!"

@app.route('/update/macro/', methods=('GET', 'POST'))
@login_required
def update_sql():
    if request.method == 'POST':
        jsonResponse = json.loads(request.data.decode('utf-8'))
        update_column = jsonResponse['update']
        value_to_set = jsonResponse['value']
        where = jsonResponse['where']
        where_val = jsonResponse['where_value']

        updated_bool = update_macro(update_column, value_to_set, where, where_val)
        
        if updated_bool:
            keyboard.unhook_all_hotkeys()
            init_macros()
            return json.dumps({'return_msg': "Success"})
        else:
            return json.dumps({'return_msg': "NameError"})
    # if file_list_response == 400:
    #     return "error in copart_trig.", 400
    # else:
    #     return json.dumps({'file_list':file_list_response,})

@app.route('/update/commands/', methods=('GET', 'POST'))
@login_required
def update_comms():
    if request.method == 'POST':
        jsonResponse = json.loads(request.data.decode('utf-8'))
        update_column = jsonResponse['update']
        value_to_set = jsonResponse['value']
        where = jsonResponse['where']
        where_val = jsonResponse['where_value']
        and_where = jsonResponse['and_where']
        and_equals = jsonResponse['and_equals']

        updated_bool = update_commands(update_column, value_to_set, where, where_val, and_where, and_equals)
        
        if updated_bool:
            keyboard.unhook_all_hotkeys()
            init_macros()
            return json.dumps({'return_msg': "Success"})
        else:
            return json.dumps({'return_msg': "NameError"})
    # if file_list_response == 400:
    #     return "error in copart_trig.", 400
    # else:
    #     return json.dumps({'file_list':file_list_response,})

@app.route('/move_comm/', methods=('GET', 'POST'))
@login_required
def move_comm():
    if request.method == 'POST':
        jsonResponse = json.loads(request.data.decode('utf-8'))
        macro_name = jsonResponse['macro_name']
        new_id = jsonResponse['new_id']
        old_id = jsonResponse['old_id']

        rows = move_command(macro_name, new_id, old_id)
        return json.dumps({'return_msg': rows})
        
        # if updated_bool:
        #     keyboard.unhook_all_hotkeys()
        #     init_macros()
        #     return json.dumps({'return_msg': "Success"})
        # else:
        #     return json.dumps({'return_msg': "NameError"})

@app.route('/delete/', methods=('GET', 'POST'))
@login_required
def delete_in_sql():
    if request.method == 'POST':
        jsonResponse = json.loads(request.data.decode('utf-8'))
        where = jsonResponse['where']
        where_val = jsonResponse['where_value']

        delete_macro(where, where_val)
        return "success!"
    # if file_list_response == 400:
    #     return "error in copart_trig.", 400
    # else:
    #     return json.dumps({'file_list':file_list_response,})

@app.route('/delete/command', methods=('GET', 'POST'))
@login_required
def delete_command_in_sql():
    if request.method == 'POST':
        jsonResponse = json.loads(request.data.decode('utf-8'))
        name_var = jsonResponse['name_var']
        command_id_var = jsonResponse['command_id_var']

        delete_command(name_var, command_id_var)
        return "success!"

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect('/')

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        name = request.form["username"]
        password = request.form["password"]
        user = User(name, password)
        if user.is_authenticated():
            login_user(user, remember=True)
            return redirect_back('index')
        else:
            return render_svelte('login', title="login - AppName12!")
    else:
        return render_svelte('login', title="login - AppName!")

@app.route('/regioncheck/', methods=['GET', 'POST'])
@login_required
def regioncheck():
    if request.method == "POST":
        jsonResponse = json.loads(request.data.decode('utf-8'))
        image_to_locate = jsonResponse['image_to_locate']

        updated_bool = get_image_loc(image_to_locate)
        return json.dumps({'return_msg': updated_bool})
    else:
        return render_svelte('regioncheck', title="regioncheck - AppName!", extra_data=json.dumps({'current_user':check_user(),}))

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    return redirect(url_for('login'))

@app.context_processor
def utility_functions():
    def print_in_console(message):
        print(str(message))

    return dict(mdebug=print_in_console)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
