# A reports section would be nice.

from sqlite3 import *
from csv import *
import os
from menu import *
from entry_list import *
from entry import *
from access_methods import *
from analysis_board import *
from random import *
from subprocess import *
import importlib 
import idlelib

class Player():
	def __init__(self, color_int, name, is_machine, entry, menu=None, plr_list=None):
		self.color_int = color_int
		self.is_machine = is_machine
		self.entry = entry
		self.name = name
		entry.text = name
		self.plr_list = plr_list
		if menu != None:
			self.menu = menu
			self.entries = menu.entries
			menu.entries.entries[0].setr_meth = self.set_name
			menu.entries.entries[1].setr_meth = self.set_machine
			self.param_name = menu.entries.entries[0]
			self.param_is_machine = menu.entries.entries[1]
			self.prompt = f"Edit {self.name}'s Settings"
		else:
			# initialize a menu and set it to self.menu
			self.param_name = Param('Name', name, color_int, setr_meth=self.set_name)
			self.param_is_machine = Param('AI', [False, True], color_int, setr_meth=self.set_machine)
			self.param_is_machine.item = is_machine
			self.entries = EntryList([self.param_name, self.param_is_machine])
			self.prompt = f"Edit {self.name}'s Settings"
			self.menu = Menu(self.prompt, self.entries, entry.color_int)
		self.menu.side_bar = None
		entry.item = self.menu

	@property
	def __dict__(self):
		d = {}
		d['name'] = self.name
		d['color_int'] = self.color_int
		d['is_machine'] = self.is_machine
		if hasattr(self, 'alg_1'): d['alg_1'] = self.alg_1.__name__
		if hasattr(self, 'alg_2'): d['alg_2'] = self.alg_2.__name__
		if hasattr(self, 'alg_3'): d['alg_3'] = self.alg_3.__name__
		if hasattr(self, 'export_alg_res'): d['export_alg_res'] = self.export_alg_res
		return d
	
	@property
	def text_color(self):
		if self.color_int > 0 and self.color_int <=7:
			return f'\033[9{self.color_int}m'

	@property
	def indicate_color(self):
		if self.color_int > 0 and self.color_int <=7:
			return f'\033[10{self.color_int}m\033[30m'

	def save_file(self):
		con = connect('games.db')
		cur = con.cursor()
		
		upd_qry_sql = """
		UPDATE players
		SET name = :name, is_machine = :is_machine
		WHERE color_int = :color_int
		"""
		
		cur.execute(upd_qry_sql, self.__dict__)
		
		con.commit()
		con = None
		cur = None
		
	# I want to store a getter method as like an attribute, but have the stored value be the method and not the returned value of the method, that way the stored value returns the updated value when called.
	def set_name(self, new_name):
		self.name = new_name
		self.save_file()
		self.entry.text = new_name
		self.prompt = f"Edit {self.name}'s Settings"
		self.menu.prompt = self.prompt
		if hasattr(self, 'post'):
			self.menu.side_bar = self.post
		else:
			self.menu.side_bar = None
	
	def set_machine(self, is_machine):
		if is_machine:
			self = Machine(self.color_int, self.name, is_machine, self.entry, self.menu, self.plr_list)
		elif not is_machine:
			self = Player(self.color_int, self.name, is_machine, self.entry, self.menu, self.plr_list)
			# Will need to remove Machine specific Entry objects in self.entries and self.menu.entries
			self.entries.remove_entry(self.entries.entries[-1])
			self.entries.remove_entry(self.entries.entries[-1])
			self.entries.remove_entry(self.entries.entries[-1])
			self.entries.remove_entry(self.entries.entries[-1])
			self.entries.remove_entry(self.entries.entries[-1])
			self.entries.remove_entry(self.entries.entries[-1])
			self.menu.entries = self.entries
		
		self.plr_list[self.color_int-1] = self

		self.save_file()

# Add params that conrtol move step processes (best move & random)
# Add launcher that pre-aggregates decision model per fen_board
class Machine(Player):
	def __init__(self, color_int, name, is_machine, entry, menu=None, plr_list=None):
		super().__init__(color_int, name, is_machine, entry, menu, plr_list)
		self.load_machine_settings()
		self.param_alg_1 = Param('1st Algorithm', self.alg_name_list, color_int, setr_meth=self.set_alg_1)
		self.param_alg_2 = Param('2nd Algorithm', self.alg_name_list, color_int, setr_meth=self.set_alg_2)
		self.param_alg_3 = Param('3rd Algorithm', self.alg_name_list, color_int, setr_meth=self.set_alg_3)
		self.param_alg_1.item = self.alg_1.__name__
		self.param_alg_2.item = self.alg_2.__name__
		self.param_alg_3.item = self.alg_3.__name__
		self.param_export_alg_res = Param('Export Alg', [False, True], color_int, setr_meth=self.set_export_alg_res)
		self.param_export_alg_res.item = self.export_alg_res
		self.static_alg_gen = Launcher('Generate Static Algorithm', self.static_alg_generate, color_int)
		self.static_alg_edt = Launcher('Edit Static Algorithm', self.static_alg_edit, color_int)
		self.entries.add_entry(self.param_alg_1)
		self.entries.add_entry(self.param_alg_2)
		self.entries.add_entry(self.param_alg_3)
		self.entries.add_entry(self.param_export_alg_res)
		self.entries.add_entry(self.static_alg_gen)
		self.entries.add_entry(self.static_alg_edt)
		self.menu.entries = self.entries
		self.menu.side_bar = self.post
		self.bad_moves = []
		self.on_alg_num = 0
		self.board = AnalysisBoard()

	def set_alg_1(self, alg_name):
		self.alg_1 = self.alg_list[self.alg_name_list.index(alg_name)]
		self.save_machine_settings()
	
	def set_alg_2(self, alg_name):
		self.alg_2 = self.alg_list[self.alg_name_list.index(alg_name)]
		self.save_machine_settings()
	
	def set_alg_3(self, alg_name):
		self.alg_3 = self.alg_list[self.alg_name_list.index(alg_name)]
		self.save_machine_settings()
	
	def set_export_alg_res(self, export_alg_res):
		self.export_alg_res = export_alg_res
		self.save_machine_settings()
	
	def save_machine_settings(self):
		con = connect('games.db')
		cur = con.cursor()
		
		upd_qry_sql = """
		UPDATE machines
		SET name = :name, is_machine = :is_machine, alg_1 = :alg_1, alg_2 = :alg_2, alg_3 = :alg_3, export_alg_res = :export_alg_res
		WHERE color_int = :color_int
		"""
		
		cur.execute(upd_qry_sql, self.__dict__)
		
		con.commit()
		con = None
		cur = None

	def load_machine_settings(self):
		con = connect('games.db')
		qry_sql = """
		SELECT *
		FROM machines
		WHERE color_int = :color_int
		"""

		rcd = OpenRecordset(con, qry_sql, self.__dict__)[0]

		self.alg_1 = self.alg_list[self.alg_name_list.index(rcd['alg_1'])]
		self.alg_2 = self.alg_list[self.alg_name_list.index(rcd['alg_2'])]
		self.alg_3 = self.alg_list[self.alg_name_list.index(rcd['alg_3'])]
		self.export_alg_res = bool(rcd['export_alg_res'])

		con = None
		
	def static_alg_generate(self):
		con = connect('games.db')
		static_script = open(f'{self.name}_{self.color_int}_static_alg.py', 'w', newline='')
		static_script.write("def static_alg(fen_board=None):\n")
		static_script.write("\tsqr_nm = ''\n\n")
		static_script.write("##\tdemo board\n")
		static_script.write("##\tif fen_board == None:\n")
		static_script.write("##\t\tfen_board = '3/3/3'\n\n")

		static_script.write("\tif fen_board == None: sqr_nm = ''\n")

		qry_sql = """
		SELECT DISTINCT board
		FROM game_log INNER JOIN move_log ON game_log.game_id = move_log.game_id
		WHERE 
			(
				plr_X_name = :name
				AND plr_X_color_int = :color_int
				AND turn = 'X'
			)
			OR
			(
				plr_O_name = :name
				AND plr_O_color_int = :color_int
				AND turn = 'O'
			)
		"""
		param = self.__dict__

		boards = OpenRecordset(con, qry_sql, param)

		for board in boards:
			sqr_nm = ''
			sqr_nm = self.move(board['board'])
			if sqr_nm != '':
				static_script.write(f"\tif fen_board == '{board['board']}': sqr_nm = '{sqr_nm}'\n")

		static_script.write("\n\treturn sqr_nm\n")
	
	def static_alg_edit(self):
		static_script = os.path.join(os.getcwd(),f'{self.name}_{self.color_int}_static_alg.py')
		if os.path.exists(static_script):
			idle_bat = idlelib.__file__.replace('__init__.py','idle.bat')
			Popen(f'{idle_bat} "{static_script}"')


	@property
	def post(self):
		return f'{self.name}:\nHello World!\nI am {self}.\nMy name is {self.name}.'
	
	@property
	def alg_list(self):
		lst = []
		for att in dir(self):
			if len(att) >= 5:
				if att[-4:] == '_alg' or att[:5] == 'rand_':
					lst.append(getattr(self, att)) 
		return lst

	# should we have distinct sub_alg select and sort_alg select?
	# straight field names is one list to select for sort alg
	@property
	def alg_name_list(self):
		lst = []
		for alg in self.alg_list:
			lst.append(alg.__name__)
		return lst

	def rand_fr(self, fen_board): return choice('abc') + choice('123')

	def rand_sqr(self, fen_board): return choice(['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3'])

	def rand_lgl(self, fen_board): return choice(self.board.legal_moves)

	def rand_rem(self, fen_board): 
		legal_moves = self.board.legal_moves
		if len(self.bad_moves) > 0:
			for move in self.bad_moves:
				legal_moves.remove(move)
		pass
		# for when all moves are losing
		if legal_moves == []:
			legal_moves = self.board.legal_moves
		return choice(legal_moves)

	def no_alg(self, fen_board): return ''

	def static_alg(self, fen_board): 
		sqr_nm = ''
		static_script = os.path.join(os.getcwd(),f'{self.name}_{self.color_int}_static_alg.py')
		if os.path.exists(static_script):
			static_mod_name = f"{self.name}_{self.color_int}_static_alg"
			static_alg_module = importlib.import_module(static_mod_name, package=None)
			sqr_nm = static_alg_module.static_alg(fen_board)

		return sqr_nm

	def w_alg(self, fen_board): 
		sqr_nm = ''
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): return f'{ce}'
		sort_alg = '(win_count)'
		sqr_nm = self.find_wdl_alg_move(fen_board, wdl_ces, sub_alg, sort_alg)
		return sqr_nm
	
	# This algorithm works.
	# the machine can get stuck in bad habits.
	# can get stuck in a loop against a different ML alg
	# would like a dynamic way of aggregating past results
	def wml_mte_alg(self, fen_board): 
		sqr_nm = ''
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): return f'({ce} / ((game_log.turns + 1) - move_log.turn_num))'
		sort_alg = '(sum_net_factor)'
		sqr_nm = self.find_wdl_alg_move(fen_board, wdl_ces, sub_alg, sort_alg)		
		return sqr_nm

	# if turns-to-end = total-turns => 100% chance do that move
	# if turns-to-end = opponent's next turn => 100% chance do not do that move
	# it will only use previous moves, even if losing
	def eg_alg(self, fen_board): 
		sqr_nm = ''
		clean_chk = False
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): 
			sa = f"""(CASE
				WHEN game_log.turns = move_log.turn_num THEN {ce}
				WHEN game_log.turns = move_log.turn_num + 1 THEN {ce}
				ELSE NULL
				END)"""
			sa = sa.replace('\n',' ')			
			sa = sa.replace('\t','')			
			return sa
		sort_alg = '(sum_net_factor)'
		prev_move_set = self.find_wdl_alg_move_set(fen_board, wdl_ces, sub_alg, sort_alg)

		if prev_move_set != None:
			if len(prev_move_set) > 0:
				if prev_move_set[0] != None:
					if prev_move_set[0]['move'] != None:
						clean_chk = True

		if clean_chk:
			for move in prev_move_set:
				if move[sort_alg[1:-1]] != None:
					if move[sort_alg[1:-1]] > 0.0:
						if sqr_nm == '':
							sqr_nm = move['move']
					elif move[sort_alg[1:-1]] < 0.0:
						self.bad_moves.append(move['move'])
		
		# sqr_nm = self.find_wdl_alg_move(fen_board, wdl_ces, sub_alg, sort_alg)		
		return sqr_nm

	# I am wanting to know which moves gets me to a known winning position or which move getss me to an all-losing position
	# do we build a loop that queries each current legal move to generate a list of possible fen_boards from past games, then run those through the eg_alg?
	# or one query that can aggragate the results
		# will have to group by cur_next_move, then by next_board, aggregate the results on the next_boards, then somehow aggregate the results up to cur_next_move.

	def m_out_1_alg(self, fen_board): 
		sqr_nm = ''
		clean_chk = False
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): 
			sa = f"""(CASE
				WHEN game_log.turns = move_log.turn_num THEN {ce}
				WHEN game_log.turns = move_log.turn_num + 1 THEN {ce}
				ELSE NULL
				END)"""
			sa = sa.replace('\n',' ')			
			sa = sa.replace('\t','')			
			return sa
		sort_alg = '(sum_net_factor)'
		prev_move_set = self.find_wdl_alg_move_set(fen_board, wdl_ces, sub_alg, sort_alg)

		if prev_move_set != None:
			if len(prev_move_set) > 0:
				if prev_move_set[0] != None:
					if prev_move_set[0]['move'] != None:
						clean_chk = True

		if clean_chk:
			for move in prev_move_set:
				if move[sort_alg[1:-1]] != None:
					if move[sort_alg[1:-1]] > 0.0:
						if sqr_nm == '':
							sqr_nm = move['move']
					elif move[sort_alg[1:-1]] < 0.0:
						self.bad_moves.append(move['move'])
		
		# sqr_nm = self.find_wdl_alg_move(fen_board, wdl_ces, sub_alg, sort_alg)		
		return sqr_nm

	# create a dc_rem_alg that filters out known bad moves?
	def dc_alg(self, fen_board): 
		sqr_nm = ''
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): return f'{ce}'
		sort_alg = '(-move_count)'
		legal_moves = self.board.legal_moves
		prev_move_set = self.find_wdl_alg_move_set(fen_board, wdl_ces, sub_alg, sort_alg)

		for mov_p in prev_move_set:
			legal_moves.remove(mov_p['move'])

		if legal_moves == []:
			if prev_move_set != None:
				if len(prev_move_set) > 0:
					if prev_move_set[0] != None:
						if prev_move_set[0]['move'] != None:
							sqr_nm = prev_move_set[0]['move']
		else:
			sqr_nm = legal_moves[0]
		
		return sqr_nm

	def dc_rem_alg(self, fen_board): 
		sqr_nm = ''
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): return f'{ce}'
		sort_alg = '(-move_count)'
		legal_moves = self.board.legal_moves
		prev_move_set = self.find_wdl_alg_move_set(fen_board, wdl_ces, sub_alg, sort_alg)
		prev_move_set_0 = prev_move_set

		for mov_p in prev_move_set:
			legal_moves.remove(mov_p['move'])

		if legal_moves == []:
			if prev_move_set != None:
				if len(prev_move_set) > 0:
					if prev_move_set[0] != None:
						if prev_move_set[0]['move'] != None:
							if len(self.bad_moves) > 0:
								for move in prev_move_set_0:
									if move['move'] in self.bad_moves:
										prev_move_set_0.remove(move)			
							pass
							if len(prev_move_set_0) > 0:
								sqr_nm = prev_move_set_0[0]['move']
							else:
								sqr_nm = prev_move_set[0]['move']
		else:
			sqr_nm = legal_moves[0]
		
		return sqr_nm

	def wml_alg(self, fen_board): 
		sqr_nm = ''
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): return f'{ce}'
		sort_alg = '(win_count - loss_count)'
		sqr_nm = self.find_wdl_alg_move(fen_board, wdl_ces, sub_alg, sort_alg)
		return sqr_nm

	def wol_alg(self, fen_board): 
		sqr_nm = ''
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): return f'{ce}'
		sort_alg = '(win_count / (CASE WHEN loss_count = 0 THEN 0.5 ELSE loss_count END))'
		sqr_nm = self.find_wdl_alg_move(fen_board, wdl_ces, sub_alg, sort_alg)
		return sqr_nm

	def lmw_alg(self, fen_board): 
		sqr_nm = ''
		wdl_ces = [1.0, 0.0, -1.0]
		def sub_alg(ce): return f'{ce}'
		sort_alg = '(loss_count - win_count)'
		sqr_nm = self.find_wdl_alg_move(fen_board, wdl_ces, sub_alg, sort_alg)
		return sqr_nm
	
	def find_wdl_alg_move(self, fen_board, wdl_ces, sub_alg, sort_alg):
		sqr_nm = ''
		clean_chk = False
		move_set = self.find_wdl_alg_move_set(fen_board, wdl_ces, sub_alg, sort_alg)
		
		if move_set != None:
			if len(move_set) > 0:
				if move_set[0] != None:
					if move_set[0]['move'] != None:
						clean_chk = True

		if clean_chk:
			if len(self.bad_moves) > 0:
				for move in move_set:
					if move['move'] in self.bad_moves:
						move_set.remove(move)			
			pass
			if len(move_set) > 0:
				sqr_nm = move_set[0]['move']

		return sqr_nm

	def find_wdl_alg_move_set(self, fen_board, wdl_ces, sub_alg, sort_alg):
		con = connect('games.db')

		w_cond = sub_alg(wdl_ces[0])
		d_cond = sub_alg(wdl_ces[1])
		l_cond = sub_alg(wdl_ces[2])
	
		qry_sql = open('alg_move.sql','r').read()

		qry_sql = qry_sql.replace('plr_X_', f'plr_{self.board.turn}_')
		qry_sql = qry_sql.replace('(1.0 / 1.0)', w_cond)
		qry_sql = qry_sql.replace('(0.0 / 1.0)', d_cond)
		qry_sql = qry_sql.replace('(-1.0 / 1.0)', l_cond)
		qry_sql = qry_sql.replace('(win_count - loss_count)', sort_alg)

		param = {
			'plr_name': self.name,
			'plr_color_int': self.color_int,
			'fen_board': fen_board
		}

		move_set = OpenRecordset(con, qry_sql, param)
		
		if self.export_alg_res: self.log_alg_move(qry_sql, param, move_set)

		con = None
		return move_set
	
	def log_alg_move(self, qry_sql, param, move_set):
		
		# we'll figure  out where to put these later
		# will need to update the .txt output for sqlite3.dll to read correct correct directory
		# if not os.path.exists(os.path.join(os.getcwd(), 'alg_export')): os.mkdir('alg_export')
		# os.chdir(os.path.join(os.getcwd(), 'alg_export'))

		open(f'alg_move_{self.on_alg_num}.sql','w', newline='').write(qry_sql)

		txt_writer = open(f'alg_move_{self.on_alg_num}.txt','w',newline='')
		txt_writer.write('.open games.db\n')
		txt_writer.write('.mode box\n')
		txt_writer.write('.parameter init\n')
		for fld in param:
			txt_writer.write(f'.parameter set :{fld} {param[fld]}\n')
		txt_writer.write(f'.read alg_move_{self.on_alg_num}.sql')
		txt_writer = None

		if move_set != None:
			if len(move_set) > 0:
				if move_set[0] != None:
					if move_set[0]['move'] != None:
						csv_writer = DictWriter(open(f'alg_move_{self.on_alg_num}.csv','w',newline=''), fieldnames=move_set[0].keys())
						csv_writer.writeheader()
						for move in move_set:
							csv_writer.writerow(move)
		csv_writer = None

	def move(self, fen_board):
		sqr_nm = ''
		self.board.fen_board = fen_board
		self.bad_moves = []
		self.on_alg_num = 0
		if sqr_nm == '':
			self.on_alg_num = 1
			sqr_nm = self.alg_1(fen_board)
		if sqr_nm == '':
			self.on_alg_num = 2
			sqr_nm = self.alg_2(fen_board)
		if sqr_nm == '':
			self.on_alg_num = 3
			sqr_nm = self.alg_3(fen_board)
		self.bad_moves = []
		self.on_alg_num = 0
		self.board.fen_board = '3/3/3'
		return sqr_nm




		

	


