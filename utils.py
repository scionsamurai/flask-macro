
from flask import request, url_for, redirect, render_template
from flask_login import current_user#, login_user, LoginManager, logout_user, login_required
from urllib.parse import urlparse, urljoin
# https://pyautogui.readthedocs.io/
import time, os, re, keyboard, pyautogui, base64, tkinter, functools, pyperclip

from sqlutils import pull_commands, pull_macros, pull_listeners

pyautogui.FAILSAFE = False

def check_user():
    if current_user.__dict__ == {}:
        return 'anon'
    else:
        return current_user.__dict__ 

def run_command(command):
    interpreted_command = interpret_command(command[1])
    backspace_len = len(command[0])
    time.sleep(0.1)
    for i in range(backspace_len+1):
        keyboard.press('backspace')
        keyboard.release('backspace')
        time.sleep(0.01)
    for key_combo in interpreted_command:
        const_keys = [k for k in key_combo if len(k) > 1]
        not_const_keys = [k for k in key_combo if len(k) == 1]

        for key in const_keys:
            keyboard.press(key)
        for key in not_const_keys:
            keyboard.press(key)
        for key in not_const_keys:
            keyboard.release(key)
        for key in const_keys[::-1]:
            keyboard.release(key)

        time.sleep(0.1)

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.args.get('next'):
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint, **values):
    target = request.form['next'] if request.form and 'next' in request.form else request.args.get('next')
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                    for root_path, dirs, files in os.walk(folder)
                    for f in files))

def render_svelte(component, title=None, extra_data=None):
    return render_template('svelte_template.html', component=component, title=title,
                            extra_data=extra_data, last_updated=dir_last_updated('static'))

def current_milli_time():
    return round(time.time() * 1000)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def interpret_command(inp_string):
    held_keys = ["<CTRL>", "<WIN>", "<SHIFT>", "<ALT>"]
    replace_with = ["~","(",")","_","+","!","@","#","$","%","^","&","{","}","|",":","<",">","?"]
    orig_string = inp_string
    replaced_dict = {}
    all_spec_keys = [x for x in [*set(re.findall('<.*?>',inp_string))] if x[1:2] != '/' and x.lower() not in [y.lower() for y in held_keys]]
    for spec_key in all_spec_keys:
        # print('spec_key', spec_key)
        replaced_dict[replace_with[0]] = spec_key
        inp_string = inp_string.replace(spec_key,replace_with[0])
        replace_with = replace_with[1:]
    combo_keys = re.findall('<.*?>',inp_string)
    for key in combo_keys:
        inp_string = inp_string.replace(key,'*')
    split_on_combos = inp_string.split('*')

    # print("split_on_combos", split_on_combos)
    # print("combo_keys", combo_keys)

    def mysplit(string_inp):
        prev_char = False;
        split_on_indexes = []
        for index, character in enumerate(string_inp):
            if prev_char == False:
                prev_char = character
            else:
                if prev_char != '+' and character != '+':
                    split_on_indexes.append(index)
                prev_char = character
        if len(split_on_indexes):
            return [string_inp[:split_on_indexes[0]],*[string_inp[i:j] for i,j in zip(split_on_indexes, split_on_indexes[1:]+[None])]]
        else:
            return string_inp
        # return split_on_indexes

    def check_for_closing_bracket(id):
        check_next = False
        inp_key = ''
        for current_id, key in enumerate(combo_keys):
            key_val = re.findall('(?<=<).*?(?=>)', key)[0]
            if check_next:
                if inp_key == key_val[1:]:
                    return current_id
                elif key_val == inp_key:
                    return False
                else:
                    pass

            if current_id == id:
                check_next = True
                inp_key = key_val

        return False

    def check_if_between_brackets(split_combo_id):
        to_left =  combo_keys[:split_combo_id]
        between_keys = []
        for current_id, key in enumerate(to_left):
            if check_for_closing_bracket(current_id) >= split_combo_id:
                between_keys.append(key)
        return between_keys
    
    def update_commands(inp_dict):
        new_commands = []
        for command in commands:
            # print('command', command)
            for (key,var) in inp_dict.items():
                new_command = []
                for each_command in command:
                    new_command.append(each_command.replace(key, var))
                command = new_command
            new_commands.append(command)
        return new_commands


    def between_combo_keys(id1, id2):
        return combo_keys[id1:id2]
    # current_ind = 0
    commands = []
    combine_with_next = False
    for current_ind, x_string in enumerate(split_on_combos):
        # print('--------------------------------------')
        # print('current_ind', current_ind, 'x_string', x_string)
        # print('split_on_combos', split_on_combos)
        # print('combo_keys', combo_keys)
        # print('combine_with_next', combine_with_next)
        # print('commands', commands)
        if len(combo_keys):
            curr_key = combo_keys[current_ind-1]
            if x_string != '':
                between_brackets = check_if_between_brackets(current_ind)
                add_to_first = False
                add_to_last = False
                if x_string[:1] == '+' and len(x_string) != 1:
                    add_to_first = curr_key
                    x_string = x_string[1:]
                if x_string[len(x_string)-1:] == '+' and len(x_string) != 1:
                    add_to_last = combo_keys[current_ind]
                    x_string = x_string[:len(x_string)-1]
                split_string_on_action = mysplit(x_string)
                # check for unused combo_key between last command and current ()
                    # 
                between_combos = between_combo_keys(current_ind-1, current_ind)
                if len(between_combos):
                    for combo_key in between_combos:
                        if not combo_key in between_brackets and add_to_first != combo_key and combo_key[1:2] != '/':
                            commands.append([combo_key])
                def get_setPlus_split(string_x):
                    return set(string_x.split('+'))
                # print('split_string_on_action', split_string_on_action, isinstance(split_string_on_action, str))
                if isinstance(split_string_on_action, str):
                    if add_to_first:
                        between_brackets = [*between_brackets, add_to_first]
                    if add_to_last:
                        between_brackets = [*between_brackets, add_to_last]
                    grab_command = ''
                    if combine_with_next:
                        new_commands = []
                        for id_xy, command in enumerate(commands):
                            if id_xy != len(commands) -1:
                                new_commands.append(command)
                            else:
                                grab_command = command
                        commands = new_commands
                    if grab_command != '':
                        between_brackets = [*between_brackets, *grab_command]

                    if len([*get_setPlus_split(split_string_on_action)]):
                        if len(between_brackets):
                            commands.append([*between_brackets, *get_setPlus_split(split_string_on_action)])
                        else:
                            commands.append([*get_setPlus_split(split_string_on_action)])
                    else:
                        if len(between_brackets):
                            commands.append(between_brackets)

                    if x_string == '+':
                        combine_with_next = True
                else:
                    grab_command = ''
                    if combine_with_next:
                        new_commands = []
                        for id_xy, command in enumerate(commands):
                            if id_xy != len(commands) -1:
                                new_commands.append(command)
                            else:
                                grab_command = command
                        commands = new_commands
                    for idx, split_a_string in enumerate(split_string_on_action):
                        if idx == 0 and add_to_first:
                            if grab_command != '':
                                commands.append([*between_brackets, *get_setPlus_split(split_a_string), add_to_first, *grab_command])
                            else:
                                commands.append([*between_brackets, *get_setPlus_split(split_a_string), add_to_first])
                        elif idx == len(split_string_on_action) and add_to_last:
                            commands.append([*between_brackets, *get_setPlus_split(split_a_string), add_to_last])
                        else:
                            commands.append([*between_brackets, *get_setPlus_split(split_a_string)])
            elif curr_key[1:2] != '/':
                between_brackets = [x for x in check_if_between_brackets(current_ind) if x != curr_key]
                if between_brackets:
                    commands.append([*between_brackets, curr_key])
                # commands.append([*between_brackets, split_string_on_action])
                # print(current_ind, check_if_between_brackets(current_ind), between_combo_keys(current_ind, current_ind+1), curr_key)
        else:
            commands = [[x] for x in mysplit(x_string)]
    if len(replaced_dict):
        commands = update_commands(replaced_dict)
    new_commands = []
    for command_x in commands:
        new_combo_keys = []
        for combo_key in command_x:
            new_combo_keys.append(remove_brackets(combo_key))
        new_commands.append(new_combo_keys)
    return new_commands

def remove_brackets(input_string):
    try:
        return re.findall('(?<=<).*?(?=>)', input_string)[0].lower()
    except IndexError:
        return input_string.lower()

def init_macros():
    rows = pull_macros()
    listeners = pull_listeners()
    for listener in listeners:
        # functools.partial
        keyboard.add_word_listener(listener[0], functools.partial(run_command, listener))
        # keyboard.add_word_listener(listener[0],lambda: run_command(listener))
    for row in rows:
        if row[5]:
            act_key = '+'.join(interpret_command(row[3])[0])
            keyboard.add_hotkey(act_key, activate_macro, args=(row[0], row[4]))

            # row_commands = pull_commands(row[0])
            # print(row_commands)
            # for macro_command in row_commands:
            #     print("macro_command", macro_command)
            #     print("interp_comm", interpret_command(macro_command[2]))

def get_image_loc(inp_image):
    img_x = inp_image.split(',')[1]
    image_64_decode = base64.b64decode(img_x) 
    image_result = open("imageToLocate.png", 'wb') # create a writable image and write the decoding result
    image_result.write(image_64_decode)
    image_result.close()
    time.sleep(1)
    loc_x = pyautogui.locateOnScreen("imageToLocate.png")
    print('loc_x', loc_x)
    return loc_x

class MyPopup():
    def __init__(self,assign_to_val, label_text):
        self.value = assign_to_val
        self.master = tkinter.Tk()
        self.master.title("tkinter popup")
        tkinter.Label(self.master, text=label_text).grid(row=0)

        self.e1 = tkinter.Entry(self.master)
        self.e1.grid(row=0, column=1)
        tkinter.Button(self.master, text='Submit', command=self.submitx).grid(row=3, column=1, sticky=tkinter.W, pady=4)
        self.master.mainloop()
    def save_value(self):
        self.value = self.e1.get()
    def submitx(self):
        self.save_value()
        self.ensure_exit()
    def ensure_exit(self):
        self.master.update()
        self.master.destroy()
        # self.master.quit()
        # self.master = ""

def show_popup(question):
    global popupvar123456789
    val = ""
    popupvar123456789 = MyPopup(val, question)
    return_Val = popupvar123456789.value
    return return_Val

def activate_command(comm_x, delay, all_commands=False):
    if comm_x[1] == 'type_command':
        global interp_comm
        if comm_x[2].split("|")[0] == "input_string":
            interp_comm = interpret_command(comm_x[2].split("|")[1])
        else:
            exec(f'interp_comm = interpret_command({comm_x[2].split("|")[1]})', globals())
        for key_combo in interp_comm:
            const_keys = [k for k in key_combo if len(k) > 1]
            not_const_keys = [k for k in key_combo if len(k) == 1]

            for key in const_keys:
                keyboard.press(key)
            for key in not_const_keys:
                keyboard.press(key)
            for key in not_const_keys:
                keyboard.release(key)
            for key in const_keys[::-1]:
                keyboard.release(key)

            if delay == 'rand':
                time.sleep(randrange(3))
            else:
                time.sleep(float(delay))
    elif comm_x[1] == "mousemove":
        if comm_x[2].split('|')[0] == "toimage":
            image_64_decode = base64.b64decode(comm_x[2].split('|')[1].split(',')[1]) 
            image_result = open("imageToSave.png", 'wb') # create a writable image and write the decoding result
            image_result.write(image_64_decode)
            image_result.close()

            # button7location = pyautogui.locateOnScreen("imageToSave.png")
            # print("button7location", button7location)
            # point = pyautogui.center(button7location)
            # point_x, point_y = point
            point_x, point_y = pyautogui.locateCenterOnScreen("imageToSave.png")
            pyautogui.moveTo(point_x, point_y)
            # pyautogui.click(point_x, point_y) 
        elif comm_x[2].split('|')[0] == "tocoordinates":
            pyautogui.move(int(comm_x[2].split('|')[1].split('*')[0]), int(comm_x[2].split('|')[1].split('*')[1]), 0.2, pyautogui.easeInQuad)
    elif comm_x[1] == "click":
        pyautogui.click(button=comm_x[2].split('|')[0], clicks=int(comm_x[2].split('|')[1]))
    elif comm_x[1] == "mouse_scroll":
        pyautogui.scroll(int(comm_x[2]))
    elif comm_x[1] == "delay":
        if comm_x[2].split('|')[0] == "image":
            image_64_decode = base64.b64decode(comm_x[2].split('|')[1].split(',')[1]) 
            image_result = open("imageDelay.png", 'wb') # create a writable image and write the decoding result
            image_result.write(image_64_decode)
            image_result.close()
            while not pyautogui.locateCenterOnScreen("imageDelay.png"):
                time.sleep(0.2)
        elif comm_x[2].split('|')[0] == "prompt":
            pyautogui.alert(text='Execution paused...', title='Delay', button='OK')
        else:
            time.sleep(int(comm_x[2].split('|')[1]))
    elif comm_x[1] == "clipboard":
        if comm_x[2].split('|')[0] == "post":
            exec(f'pyperclip.copy({comm_x[2].split("|")[1]})')
        else:
            exec(f'{comm_x[2].split("|")[1]}=pyperclip.paste()', globals())
    elif comm_x[1] == "prompt_input":
        exec(f'{comm_x[2].split("|")[1]} = show_popup("{comm_x[2].split("|")[0]}")', globals())
        exec(f'print(len(list(filter(None, {comm_x[2].split("|")[1]}.split("\\n")))))')
        exec(
        'newline_split = []\n' \
        'tab_split = []\n' \
        f'newline_split = list(filter(None, {comm_x[2].split("|")[1]}.split("\\n")))\n' \
        'if len(newline_split) > 1:\n' \
        '    for linex in newline_split:\n' \
        f'        tab_split.append(list(filter(None, linex.split("\\t"))))\n' \
        'if len(newline_split) <= 1:\n' \
        f'    tab_split = [list(filter(None, {comm_x[2].split("|")[1]}.split("\\t"))),["stop_here"]]\n' \
        'if len(tab_split) > 1:\n' \
        f'    {comm_x[2].split("|")[1]} = tab_split'
        , globals()
        )
        print('tab_split', tab_split)
        # list(filter(None, str_list))
    elif comm_x[1] == "python_function":
        if comm_x[2].split('|')[1] != '':
            exec(f'{comm_x[2].split("|")[2]} = {comm_x[2].split("|")[0]}({comm_x[2].split("|")[1]})', globals())
        else:
            exec(f'{comm_x[2].split("|")[2]} = {comm_x[2].split("|")[0]}()', globals())
    elif comm_x[1] == "loop_start":
        exec(
        f'for {comm_x[2].split("|")[2]} in {comm_x[2].split("|")[1]}:\n' \
        '    start_comm_found = False\n' \
        '    end_comm_found = False\n' \
        f'    for loop_command in {all_commands}:\n' \
        f'        if {comm_x[2].split("|")[2]}[0] != "stop_here":\n' \
        '            if start_comm_found and not end_comm_found:\n' \
        f'                activate_command(loop_command, {delay}, {all_commands})\n' \
        f'            if loop_command[1] == "loop_start":\n' \
        f'                if loop_command[2].split("|")[0] == "{comm_x[2].split("|")[0]}":\n' \
        '                    start_comm_found = True\n' \
        f'            if loop_command[1] == "loop_end":\n' \
        f'                if loop_command[2] == "{comm_x[2].split("|")[0]}":\n' \
        '                    end_comm_found = True', globals())
    elif comm_x[1] == "loop_end":
        pass
    else:
        print(f"Command type ({comm_x[1]}) not yet supported.")
        print(comm_x[2])

def activate_macro(macro_name, delay):
    print(f"activated {macro_name}")
    row_commands = pull_commands(macro_name)
    print(row_commands)
    in_loops = []
    time.sleep(1)
    for macro_command in row_commands:
        if macro_command[1] == 'loop_end':
            in_loops.remove(macro_command[2])
        if len(in_loops) == 0 or macro_command[1] == 'loop_start':
            if macro_command[1] == 'loop_start':
                in_loops.append(macro_command[2].split("|")[0])
            activate_command(macro_command, delay, row_commands)

if __name__ == "__main__":
    # this_string = "<SHIFT>hello</SHIFT><ENTER>my name"
    # this_string = "<CTRL>aa+b</CTRL>a<SHIFT>+a<SHIFT>b+<CTRL></SHIFT>a</CTRL>"
    # this_string = "<CTRL><SHIFT>+a+b</CTRL>"
    # this_string = "<CTRL><SHIFT></CTRL>+a"
    # this_string = "<SHIFT><CTRL></SHIFT>+a"
    this_string = "<CTRL><SHIFT>+a</CTRL>"
    # this_string = "<SHIFT>+<CTRL><SHIFT>+a"
    # this_string = "b<ctrl><alt>+e</ctrl><ctrl>+c+d<ctrl>+<alt>+a"
    # this_string = "Common2<tab>+a"
    # this_string = "Comm on2<TAB>"
    # this_string = "<CTRL><SHIFT></CTRL>a</SHIFT>a+a"
    # this_string = "<CTRL><SHIFT></CTRL>a</SHIFT>a+b"
    # this_string = "<SHIFT><TAB><ENTER><TAB><TAB></SHIFT>"
    # this_string = "<CTRL>a<SHIFT></CTRL>b+c</SHIFT>"

    # this_string = "<SHIFT>b+<CTRL>+a</SHIFT>"
                # =
    # this_string = "<SHIFT><CTRL>ba</CTRL></SHIFT>"
    print(interpret_command(this_string))
    print(remove_brackets(this_string))