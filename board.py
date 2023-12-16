# Notes:
# need to program game stats reporting
# then program the ML algorithm!
# should I program ultimate before story? Just to stretch the legs of the ML Algorithm?
# consider adding an excel doc in the project folder that presents the report. Won't work for machines without an excel reader. could have a text based report.

from msvcrt import *
from sqlite3 import *
import time
from access_methods import *

class Board:
	def __init__(self, plr_X, plr_O, wdl_stats=None, size=1):
		blank_file = [' ', ' ', ' ']
		self.file_name = ['a', 'b', 'c']
		self.rank_name = ['1', '2', '3']
		self.diag_name = ['a1_c3', 'a3_c1']
		self.board = [blank_file[:], blank_file[:], blank_file[:]]
		self.plr_X = plr_X
		self.plr_O = plr_O
		self.nav_sqr = 'a3'
		self.subtext_msg = ''
		self.dr_menu = False
		self.dr_entries = ['Offer Draw', 'Resign']
		self.nav_entry = ''
		self.draw_offer = False
		self.do_entries = ['Reject', 'Accept']
		self.draw_accept = False
		self.resign = False
		self.wdl_stats = wdl_stats
		self.size = size
		self.set_wdl_stats()
		self.start_log()

	@property
	def __dict__(self):
		d = {}
		for fn in self.file_name:
			fi = self.file_name.index(fn)
			d[fn] = {}
			for rn in self.rank_name:
				ri = self.rank_name.index(rn)
				d[fn][rn] = self.board[fi][ri]
		return d
	
	def start_log(self):
		con = connect('games.db')
		cur = con.cursor()
		res = cur.execute("""
			SELECT max(game_id) AS game_id
			FROM game_log
		""").fetchone()
		if res == None:
			game_id = 0
		else:
			game_id = Nz(res[0]) + 1
		self.move_log = []
		self.game_log = {
			'game_id': game_id, 
			'plr_X_name': self.plr_X.name, 
			'plr_X_color_int': self.plr_X.color_int, 
			'plr_O_name': self.plr_O.name, 
			'plr_O_color_int': self.plr_O.color_int, 
			'start_time': time.time(),
			'start_board': self.fen_board
		}

	@property
	def side_bar(self):
		msg = f'\t{self.plr_X.text_color}{self.plr_X.name}\033[0m'
		msg += f'\t{self.plr_O.text_color}{self.plr_O.name}\033[0m'
		i = 0
		for log in self.move_log:
			if i != log['move_num']:
				msg += f"\n{str(log['move_num'])}."
				i = log['move_num']
			if log['turn'] == 'X':
				msg += f"\t{self.plr_X.text_color}{log['move']}\033[0m"
			elif log['turn'] == 'O' and self.move_log[0]['turn'] == 'O' and log['move_num'] == self.move_log[0]['move_num']:
				msg += f"\t\t{self.plr_O.text_color}{log['move']}\033[0m"
			elif log['turn'] == 'O':
				msg += f"\t{self.plr_O.text_color}{log['move']}\033[0m"

		return msg
	
	@property
	def subtext(self):
		if self.vic_chk: return f'{self.victor.text_color}{self.victor.name} Wins!\033[0m'
		elif self.end_game_chk and not self.vic_chk: return 'Draw'
		elif self.draw_offer:
			st = 'Accept Draw Offer?\n\n'
			for entry in self.do_entries:
				if self.nav_entry == entry: st += self.plr_alt.indicate_color
				st += f'\t {entry} \033[0m'
			return st
		elif self.dr_menu:
			st = 'End Game Options:\n\n'
			for entry in self.dr_entries:
				if self.nav_entry == entry: st += self.plr_turn.indicate_color
				st += f'\t {entry} \033[0m'
			return st
		else: 
			st = f'{self.plr_turn.text_color}{self.plr_turn.name} to move'
			if self.subtext_msg: st += f'\n\n\t{self.subtext_msg}'
			return st

	@property
	def fen_board(self):
		fen = ''
		space_count = 0
		r = 0
		for rank in reversed(self.ranks):
			r += 1
			for sqr in rank:
				if sqr == ' ':
					space_count += 1
				else:
					if space_count != 0:
						fen += str(space_count)
						space_count = 0
					fen += sqr
			if space_count != 0:
				fen += str(space_count)
				space_count = 0
			if not r == 3:
				fen += '/'
		return fen
	
	@fen_board.setter
	def fen_board(self, fen):
		str_board = ''
		for s in fen.replace('/',''):
			if s.isnumeric(): str_board += int(s) * ' '
			else: str_board += s
		self.board = [
			[str_board[6], str_board[3], str_board[0]],
			[str_board[7], str_board[4], str_board[1]],
			[str_board[8], str_board[5], str_board[2]]
		]

	def sqr_val(self, sqr_nm):
		f = self.file_name.index(sqr_nm[0])
		r = self.rank_name.index(sqr_nm[1])
		return self.board[f][r]
	
	def is_vic_sqr(self, sqr_nm): return sqr_nm in self.vic_sqrs

	def dsp_sqr(self, sqr_nm):
		sqr_val = self.sqr_val(sqr_nm)
		color = ''
		if sqr_nm in self.vic_sqrs: 
			color = f'{self.victor.indicate_color}\033[30m'
		elif self.nav_sqr == sqr_nm: color = f'{self.plr_turn.indicate_color}\033[30m'
		elif sqr_val == 'X': color = f'{self.plr_X.text_color}'
		elif sqr_val == 'O': color = f'{self.plr_O.text_color}'
		return f'{color}{sqr_val}\033[40m\033[97m'

	#https://en.wikipedia.org/wiki/Code_page_437
	# full block: █
	# left block: ▌
	# rite block: ▐
	# vr box bar: │
	def dsp_intr_sqr(self, sqr_1, sqr_2):
		if sqr_1 in self.vic_sqrs and sqr_2 in self.vic_sqrs:
			return f'{self.victor.indicate_color}│\033[40m\033[97m'
		elif sqr_1 in self.vic_sqrs:
			return f'{self.victor.text_color}▌\033[40m\033[97m'
		elif sqr_2 in self.vic_sqrs:
			return f'{self.victor.text_color}▐\033[40m\033[97m'
		elif self.nav_sqr == sqr_1 and sqr_1 != '':
			return f'{self.plr_turn.text_color}▌\033[40m\033[97m'
		elif self.nav_sqr == sqr_2 and sqr_2 != '':
			return f'{self.plr_turn.text_color}▐\033[40m\033[97m'
		elif sqr_1 == '' or sqr_2 == '':
			return ' '
		else:
			return '│'

	def dsp_size_2(self):
		brd = []
		for rank in self.rank_name:
			rank_str = ''
			rank_str += self.dsp_intr_sqr('', 'a' + rank)
			if rank == '2' or rank == '3':
				rank_str += '\033[4m'
			rank_str += self.dsp_sqr('a' + rank)
			rank_str += self.dsp_intr_sqr('a' + rank, 'b' + rank)
			rank_str += self.dsp_sqr('b' + rank)
			rank_str += self.dsp_intr_sqr('b' + rank, 'c' + rank)
			rank_str += self.dsp_sqr('c' + rank)	
			if rank == '2' or rank == '3':
				rank_str += '\033[0m'
			rank_str += self.dsp_intr_sqr('c' + rank, '')
			brd.append(rank_str)
		return brd

	@property
	def all_sqr_vals(self):
		return [
			self.board[0][0],
			self.board[0][1],
			self.board[0][2],
			self.board[1][0],
			self.board[1][1],
			self.board[1][2],
			self.board[2][0],
			self.board[2][1],
			self.board[2][2]
		]

	@property
	def sqr_nms(self): 
		return [
			['a1', 'a2', 'a3'],
			['b1', 'b2', 'b3'],
			['c1', 'c2', 'c3']
		]

	@property
	def all_sqr_nms(self): return ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3']

	@property
	def all_sqrs_dict(self): return dict(zip(self.all_sqr_nms, self.all_sqr_vals))

	@property
	def plr_turn(self):
		if self.all_sqr_vals.count('X') <= self.all_sqr_vals.count('O'): return self.plr_X
		elif self.all_sqr_vals.count('X') > self.all_sqr_vals.count('O'): return self.plr_O

	@property
	def plr_alt(self):
		if self.all_sqr_vals.count('X') <= self.all_sqr_vals.count('O'): return self.plr_O
		elif self.all_sqr_vals.count('X') > self.all_sqr_vals.count('O'): return self.plr_X

	@property
	def move_num(self): return self.all_sqr_vals.count('O') + 1
	
	@property
	def turn_num(self): return 10 - self.all_sqr_vals.count(' ')
	
	@property
	def val_a1(self): return self.board[0][0]
	@property
	def val_a2(self): return self.board[0][1]
	@property
	def val_a3(self): return self.board[0][2]
	@property
	def val_b1(self): return self.board[1][0]
	@property
	def val_b2(self): return self.board[1][1]
	@property
	def val_b3(self): return self.board[1][2]
	@property
	def val_c1(self): return self.board[2][0]
	@property
	def val_c2(self): return self.board[2][1]
	@property
	def val_c3(self): return self.board[2][2]

	@property
	def dsp_a1(self): return self.dsp_sqr('a1')
	@property
	def dsp_a2(self): return self.dsp_sqr('a2')
	@property
	def dsp_a3(self): return self.dsp_sqr('a3')
	@property
	def dsp_b1(self): return self.dsp_sqr('b1')
	@property
	def dsp_b2(self): return self.dsp_sqr('b2')
	@property
	def dsp_b3(self): return self.dsp_sqr('b3')
	@property
	def dsp_c1(self): return self.dsp_sqr('c1')
	@property
	def dsp_c2(self): return self.dsp_sqr('c2')
	@property
	def dsp_c3(self): return self.dsp_sqr('c3')

	def __str__(self):
		if self.size == 1:
			s = f'''\033[40m\033[97m
	3 \033[4m{self.dsp_a3}│{self.dsp_b3}│{self.dsp_c3}\033[0m
	2 \033[4m{self.dsp_a2}│{self.dsp_b2}│{self.dsp_c2}\033[0m
	1 {self.dsp_a1}│{self.dsp_b1}│{self.dsp_c1}\033[0m
	  a b c'''
		elif self.size == 2:
			b = self.dsp_size_2()

			s = f'''\033[40m\033[97m
	3 {b[2]}\033[0m
	2 {b[1]}\033[0m
	1 {b[0]}\033[0m
	   a b c'''
			
		return s

	def display(self):
		print('\033[0m', '\033[?25l', '\033[2J', '\033[0;0f', sep='', end='')
		self.print_side_bar()
		print(f'{self.str_wdl_stats}{str(self)}\n\n\t{self.subtext}')
		self.subtext_msg = ''

	def set_wdl_stats(self):
		msg = ''
		if self.wdl_stats != None:
			con = connect('games.db')
			qry_wdl_stats = open('wdl_stats.sql','r').read()
			rst = OpenRecordset(con, qry_wdl_stats, self.wdl_stats)
			rcd = rst[0]
			for fld in rcd:
				if rcd[fld] == None: rcd[fld] = 0
			con = None
			msg = f"\t{rcd['plr_1_text_color']}{rcd['plr_1_name']}\033[0m"
			msg += f"\tDraw"
			msg += f"\t{rcd['plr_2_text_color']}{rcd['plr_2_name']}\033[0m"
			msg += f"\nX vs. O"
			msg += f"\t{rcd['plr_1_text_color']}{rcd['plr_1_X_wins']}\033[0m"
			msg += f"\t{rcd['game_X_O_draws']}"
			msg += f"\t{rcd['plr_2_text_color']}{rcd['plr_2_O_wins']}\033[0m"
			msg += f"\nO vs. X"
			msg += f"\t{rcd['plr_1_text_color']}{rcd['plr_1_O_wins']}\033[0m"
			msg += f"\t{rcd['game_O_X_draws']}"
			msg += f"\t{rcd['plr_2_text_color']}{rcd['plr_2_X_wins']}\033[0m"
			msg += f"\nTotal"
			msg += f"\t{rcd['plr_1_text_color']}{rcd['plr_1_X_wins']+rcd['plr_1_O_wins']}\033[0m"
			msg += f"\t{rcd['game_X_O_draws']+rcd['game_O_X_draws']}"
			msg += f"\t{rcd['plr_2_text_color']}{rcd['plr_2_O_wins']+rcd['plr_2_X_wins']}\033[0m"
			msg += f"\n"
		self.str_wdl_stats = msg

	def print_side_bar(self):		
		if self.side_bar:
			lines = self.side_bar.split('\n')
			l = 1
			for line in lines:
				print(f'\033[{l};35f', line, sep='', end='')
				l+=1
			print('\033[0;0f', end='')		

	@property
	def row_a(self): return self.board[0]
	@property
	def row_b(self): return self.board[1]
	@property
	def row_c(self): return self.board[2]
	@property
	def row_1(self): return [self.board[0][0], self.board[1][0], self.board[2][0]]
	@property
	def row_2(self): return [self.board[0][1], self.board[1][1], self.board[2][1]]
	@property
	def row_3(self): return [self.board[0][2], self.board[1][2], self.board[2][2]]
	@property
	def row_a1_c3(self): return [self.board[0][0], self.board[1][1], self.board[2][2]]
	@property
	def row_a3_c1(self): return [self.board[0][2], self.board[1][1], self.board[2][0]]

	@property
	def row_a_sqr_nms(self): return self.sqr_nms[0]
	@property
	def row_b_sqr_nms(self): return self.sqr_nms[1]
	@property
	def row_c_sqr_nms(self): return self.sqr_nms[2]
	@property
	def row_1_sqr_nms(self): return [self.sqr_nms[0][0], self.sqr_nms[1][0], self.sqr_nms[2][0]]
	@property
	def row_2_sqr_nms(self): return [self.sqr_nms[0][1], self.sqr_nms[1][1], self.sqr_nms[2][1]]
	@property
	def row_3_sqr_nms(self): return [self.sqr_nms[0][2], self.sqr_nms[1][2], self.sqr_nms[2][2]]
	@property
	def row_a1_c3_sqr_nms(self): return [self.sqr_nms[0][0], self.sqr_nms[1][1], self.sqr_nms[2][2]]
	@property
	def row_a3_c1_sqr_nms(self): return [self.sqr_nms[0][2], self.sqr_nms[1][1], self.sqr_nms[2][0]]

	@property
	def row_a_dict(self): return dict(zip(self.row_a_sqr_nms, self.row_a))
	@property
	def row_b_dict(self): return dict(zip(self.row_b_sqr_nms, self.row_b))
	@property
	def row_c_dict(self): return dict(zip(self.row_c_sqr_nms, self.row_c))
	@property
	def row_1_dict(self): return dict(zip(self.row_1_sqr_nms, self.row_1))
	@property
	def row_2_dict(self): return dict(zip(self.row_2_sqr_nms, self.row_2))
	@property
	def row_3_dict(self): return dict(zip(self.row_3_sqr_nms, self.row_3))
	@property
	def row_a1_c3_dict(self): return dict(zip(self.row_a1_c3_sqr_nms, self.row_a1_c3))
	@property
	def row_a3_c1_dict(self): return dict(zip(self.row_a1_c3_sqr_nms, self.row_a1_c3))

	@property
	def files(self): return self.board

	@property
	def ranks(self): return [self.row_1, self.row_2, self.row_3]

	@property
	def ranks_dict(self): 
		v = [self.row_1_dict, self.row_2_dict, self.row_3_dict]
		return dict(zip(self.rank_name, v))

	@property
	def diagonals(self): return [self.row_a1_c3, self.row_a3_c1]
		
	@property
	def rows(self):
		return [
			self.row_a,
			self.row_b,
			self.row_c,
			self.row_1,
			self.row_2,
			self.row_3,
			self.row_a1_c3,
			self.row_a3_c1
		]

	@property
	def row_dicts(self):
		return [
			self.row_a_dict,
			self.row_b_dict,
			self.row_c_dict,
			self.row_1_dict,
			self.row_2_dict,
			self.row_3_dict,
			self.row_a1_c3_dict,
			self.row_a3_c1_dict
		]

	@property
	def row_names(self): return self.file_name + self.rank_name + self.diag_name

	@property
	def row_dict(self): return dict(zip(self.row_names, self.rows))

	@property
	def row_dict_dicts(self): return dict(zip(self.row_names, self.row_dicts))

	@property
	def vic_chk(self):
		for rng in self.rows:
			if rng.count(rng[0]) == 3 and rng[0] != ' ': return True
		return self.resign
	
	@property
	def three_in_a_row_chk(self):
		for rng in self.rows:
			if rng.count(rng[0]) == 3 and rng[0] != ' ': return True
		return False
	
	@property
	def vic_sqrs(self):
		sqrs = []
		for i in range(3):
			if self.files[i].count(self.files[i][0]) == 3 and self.files[i][0] != ' ':
				for rnk_nm in self.rank_name: sqrs.append(self.file_name[i] + rnk_nm)
			if self.ranks[i].count(self.ranks[i][0]) == 3 and self.ranks[i][0] != ' ':
				for fil_nm in self.file_name: sqrs.append(fil_nm + self.rank_name[i])
		if self.row_a1_c3.count(self.row_a1_c3[0]) == 3 and self.row_a1_c3[0] != ' ':
			for i in range(3): sqrs.append(self.file_name[i] + self.rank_name[i])
		if self.row_a3_c1.count(self.row_a3_c1[0]) == 3 and self.row_a3_c1[0] != ' ':
			for i in range(3): sqrs.append(self.file_name[i] + self.rank_name[2-i])
		return sqrs

	@property
	def end_game_chk(self):
		return self.all_sqr_vals.count(' ') == 0 or self.vic_chk or self.draw_accept

	@property
	def victor(self):
		if self.three_in_a_row_chk:
			for rng in self.rows:
				if rng.count(rng[0]) == 3:
					if rng[0] == 'X': return self.plr_X
					elif rng[0] == 'O': return self.plr_O
		elif self.resign: return self.plr_alt
		return None

	@property
	def mark(self):
		if self.plr_turn == self.plr_X: return 'X'
		elif self.plr_turn == self.plr_O: return 'O'

	def log_move(self):
		i = len(self.move_log)
		self.move_log.append({'game_id': self.game_log['game_id']})
		self.move_log[i]['board'] = self.fen_board
		self.move_log[i]['turn'] = self.mark
		self.move_log[i]['move_num'] = self.move_num
		self.move_log[i]['turn_num'] = self.turn_num
		self.move_log[i]['move'] = self.nav_sqr
		self.move_log[i]['timestamp'] = time.time()

	def mark_sqr(self, sqr_nm=None):
		if sqr_nm != None: self.nav_sqr = sqr_nm
		f = self.file_name.index(self.nav_sqr[0])
		r = self.rank_name.index(self.nav_sqr[1])
		if self.board[f][r] == ' ': 
			self.log_move()
			self.board[f][r] = self.mark
			return True
		else:
			self.subtext_msg = 'Illegal Move'
			return False
	
	def draw_or_resign(self, ks):
		chk = False
		if not self.nav_entry in self.dr_entries: self.nav_entry = self.dr_entries[0]
		if ks == [b'\r']:
			if self.nav_entry == self.dr_entries[0]:
				self.draw_offer = True
				self.nav_entry = self.do_entries[0]
				chk = self.kb_nav(self.accept_draw)
				self.draw_offer = False
				self.nav_entry = self.dr_entries[0]
			elif self.nav_entry == self.dr_entries[1]:
				self.resign = True
				chk = True
		elif ks == [b'\x1b']:
			chk = True
		elif ks == [b'\t']: 
			self.nav_entry = self.dr_entries[self.dr_entries.index(self.nav_entry)-1]
		elif ks == [b'\x00', b'H'] or ks == [b'\xe0', b'H']: # Up
			self.nav_entry = self.dr_entries[self.dr_entries.index(self.nav_entry)-1]
		elif ks == [b'\x00', b'P'] or ks == [b'\xe0', b'P']: # Down
			self.nav_entry = self.dr_entries[self.dr_entries.index(self.nav_entry)-1]
		elif ks == [b'\x00', b'M'] or ks == [b'\xe0', b'M']: # Right
			self.nav_entry = self.dr_entries[self.dr_entries.index(self.nav_entry)-1]
		elif ks == [b'\x00', b'K'] or ks == [b'\xe0', b'K']: # Left
			self.nav_entry = self.dr_entries[self.dr_entries.index(self.nav_entry)-1]
		return chk
	
	def accept_draw(self, ks):
		chk = False
		if not self.nav_entry in self.do_entries: self.nav_entry = self.do_entries[0]
		if ks == [b'\r']:
			if self.nav_entry == self.do_entries[0]:
				self.draw_offer = False
				self.nav_entry = self.dr_entries[0]
				chk = True
			elif self.nav_entry == self.do_entries[1]:
				self.draw_accept = True
				chk = True
		elif ks == [b'\x1b']:
			self.draw_offer = False
			self.nav_entry = self.dr_entries[0]
			chk = True
		elif ks == [b'\t']: 
			self.nav_entry = self.do_entries[self.do_entries.index(self.nav_entry)-1]
		elif ks == [b'\x00', b'H'] or ks == [b'\xe0', b'H']: # Up
			self.nav_entry = self.do_entries[self.do_entries.index(self.nav_entry)-1]
		elif ks == [b'\x00', b'P'] or ks == [b'\xe0', b'P']: # Down
			self.nav_entry = self.do_entries[self.do_entries.index(self.nav_entry)-1]
		elif ks == [b'\x00', b'M'] or ks == [b'\xe0', b'M']: # Right
			self.nav_entry = self.do_entries[self.do_entries.index(self.nav_entry)-1]
		elif ks == [b'\x00', b'K'] or ks == [b'\xe0', b'K']: # Left
			self.nav_entry = self.do_entries[self.do_entries.index(self.nav_entry)-1]
		return chk

	def nav_board(self, ks):
		chk = False
		if self.nav_sqr == '': self.nav_sqr = 'a3'
		if ks == [b'\r']:
			chk = self.mark_sqr() 
		elif ks == [b'\x1b']:
			self.dr_menu = True
			self.nav_entry = self.dr_entries[0]
			chk = self.kb_nav(self.draw_or_resign) 
			self.nav_entry = ''
			self.dr_menu = False
		elif ks == [b'\t']:
			f = self.file_name.index(self.nav_sqr[0])
			r = self.rank_name.index(self.nav_sqr[1])
			if f == 2: 
				f = 0
				if r == 0: r = 2
				else: r -= 1
			else: f += 1
			self.nav_sqr = self.file_name[f] + self.rank_name[r]
		elif ks == [b'\x00', b'H'] or ks == [b'\xe0', b'H']: # Up
			pos = self.rank_name.index(self.nav_sqr[1])
			if pos == len(self.rank_name) - 1: pos = 0
			else: pos += 1
			self.nav_sqr = self.nav_sqr[0] + self.rank_name[pos]
		elif ks == [b'\x00', b'P'] or ks == [b'\xe0', b'P']: # Down
			pos = self.rank_name.index(self.nav_sqr[1])
			if pos == 0: pos = len(self.rank_name) - 1
			else: pos -= 1
			self.nav_sqr = self.nav_sqr[0] + self.rank_name[pos]
		elif ks == [b'\x00', b'M'] or ks == [b'\xe0', b'M']: # Right
			pos = self.file_name.index(self.nav_sqr[0])
			if pos == len(self.file_name) - 1: pos = 0
			else: pos += 1
			self.nav_sqr = self.file_name[pos] + self.nav_sqr[1]
		elif ks == [b'\x00', b'K'] or ks == [b'\xe0', b'K']: # Left
			pos = self.file_name.index(self.nav_sqr[0])
			if pos == 0: pos = len(self.file_name) - 1
			else: pos -= 1
			self.nav_sqr = self.file_name[pos] + self.nav_sqr[1]
		return chk
	
	def kb_nav(self, meth):
		chk = False
		while not chk:
			self.display()
			ks = [getch()]
			if kbhit(): ks.append(getch())
			chk = meth(ks)
		return chk
	
	def log_game(self):
		if len(self.move_log) > 0:
			con = connect('games.db')
			cur = con.cursor()

			app_game_log_sql = open('app_game_log.sql', 'r').read()
			cur.execute(app_game_log_sql, self.game_log)

			app_move_log_sql = open('app_move_log.sql', 'r').read()
			for log in self.move_log:
				cur.execute(app_move_log_sql, log)

			con.commit()
			con = None
			cur = None

	def play(self):
		while not self.end_game_chk:
			if not self.plr_turn.is_machine:
				if not self.kb_nav(self.nav_board): 
					break
			elif self.plr_turn.is_machine:
				self.display()
				sqr_nm = self.plr_turn.move(self.fen_board)
				self.mark_sqr(sqr_nm)

		self.nav_sqr = ''
		self.game_log['vic_chk'] = self.vic_chk
		if self.vic_chk:
			self.game_log['victor_name'] = self.victor.name
			self.game_log['victor_color_int'] = self.victor.color_int
		else:
			self.game_log['victor_name'] = ''
			self.game_log['victor_color_int'] = 0
		self.game_log['three_in_a_row'] = self.three_in_a_row_chk
		self.game_log['draw_accept'] = self.draw_accept
		self.game_log['resign'] = self.resign
		self.game_log['end_board'] = self.fen_board
		self.game_log['turns'] = self.turn_num - 1
		self.game_log['end_time'] = time.time()

		self.log_game()
		self.set_wdl_stats()
		self.display()
		if not self.plr_X.is_machine or not self.plr_O.is_machine:
			input()


	

	
