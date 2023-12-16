#Notes:
# There is a simplification opportinity to depreciate the EntryList class.
# because we are using list index funtionality and not iterator functionalit
# just put the Entry objects into a list object, then create a nav str object that is populated with Entry.text items.
# ks == [b'\r'] will loop to find entry.text == nav_str
# Should we keep EntryList, but move that functionality here?
# the entry.indicate() method is referencing entry.select. May need to keep the .select setter functionality.

class EntryList():
	def __init__(self, init_list):
		self.entries = init_list
		self.iter_entries = iter(init_list)
		self.entries[0].select = True
	
	def __iter__(self):
		self.iter_entries = iter(self.entries)
		return self.iter_entries

	def __next__(self):
		return next(self.iter_entries)
	
	# FOR THE LOVE OF GOD DEVS MAKE BACK A THING
	def __back__(self):
		pass

	def add_entry(self, entry):
		if not entry in self.entries:
			entry.select = False
			self.entries.append(entry)
			self.iter_entries = iter(self.entries)
			
	def remove_entry(self, entry):
		chk = False
		if entry in self.entries:
			chk = entry.select
			self.entries.remove(entry)
			self.iter_entries = iter(self.entries)
		if chk:
			self.entries[0].select = True

	def set_select(self):
		i = 0
		for entry in self.entries:
			entry.select = (i == 0)
			i += 1

	def nav(self, next = 'NEXT'):
		chk = False
		if next == 'NEXT':
			for entry in self.entries:
				if entry.select:
					chk = entry.select
					entry.select = False   
				elif chk:
					entry.select = chk
					chk = False
			self.entries[0].select = chk

		elif next == 'PREV':
			for entry in reversed(self.entries):
				if entry.select:
					chk = entry.select
					entry.select = False
				elif chk:
					entry.select = chk
					chk = False
			self.entries[-1].select = chk


	
