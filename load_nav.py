from csv import *
from sqlite3 import *
from entry import *
from entry_list import *
from menu import *
from player import *
from board import *
from bot import *
from access_methods import *

def launch_game(plr_1, plr_2):
	size = lab_entry_4.item
	game_board = Board(plr_1, plr_2, size=size)
	game_board.play()
	if plr_1.is_machine and plr_2.is_machine:
		input()

def launch_games(plr_1, plr_2, game_count):
	size = lab_entry_4.item
	wdl_stats_param = {
		'plr_1_name': plr_1.name,
		'plr_1_color_int': plr_1.color_int,
		'plr_1_text_color': plr_1.text_color,
		'plr_2_name': plr_2.name,
		'plr_2_color_int': plr_2.color_int,
		'plr_2_text_color': plr_2.text_color,
	}

	for i in range(game_count):
		if kbhit():
			ks = [getch()]
			if kbhit(): ks.append(getch())
			if ks == [b'\x1b']:
				# would like an options dialogue here
				break
		if i % 2 == 0:
			game_board = Board(plr_1, plr_2, wdl_stats_param, size=size)
			game_board.play()
		else:
			game_board = Board(plr_2, plr_1, wdl_stats_param, size=size)
			game_board.play()
	if plr_1.is_machine and plr_2.is_machine:
		input()

con = connect('games.db')
cur = con.cursor()

# Main Menu
mm_prompt = 'Main Menu'

mm_entry_1 = Entry('Play')
mm_entry_2 = Entry('Laboratory')
mm_entry_3 = Entry('Story Mode')
mm_entry_4 = Entry('Profiles')
mm_entry_5 = Entry('Control Bot Profiles')

mm_entries = EntryList([mm_entry_1, mm_entry_2, mm_entry_3, mm_entry_4, mm_entry_5])

mm_menu = Menu(mm_prompt, mm_entries)


# Story Mode
story_prompt = 'Select Human User and AI Machine and complete the challenges together.'

story_entry_1 = Entry('User')
story_entry_2 = Entry('Machine')
story_entry_3 = Entry('Challenges')

story_entries = EntryList([story_entry_1, story_entry_2, story_entry_3])

story_menu = Menu(story_prompt, story_entries)

# Profiles menu
prof_prompt = 'Manage User and AI profiles.'

prof_entry_1 = Entry('Red', color_int=1)
prof_entry_3 = Entry('Yellow', color_int=3)
prof_entry_2 = Entry('Green', color_int=2)
prof_entry_6 = Entry('Cyan', color_int=6)
prof_entry_4 = Entry('Blue', color_int=4)
prof_entry_5 = Entry('Magenta', color_int=5)

prof_entries = EntryList([prof_entry_1, prof_entry_3, prof_entry_2, prof_entry_6, prof_entry_4, prof_entry_5])

prof_menu = Menu(prof_prompt, prof_entries)

# Bot Menu
bot_prompt = 'Edit Bot Settings'

bot_1_entry = Entry('Bot 1')
bot_2_entry = Entry('Bot 2')

bot_entries = EntryList([bot_1_entry, bot_2_entry])

bot_menu = Menu(bot_prompt, bot_entries)

# Load Entries
mm_entry_3.item = story_menu
mm_entry_4.item = prof_menu
mm_entry_5.item = bot_menu

# initialize players
# set thier menu attribute to color entry.item

rst = OpenRecordset(con, "SELECT * FROM players")

for rcd in rst:
	rcd['is_machine'] = bool(rcd['is_machine'])
	if rcd['is_machine']: rcd['cls'] = Machine
	else: rcd['cls'] = Player

plr_1 = rst[0]['cls'](rst[0]['color_int'], rst[0]['name'], rst[0]['is_machine'], prof_entry_1)
plr_2 = rst[1]['cls'](rst[1]['color_int'], rst[1]['name'], rst[1]['is_machine'], prof_entry_2)
plr_3 = rst[2]['cls'](rst[2]['color_int'], rst[2]['name'], rst[2]['is_machine'], prof_entry_3)
plr_4 = rst[3]['cls'](rst[3]['color_int'], rst[3]['name'], rst[3]['is_machine'], prof_entry_4)
plr_5 = rst[4]['cls'](rst[4]['color_int'], rst[4]['name'], rst[4]['is_machine'], prof_entry_5)
plr_6 = rst[5]['cls'](rst[5]['color_int'], rst[5]['name'], rst[5]['is_machine'], prof_entry_6)

bot_1 = Bot('Bot 1', bot_1_entry)
bot_2 = Bot('Bot 2', bot_2_entry)

# I would like to find an alternative to a player list being an attribute of all the players
# class method/attribute?
plr_list = [plr_1, plr_2, plr_3, plr_4, plr_5, plr_6, bot_1, bot_2]

plr_1.plr_list = plr_list
plr_2.plr_list = plr_list
plr_3.plr_list = plr_list
plr_4.plr_list = plr_list
plr_5.plr_list = plr_list
plr_6.plr_list = plr_list
bot_1.plr_list = plr_list
bot_2.plr_list = plr_list

prof_entry_1.item = plr_1.menu
prof_entry_2.item = plr_2.menu
prof_entry_3.item = plr_3.menu
prof_entry_4.item = plr_4.menu
prof_entry_5.item = plr_5.menu
prof_entry_6.item = plr_6.menu
bot_1_entry.item = bot_1.menu
bot_2_entry.item = bot_2.menu

# do we have to define the get_players() getter method after the players have been initialized?
def get_players():
	players = []
	for entry in prof_entries.entries:
		players.append(entry.text)
	for entry in bot_entries.entries:
		players.append(entry.text)
	return players

def set_plrs_getr(plr_param, alt_plr_param):
	def get_plrs():
		players = []
		for entry in prof_entries.entries:
			if entry.color_int != alt_plr_param.itm_color_int:
				players.append(entry.text)
		for entry in bot_entries.entries:
			if entry.text != alt_plr_param.item:
				players.append(entry.text)
		return players
	return get_plrs

# there is a bug if 2 or more profiles have the same name
def set_plr_setr(param):
	def set_plr(plr_name):
		clr_i = None
		for entry in prof_entries.entries:
			if entry.text == plr_name:
				clr_i = entry.color_int
		for entry in bot_entries.entries:
			if entry.text == plr_name:
				clr_i = entry.color_int
		param.itm_color_int = clr_i
	return set_plr

# Play/Lab Menu
play_prompt = 'Play Menu'
lab_prompt = 'Welcome to the Laboratory!'

init_plrs = get_players()

lab_plr_1 = Param('Player 1', init_val=init_plrs)
lab_plr_2 = Param('Player 2', init_val=init_plrs)
lab_plr_1.setr_meth = set_plr_setr(lab_plr_1)
lab_plr_2.setr_meth = set_plr_setr(lab_plr_2)
lab_plr_1.getr_meth = set_plrs_getr(lab_plr_1, lab_plr_2)
lab_plr_2.getr_meth = set_plrs_getr(lab_plr_2, lab_plr_1)
lab_plr_1.set_item(lab_plr_1.item)
lab_plr_2.set_item(lab_plr_2.item)
lab_plr_2.get_options()
lab_plr_1.get_options()

def get_game_players():
	global plr_list
	for plr in plr_list:
		if lab_plr_1.item == plr.name: game_plr_1 = plr
		if lab_plr_2.item == plr.name: game_plr_2 = plr
	return [game_plr_1, game_plr_2]

play_entry_3 = Launcher('Play', launch_game, args_getr_meth=get_game_players)
lab_entry_3 = Param('Games', 10)
lab_entry_4 = Param('Board Size', [2, 1])

def get_series_settings():
	args = get_game_players()
	args.append(int(lab_entry_3.item))
	return args

lab_entry_5 = Launcher('Play Games', launch_games, args_getr_meth=get_series_settings)
lab_entry_6 = Entry('Help')
lab_entry_7 = Entry('Reports')

play_entries = EntryList([lab_plr_1, lab_plr_2, lab_entry_4, play_entry_3])
lab_entries = EntryList([lab_plr_1, lab_plr_2, lab_entry_3, lab_entry_4, lab_entry_5, lab_entry_6, lab_entry_7])

play_menu = Menu(play_prompt, play_entries)
lab_menu = Menu(lab_prompt, lab_entries)

mm_entry_1.item = play_menu
mm_entry_2.item = lab_menu





