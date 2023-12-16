# NOTES:
# Look into subclasses
#	- Report()
#		- should this be a Menu subclass?
# 	- ReportSummary() & ReportDetail()
#	- ReportSummary puts a stat in the item fiels like Param does.
#	- ReportDetail prints new lines with columns and rows on .indicate()
#	- I do not want to select a report entry. So doesn't need to be an EntryList?
#	- I would like some connectivity to Param entries that would change the report args

from msvcrt import *

class Entry():
	def __init__(self, text, color_int=7):
		self.text = text
		self.color_int = color_int
		self.select = False	

	@property
	def text_color(self):
		if self.color_int > 0 and self.color_int <=7:
			return f'\033[9{self.color_int}m'

	@property
	def indicate_color(self):
		if self.color_int > 0 and self.color_int <=7:
			return f'\033[10{self.color_int}m\033[30m'
	
	def indicate(self, color_int=None):
		color = '\033[0m'
		if self.select and color_int == None:
			color = f'\033[10{self.color_int}m\033[30m'
		elif self.select:
			color = f'\033[10{color_int}m\033[30m'
		elif not self.select and self.color_int != 7:
			color = f'\033[9{self.color_int}m'
		return color + ' ' + self.text + ' ' + '\033[0m'

class Launcher(Entry):
	def __init__(self, text, meth, color_int=7, args_getr_meth=None, *args, **kwargs):
		super().__init__(text, color_int)
		self.meth = meth
		self.color_int = color_int
		self.args_getr_meth = args_getr_meth
		self.args = args
		self.kwargs = kwargs

	@property
	def item(self):
		return self
	
	def get_args(self):
		if self.args_getr_meth != None:
			self.args = self.args_getr_meth()
	
	def launch(self):
		self.get_args()
		self.meth(*self.args)
	


# There are Params with a control list to select from
# There are Params that use input()
# Need to handle boolean values for toggle setting.
	# I could use existing list functionality passing a list [False, True]
	# My vision was to display a "box" with brakets and populate with a star [*] for True, [ ] for False.
class Param(Entry):
	def __init__(self, text, init_val=None, color_int=7, itm_color_int=None, setr_meth=None, getr_meth=None):
		super().__init__(text, color_int)
		if getr_meth != None:
			self.options = getr_meth()
			self.item = self.options[0]
		elif type(init_val) is list:
			self.options = init_val
			self.item = init_val[0]
		else:
			self.item = init_val
		self.edit = False
		self.itm_color_int = itm_color_int
		self.setr_meth = setr_meth
		self.getr_meth = getr_meth

	def set_item(self, new_val):
		self.item = new_val
		if self.setr_meth != None:
			self.setr_meth(new_val)

	def get_options(self):
		if self.getr_meth != None:
			self.options = self.getr_meth()
			if not self.item in self.options:
				self.set_item(self.options[0])

	def indicate(self, color_int=None):
		if self.color_int != 7:
			txt_clr_i = self.color_int
		elif color_int != None:
			txt_clr_i = color_int
		else:
			txt_clr_i = self.color_int
		
		if self.itm_color_int != None:
			itm_clr_i = self.itm_color_int
		else:
			itm_clr_i = txt_clr_i

		if self.select and self.edit:
			txt_color = f'\033[9{txt_clr_i}m'
			itm_color = f'\033[10{itm_clr_i}m\033[30m\033[s'
		elif self.select:
			txt_color = f'\033[10{txt_clr_i}m\033[30m'
			itm_color = f'\033[9{itm_clr_i}m'
		else:
			txt_color = f'\033[9{txt_clr_i}m'
			itm_color = f'\033[9{itm_clr_i}m'

		txt = ''
		if len(self.text) < 6:
			txt = f'{txt_color} {self.text} \033[0m\t\t'
		elif len(self.text) >= 6 and len(self.text) < 14:
			txt = f'{txt_color} {self.text} \033[0m\t'
		elif len(self.text) >= 14:
			txt = f'{txt_color} {self.text[0:15]} \033[0m'

		return f'''{txt}: {itm_color} {str(self.item)} \033[0m''' 
	
	# Using list indexes is lazy. I really want to "professionalize" the code by using iterator functionality. This would also handle other data types and custom class objects as well.
	def edit_item(self, next='NEXT'):
		if next == 'NEXT':
			next_ind = self.options.index(self.item) + 1
			if next_ind > (len(self.options) - 1):
				next_ind = 0
		elif next == 'PREV':
			next_ind = self.options.index(self.item) - 1
			if next_ind < 0:
				next_ind = len(self.options) - 1
		self.set_item(self.options[next_ind])

		if self.itm_color_int != None:
			itm_clr_i = self.itm_color_int
		else:
			itm_clr_i = self.color_int
		
		itm_color = f'\033[10{itm_clr_i}m\033[30m'
		print(f'\033[u{itm_color} {self.item} \033[0m', sep='')
	
	def keyboard_edit(self):
		itm_color = f'\033[10{self.color_int}m\033[30m'
		if hasattr(self, 'options'):
			self.get_options()
			while True:
				cmd = getch()
				if cmd == b'\x1b' or cmd == b'\x08' or cmd == b'\r':
					break
				elif cmd == b'\x00' or cmd == b'\xe0':
					cmd = getch()
					if cmd == b'M' or cmd == b'P':
						self.edit_item('NEXT')
					elif cmd == b'K' or cmd == b'H':
						self.edit_item('PREV')
				elif cmd == b'\t':
					self.edit_item('NEXT')
		else:
			# there are some UI improvements that could be made. you are typing over the old value on the screen.
			# I don't want it to clear the old value, I want it to wait for a keyboard command before clearing.
			# if we did that, we'd actually have to print that keystroke and put it in the self.item.
			new_val = input(f'\033[u{itm_color} ')
			if new_val: 
				self.set_item(new_val)
		



