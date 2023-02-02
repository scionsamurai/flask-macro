import sqlite3


conn = sqlite3.connect("scraper.db")

cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS User;")
cursor.execute("CREATE TABLE User (username TEXT, password TEXT)")
cursor.execute("INSERT INTO User VALUES ('admin', 'test123')")
# cursor.execute("INSERT INTO ScraperItems VALUES ('s10', 'weeks', 1, 1, 0)")

cursor.execute("DROP TABLE IF EXISTS Macro;")
cursor.execute("CREATE TABLE Macro (name TEXT, tags TEXT, description TEXT, activation_key TEXT, interval TEXT, enabled INTEGER, date_added INTEGER, last_edited INTEGER)")
cursor.execute("INSERT INTO Macro VALUES ('Family Link', 'family,link,search', 'for searching for family link', '<ctrl>+r','rand',0,0,0)")
cursor.execute("INSERT INTO Macro VALUES ('HX Search', 'HX,ID,search', 'for searching for HX ID', '<ctrl>+t','0.5',0,0,0)")
cursor.execute("INSERT INTO Macro VALUES ('work macro', 'does,more,than,search', 'for more STUFF!', '<ctrl>0</ctrl>','0.5',1,0,0)")

cursor.execute("DROP TABLE IF EXISTS Commands;")
cursor.execute("CREATE TABLE Commands (name TEXT, command_id INTEGER, command_type TEXT, command TEXT)")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 0, 'type_command', 'input_string|<CTRL>+c or <CTRL>c</CTRL>')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 1, 'type_command', 'variable|secondcommands')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 2, 'mousemove', 'tocoordinates|0*0')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 3, 'mousemove', 'toimage|x')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 4, 'click', 'left|2')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 5, 'click', 'right|1')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 6, 'mouse_scroll', '1')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 7, 'delay', 'seconds|1')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 8, 'delay', 'image|x')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 9, 'clipboard', 'post|1')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 10, 'prompt_input', 'question|var')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 11, 'python_function', 'func_name|func_var_input|assign_to_name')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 12, 'loop_start', 'func_name|func_var_input|assign_to_name')")
cursor.execute("INSERT INTO Commands VALUES ('Family Link', 13, 'loop_end', 'assign_to_name')")

cursor.execute("INSERT INTO Commands VALUES ('HX Search', 0, 'type_command', 'somecommands')")
cursor.execute("INSERT INTO Commands VALUES ('HX Search', 1, 'click', 'secondcommands')")

cursor.execute("DROP TABLE IF EXISTS Listeners;")
cursor.execute("CREATE TABLE Listeners (listen_for TEXT, command TEXT)")
cursor.execute("INSERT INTO Listeners VALUES ('@email', '<CTRL>c</CTRL>')")
cursor.execute("INSERT INTO Listeners VALUES ('@yes', 'no')")

cursor.execute("DROP TABLE IF EXISTS Images;")

cursor.execute("DROP TABLE IF EXISTS RegionCheck;")
cursor.execute("CREATE TABLE RegionCheck (region_id INTEGER, region_image TEXT)")

conn.commit()

rows = cursor.execute("SELECT * FROM User WHERE username='admin'").fetchall()
print("rows", rows)

# cursor.execute("UPDATE ScraperItems set running = 0 WHERE query = 'leaf' ").fetchall()
# conn.commit()
# rows = cursor.execute("SELECT query, freq, freq_num, running, last_pull FROM ScraperItems").fetchall()
# print("rows2", rows)
cursor.close()
conn.close()

