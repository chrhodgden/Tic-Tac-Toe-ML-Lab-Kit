# check if the entry.py and time modules are being used. Remove import if not.
from msvcrt import *
from entry import *
from time import *

class Menu():
	def __init__(self, prompt, entries, color_int=7, side_bar=None):
		self.prompt = prompt
		self.entries = entries
		self.iter_entries = iter(entries)
		self.color_int = color_int
		self.next_item = None
		self.side_bar = side_bar

	@property
	def text_color(self):
		if self.color_int > 0 and self.color_int <=7:
			return f'\033[9{self.color_int}m'

	@property
	def indicate_color(self):
		if self.color_int > 0 and self.color_int <=7:
			return f'\033[10{self.color_int}m\033[30m'
		
	def refresh(self):
		if self.color_int == 7: color_int = None
		else: color_int = self.color_int
		self.text = '\n'
		if color_int: self.text += f'\033[9{color_int}m'
		self.text += self.prompt
		self.text += '\n' * 2
		for entry in self.entries:	
			if hasattr(entry, 'get_options'):
				entry.get_options()
			self.text += '\t' + entry.indicate(color_int) 
			if color_int: self.text += f'\033[9{color_int}m'
			self.text += '\n'
		self.text += '\n'
	
	def open(self, prev_menu):
		self.clear()
		self.prev_menu = prev_menu
		self.next_item = None
		self.entries.set_select()
		self.refresh()
		self.print_side_bar()
		print(self.text)
		self.keyboard_nav()

	def clear(self):
		print('\033[0m', '\033[?25l', '\033[2J', '\033[0;0f', sep='', end='')

	def reprint(self):
		self.clear()
		self.print_side_bar()
		print(self.text)
	
	def print_side_bar(self):		
		if self.side_bar:
			lines = self.side_bar.split('\n')
			l = 2
			for line in lines:
				print(f'\033[{l};40f', f'\033[9{self.color_int}m', line, '\033[0m', sep='', end='')
				l+=1
			print('\033[0;0f', end='')


	def nav_entries(self, next='NEXT'):
		self.entries.nav(next)
		self.refresh()
		self.reprint()


	def edit_param(self, param):
		param.edit = True
		self.refresh()
		self.reprint()
		param.keyboard_edit()
		param.edit = False
		self.refresh()
		self.reprint()

	def keyboard_nav(self):
		while True:
			cmd = getch()
			if cmd == b'\x1b' or cmd == b'\x08':
				self.next_item = self.prev_menu
				break
			elif cmd == b'\x00' or cmd == b'\xe0':
				cmd = getch()
				if cmd == b'M' or cmd == b'P':
					self.nav_entries(next='NEXT')
				elif cmd == b'K' or cmd == b'H':
					self.nav_entries(next='PREV')
			elif cmd == b'\t':
					self.nav_entries(next='NEXT')
			elif cmd == b'\r':
				for entry in self.entries:
					if entry.select and type(entry) is Param:
						self.edit_param(entry)
					elif entry.select:
						self.next_item = entry.item
				if self.next_item != None:
					break







		
	
	