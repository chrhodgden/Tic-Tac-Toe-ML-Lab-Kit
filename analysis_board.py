class AnalysisBoard():
	def __init__(self, fen_board='3/3/3'):
		self.file_name = ['a', 'b', 'c']
		self.rank_name = ['1', '2', '3']
		self.diag_name = ['a1_c3', 'a3_c1']
		self.fen_board = fen_board
	
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
	def all_sqr_nms(self): return ['a1', 'a2', 'a3', 'b1', 'b2', 'b3', 'c1', 'c2', 'c3']

	@property
	def all_sqrs_dict(self): return dict(zip(self.all_sqr_nms, self.all_sqr_vals))

	@property
	def sqr_nms(self): 
		return [
			['a1', 'a2', 'a3'],
			['b1', 'b2', 'b3'],
			['c1', 'c2', 'c3']
		]

	@property
	def turn(self):
		if self.all_sqr_vals.count('X') <= self.all_sqr_vals.count('O'): return 'X'
		elif self.all_sqr_vals.count('X') > self.all_sqr_vals.count('O'): return 'O'

	@property
	def alt_turn(self):
		if self.all_sqr_vals.count('X') <= self.all_sqr_vals.count('O'): return 'O'
		elif self.all_sqr_vals.count('X') > self.all_sqr_vals.count('O'): return 'X'

	@property
	def legal_moves(self):
		legal_moves = []
		for f in range(3):
			for r in range(3):
				if self.board[f][r] == ' ': legal_moves.append('abc'[f] + '123'[r])
		return legal_moves

	@property
	def move_num(self): return self.all_sqr_vals.count('O') + 1
	
	@property
	def turn_num(self): return 10 - self.all_sqr_vals.count(' ')

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
	def sqr_rows(self):
		sr = {}
		for sqr_nm in self.all_sqr_nms:
			rows = [sqr_nm[0], sqr_nm[1]]
			if sqr_nm in self.row_a1_c3_sqr_nms: rows.append('a1_c3')
			if sqr_nm in self.row_a3_c1_sqr_nms: rows.append('a3_c1')
			sr[sqr_nm] = rows
		return sr

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
	def row_a3_c1_dict(self): return dict(zip(self.row_a3_c1_sqr_nms, self.row_a3_c1))

	@property
	def files(self): return self.board
	@property
	def ranks(self):return [self.row_1, self.row_2, self.row_3]
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

	def sqr_val(self, sqr_nm):
		f = self.file_name.index(sqr_nm[0])
		r = self.rank_name.index(sqr_nm[1])
		return self.board[f][r]
	