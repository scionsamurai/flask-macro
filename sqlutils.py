
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("scraper.db")
    return conn

def quotes_or_no(value):
    return f"'{value}'" if not isinstance(value, (int, float)) else f"{value}"

def pull_macros(pull="all"):
    conn = get_db_connection()
    cursor = conn.cursor()
    if pull == "all":
        rows = cursor.execute("SELECT name, tags, description, activation_key, interval, enabled, date_added, last_edited FROM Macro;").fetchall()
    else:
        rows = cursor.execute(f"SELECT name, tags, description, activation_key, interval, enabled, date_added, last_edited FROM Macro WHERE name= '{pull}';").fetchall()
        print(rows)
        if len(rows) > 1:
            print('Error! Too many macros with same name! That should\'t have happened.')
        else:
            print(rows)
            rows = rows[0]
    # running_list = rows
    cursor.close()
    conn.close()
    return rows

def update_macro(update, value, where, where_equals):
    conn = get_db_connection()
    cursor = conn.cursor()

    if update == 'name':
        rows = cursor.execute(f"SELECT name FROM Macro WHERE name= '{value}';").fetchall()
        if not len(rows):
            cursor.execute(f"UPDATE Macro set {update} = {quotes_or_no(value)} WHERE {where} = {quotes_or_no(where_equals)} ").fetchall()
            # If we update the name of the macro we will also need to update the name of it in the commands table
            # and commands table needs the command ID and the macro name to update (and_where is the second logic check)
            conn.commit()
            cursor.close()
            conn.close()
            update_commands(update, value, where, where_equals, False, False)
            return True
        else:
            cursor.close()
            conn.close()
            return False
            
    else:
        cursor.execute(f"UPDATE Macro set {update} = {quotes_or_no(value)} WHERE {where} = {quotes_or_no(where_equals)} ").fetchall()
        conn.commit()

    cursor.close()
    conn.close()
    return True

def update_commands(update, value, where, where_equals, and_where, and_equals):
    conn = get_db_connection()
    cursor = conn.cursor()
    if and_where:
        cursor.execute(f"UPDATE Commands set {update} = {quotes_or_no(value)} WHERE ( {where} = {quotes_or_no(where_equals)} AND {and_where} = {quotes_or_no(and_equals)} )").fetchall()
    else:
        cursor.execute(f"UPDATE Commands set {update} = {quotes_or_no(value)} WHERE {where} = {quotes_or_no(where_equals)} ").fetchall()
    
    conn.commit()
    cursor.close()
    conn.close()
    return True

def move_command(macro_name, new_id, old_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(f"SELECT command_id FROM Commands WHERE name= '{macro_name}'").fetchall()
    max_id = 0
    for row in rows:
        if row[0] > max_id:
            max_id = row[0]
    max_id += 1
    print('rows', rows)
    print(new_id, old_id)
    if new_id < old_id:
        cursor.execute(f"UPDATE Commands set command_id = {quotes_or_no(max_id)} WHERE ( name = {quotes_or_no(macro_name)} AND command_id = {quotes_or_no(new_id)} )").fetchall()
        cursor.execute(f"UPDATE Commands set command_id = {quotes_or_no(new_id)} WHERE ( name = {quotes_or_no(macro_name)} AND command_id = {quotes_or_no(old_id)} )").fetchall()
        cursor.execute(f"UPDATE Commands set command_id = {quotes_or_no(old_id)} WHERE ( name = {quotes_or_no(macro_name)} AND command_id = {quotes_or_no(max_id)} )").fetchall()
    elif new_id > old_id:
        cursor.execute(f"UPDATE Commands set command_id = {quotes_or_no(max_id)} WHERE ( name = {quotes_or_no(macro_name)} AND command_id = {quotes_or_no(old_id)} )").fetchall()
        cursor.execute(f"UPDATE Commands set command_id = {quotes_or_no(old_id)} WHERE ( name = {quotes_or_no(macro_name)} AND command_id = {quotes_or_no(new_id)} )").fetchall()
        cursor.execute(f"UPDATE Commands set command_id = {quotes_or_no(new_id)} WHERE ( name = {quotes_or_no(macro_name)} AND command_id = {quotes_or_no(max_id)} )").fetchall()

    conn.commit()
    rows = cursor.execute(f"SELECT command_id, command_type, command FROM Commands WHERE name= '{macro_name}'").fetchall()
    cursor.close()
    conn.close()
    return rows

def pull_listeners(pull="all"):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT listen_for, command FROM Listeners;").fetchall()

    # running_list = rows
    cursor.close()
    conn.close()
    return rows

def delete_listener(listen_for_string):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM Listeners WHERE listen_for = {quotes_or_no(listen_for_string)};")
    conn.commit()

    cursor.close()
    conn.close()

def add_listener():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO Listeners (listen_for, command)'
                'VALUES (?, ?)',
                ("", ""))
    conn.commit()

    cursor.close()
    conn.close()

def update_listener(column_to_update, update_to_value, where, where_equals):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(f"UPDATE Listeners set {column_to_update} = {quotes_or_no(update_to_value)} WHERE {where} = {quotes_or_no(where_equals)} ")

    conn.commit()

    cursor.close()
    conn.close()

def delete_macro(where, where_equals):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM Macro WHERE {where} = {quotes_or_no(where_equals)};")
    cursor.execute(f"DELETE FROM Commands WHERE {where} = {quotes_or_no(where_equals)};")
    conn.commit()

    cursor.close()
    conn.close()

def delete_command(name_var, command_id_var):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM Commands WHERE ( name = {quotes_or_no(name_var)} AND command_id = {quotes_or_no(command_id_var)} );")
    # lower the id of all commands in with same name but higher id
    rows = cursor.execute(f"SELECT name, command_id FROM Commands WHERE name= '{name_var}';").fetchall()
    rows.sort(key=lambda xy: xy[1])
    update_IDs = []
    for row in rows:
        if row[1] > command_id_var:
            cursor.execute(f"UPDATE Commands set command_id = {quotes_or_no(row[1]-1)} WHERE ( name = {quotes_or_no(name_var)} AND command_id = {row[1]} ); ")
            # update_IDs.append(row[1])
    # print("update_IDs", update_IDs)      

    conn.commit()

    rows = cursor.execute(f"SELECT name, command_id FROM Commands WHERE name= '{name_var}';").fetchall()
    print('rows', rows)

    cursor.close()
    conn.close()

def create_macro(title, tags, description, activation_key, interval, enabled):
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute(f"SELECT name FROM Macro WHERE name= '{title}';").fetchall()
    print(rows);
    if not len(rows):
        cursor.execute(f'INSERT INTO Macro (name, tags, description, activation_key, interval, enabled, date_added, last_edited)'
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                    (title, tags, description, activation_key, interval, enabled, 1, 1))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    else:
        cursor.close()
        conn.close()
        return False

def add_func(macro_name, comm_type, comm_value):
    conn = get_db_connection()
    cursor = conn.cursor()

    rows = cursor.execute(f"SELECT name, command_id FROM Commands WHERE name='{macro_name}';").fetchall()
    try:
        set_id = max([x[1] for x in rows]) + 1
    except ValueError:
        set_id = 0
    print('rows', rows)

    cursor.execute(f"INSERT INTO Commands VALUES ('{macro_name}', {set_id}, '{comm_type}', '{comm_value}')")
    
    # cursor.execute(f"UPDATE {table} set {update} = {quotes_or_no(value)} WHERE {where} = {quotes_or_no(where_equals)} ").fetchall()
    conn.commit()

    cursor.close()
    conn.close()

def pull_commands(macro_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute(f"SELECT command_id, command_type, command FROM Commands WHERE name= '{macro_name}'").fetchall()
    rows.sort(key=lambda xy: xy[0])
    # running_list = rows
    cursor.close()
    conn.close()
    return rows

class User:
    name = ""
    password = ""

    def __init__(self, name="", password=""):
        self.name = name
        self.password = password
        self.id = 0;

    def is_authenticated(self):

        query = "SELECT * FROM User WHERE username= ?;"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (self.name,))
        data = cur.fetchone()
        print('data', data)
        cur.close()
        conn.close()
        if data is None:
            return False
        else:
            print("self.check_password(data[1])", self.check_password(data[1]))
            if self.check_password(data[1]):
                return True
            else:
                return False

    def is_active(self):
        return True

    def get_id(self):
        return str(self.name)

    def set_password(self, passwordy):
        self.pw_hash = passwordy
        # self.pw_hash = generate_password_hash(passwordy)

    def check_password(self, passwordx):
        return passwordx == self.password
        # return check_password_hash(passwordx, self.password)

    @staticmethod
    def get(user_name):
        query = "SELECT * FROM User WHERE username= ?;"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, (user_name,))
        data = cur.fetchone()
        user = User()
        user.name = data[0]
        # user.password = data[2]  #commented out because users password isn't needed after member authenticated - left empty
        cur.close()
        conn.close()
        return user

