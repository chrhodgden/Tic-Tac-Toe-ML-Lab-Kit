from menu import *
from entry_list import *
from entry import *
from analysis_board import *
from random import *
from time import time

def rnd(i = 1): return randint(0,i)

class Bot():
	def __init__(self, name, entry, plr_list=None):
		self.color_int = 7
		self.is_machine = True
		self.name = name
		# bots go at the end of the list
		self.plr_list = plr_list
		self.alg_1 = self.no_alg
		self.alg_2 = self.no_alg
		self.alg_3 = self.no_alg
		self.alg_4 = self.no_alg
		self.alg_5 = self.no_alg
		# initialize a menu and set it to self.menu
		self.param_alg_1 = Param('1st Algorithm', self.alg_name_list, setr_meth=self.set_alg_1)
		self.param_alg_2 = Param('2nd Algorithm', self.alg_name_list, setr_meth=self.set_alg_2)
		self.param_alg_3 = Param('3rd Algorithm', self.alg_name_list, setr_meth=self.set_alg_3)
		self.param_alg_4 = Param('4th Algorithm', self.alg_name_list, setr_meth=self.set_alg_4)
		self.param_alg_5 = Param('5th Algorithm', self.alg_name_list, setr_meth=self.set_alg_5)
		self.param_alg_1.item = self.alg_1.__name__
		self.param_alg_2.item = self.alg_2.__name__
		self.param_alg_3.item = self.alg_3.__name__
		self.param_alg_4.item = self.alg_4.__name__
		self.param_alg_5.item = self.alg_5.__name__
		self.entries = EntryList([self.param_alg_1, self.param_alg_2, self.param_alg_3, self.param_alg_4, self.param_alg_5])
		self.prompt = f"Edit {self.name}'s Settings"
		self.menu = Menu(self.prompt, self.entries)
		self.entry = entry
		entry.text = name
		entry.item = self.menu
		self.board = AnalysisBoard()
	
	@property
	def text_color(self):
		if self.color_int > 0 and self.color_int <=7:
			return f'\033[9{self.color_int}m'

	@property
	def indicate_color(self):
		if self.color_int > 0 and self.color_int <=7:
			return f'\033[10{self.color_int}m\033[30m'

	def set_alg_1(self, alg_name): self.alg_1 = self.alg_list[self.alg_name_list.index(alg_name)]
	def set_alg_2(self, alg_name): self.alg_2 = self.alg_list[self.alg_name_list.index(alg_name)]
	def set_alg_3(self, alg_name): self.alg_3 = self.alg_list[self.alg_name_list.index(alg_name)]
	def set_alg_4(self, alg_name): self.alg_4 = self.alg_list[self.alg_name_list.index(alg_name)]
	def set_alg_5(self, alg_name): self.alg_5 = self.alg_list[self.alg_name_list.index(alg_name)]
		
	@property
	def alg_list(self):
		lst = []
		for att in dir(self):
			if len(att) >= 5:
				if att[-4:] == '_alg' or att[:5] == 'rand_':
					lst.append(getattr(self, att)) 
		return lst

	@property
	def alg_name_list(self):
		lst = []
		for alg in self.alg_list:
			lst.append(alg.__name__)
		return lst

	def rand_fr(self): return choice('abc') + choice('123')

	def rand_sqr(self): return choice(['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3'])

	def rand_lgl(self): return choice(self.board.legal_moves)

	def no_alg(self): return ''

	def tiar_alg(self):
		sqr_nm = ''
		row_names = self.board.row_names
		shuffle(row_names)
		for row_name in row_names:
			if self.board.row_dict[row_name].count(self.board.turn) == 2 and self.board.row_dict[row_name].count(' ') == 1: 
				pos = self.board.row_dict[row_name].index(' ')
				sqr_nms = self.board.__getattribute__(f'row_{row_name}_sqr_nms')
				sqr_nm = sqr_nms[pos]

		return sqr_nm

	def block_alg(self):
		sqr_nm = ''
		row_names = self.board.row_names
		shuffle(row_names)
		for row_name in row_names:
			if self.board.row_dict[row_name].count(self.board.alt_turn) == 2 and self.board.row_dict[row_name].count(' ') == 1: 
				pos = self.board.row_dict[row_name].index(' ')
				sqr_nms = self.board.__getattribute__(f'row_{row_name}_sqr_nms')
				sqr_nm = sqr_nms[pos]

		return sqr_nm
	
	def build_alg(self):
		sqr_nm = ''
		row_names = self.board.row_names
		shuffle(row_names)
		for row_name in row_names:
			if self.board.row_dict[row_name].count(self.board.turn) == 1 and self.board.row_dict[row_name].count(' ') == 2: 
				rng_ind = [0, 1, 2]
				pos = self.board.row_dict[row_name].index(self.board.turn)
				rng_ind.remove(pos)
				sqr_nms = self.board.__getattribute__(f'row_{row_name}_sqr_nms')
				sqr_nm = sqr_nms[rng_ind[rnd()]]

		return sqr_nm

	def fork_alg(self):
		sqr_nm = ''
		sn = self.board.all_sqr_nms
		shuffle(sn)
		for s in sn:
			if self.board.all_sqrs_dict[s] == self.board.turn:
				s_2 = ''
				for s_0 in sn:
					if s_0 != s and self.board.all_sqrs_dict[s_0] == self.board.turn: s_2 = s_0
				if s_2 != '':
					rows_s_1 = self.board.sqr_rows[s]
					rows_s_2 = self.board.sqr_rows[s_2]
					for q in sn:
						if self.board.all_sqrs_dict[q] == ' ':
							row_q_1 = ''
							row_q_2 = ''
							for row_q in self.board.sqr_rows[q]:
								if row_q in rows_s_1 and self.board.row_dict[row_q].count(' ') == 2 and self.board.row_dict[row_q].count(self.board.turn) == 1:
									row_q_1 = row_q
								if row_q in rows_s_2 and self.board.row_dict[row_q].count(' ') == 2 and self.board.row_dict[row_q].count(self.board.turn) == 1:
									row_q_2 = row_q
							pass
							if row_q_1 != '' and row_q_2 != '':
								sqr_nm = q

		return sqr_nm

	def move(self, fen_board):
		sqr_nm = ''
		self.board.fen_board = fen_board
		if sqr_nm == '': sqr_nm = self.alg_1()
		if sqr_nm == '': sqr_nm = self.alg_2()
		if sqr_nm == '': sqr_nm = self.alg_3()
		if sqr_nm == '': sqr_nm = self.alg_4()
		if sqr_nm == '': sqr_nm = self.alg_5()
		self.board.fen_board = '3/3/3'
		return sqr_nm

