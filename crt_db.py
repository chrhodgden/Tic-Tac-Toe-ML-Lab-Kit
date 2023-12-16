from sqlite3 import *
import os

db_name = 'games.db'

if os.path.exists(os.path.join(os.getcwd(), 'games.db')): os.remove('games.db')

con = connect('games.db')
cur = con.cursor()

game_log_fld_types = {
	'game_id': 'Integer',
	'plr_X_name': 'Text',
	'plr_X_color_int': 'Integer',
	'plr_O_name': 'Text',
	'plr_O_color_int': 'Integer',
	'start_time': 'Real',
	'start_board': 'Text',
	'vic_chk': 'Integer',
	'victor_name': 'Text',
	'victor_color_int': 'Integer',
	'three_in_a_row': 'Integer',
	'draw_accept': 'Integer',
	'resign': 'Integer',
	'end_board': 'Text',
	'turns': 'Integer',
	'end_time': 'Real'
}

crt_flds = ''
for k in game_log_fld_types:
	crt_flds += f'{k} {game_log_fld_types[k]}, '
crt_flds = crt_flds[:-2]

qry_crt_game_log = f'CREATE TABLE game_log ({crt_flds})'
cur.execute(qry_crt_game_log)

move_log_fld_types = {
	'game_id': 'Integer',
	'board': 'Text',
	'turn': 'Text',
	'move_num': 'Integer',
	'turn_num': 'Integer',
	'move': 'Text',
	'timestamp': 'Real'
}

crt_flds = ''
for k in move_log_fld_types:
	crt_flds += f'{k} {move_log_fld_types[k]}, '
crt_flds = crt_flds[:-2]

qry_crt_move_log = f'CREATE TABLE move_log ({crt_flds})'
cur.execute(qry_crt_move_log)

players_fld_types = {
	'color_int': 'Integer',
	'name': 'Text',
	'is_machine': 'Integer' 
}

crt_flds = ''
for k in players_fld_types:
	crt_flds += f'{k} {players_fld_types[k]}, '
crt_flds = crt_flds[:-2]

qry_crt_players = f'CREATE TABLE players ({crt_flds})'
cur.execute(qry_crt_players)

plrs = [
	{'color_int': 1, 'name': 'Red', 'is_machine': False},
	{'color_int': 2, 'name': 'Green', 'is_machine': False},
	{'color_int': 3, 'name': 'Yellow', 'is_machine': False},
	{'color_int': 4, 'name': 'Blue', 'is_machine': False},
	{'color_int': 5, 'name': 'Magenta', 'is_machine': False},
	{'color_int': 6, 'name': 'Cyan', 'is_machine': False},
]

qry_app_players = """INSERT INTO players (color_int, name, is_machine)
VALUES (:color_int, :name, :is_machine)"""

for plr in plrs:
	cur.execute(qry_app_players, plr)

machines_fld_types = {
	'color_int': 'Integer',
	'name': 'Text',
	'is_machine': 'Integer',
	'alg_1': 'Text',
	'alg_2': 'Text',
	'alg_3': 'Text',
	'export_alg_res': 'Integer'
}

crt_flds = ''
for k in machines_fld_types:
	crt_flds += f'{k} {machines_fld_types[k]}, '
crt_flds = crt_flds[:-2]

qry_crt_machines = f'CREATE TABLE machines ({crt_flds})'
cur.execute(qry_crt_machines)

machines = [
	{'color_int': 1, 'name': 'Red', 'is_machine': False, 'alg_1': 'no_alg', 'alg_2': 'no_alg', 'alg_3': 'no_alg', 'export_alg_res': False},
	{'color_int': 2, 'name': 'Green', 'is_machine': False, 'alg_1': 'no_alg', 'alg_2': 'no_alg', 'alg_3': 'no_alg', 'export_alg_res': False},
	{'color_int': 3, 'name': 'Yellow', 'is_machine': False, 'alg_1': 'no_alg', 'alg_2': 'no_alg', 'alg_3': 'no_alg', 'export_alg_res': False},
	{'color_int': 4, 'name': 'Blue', 'is_machine': False, 'alg_1': 'no_alg', 'alg_2': 'no_alg', 'alg_3': 'no_alg', 'export_alg_res': False},
	{'color_int': 5, 'name': 'Magenta', 'is_machine': False, 'alg_1': 'no_alg', 'alg_2': 'no_alg', 'alg_3': 'no_alg', 'export_alg_res': False},
	{'color_int': 6, 'name': 'Cyan', 'is_machine': False, 'alg_1': 'no_alg', 'alg_2': 'no_alg', 'alg_3': 'no_alg', 'export_alg_res': False},
]

qry_app_machine = """INSERT INTO machines (color_int, name, is_machine, alg_1, alg_2, alg_3, export_alg_res)
VALUES (:color_int, :name, :is_machine, :alg_1, :alg_2, :alg_3, :export_alg_res)"""

for machine in machines:
	cur.execute(qry_app_machine, machine)

con.commit()
con.close()
con = None
cur = None