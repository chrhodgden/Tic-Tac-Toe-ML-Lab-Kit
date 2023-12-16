from load_nav import *

menu_tree = [None, None, mm_menu]

while True:

	# if next item is the previous item, remove next item and current item and load the previous item
	if menu_tree[-1] == menu_tree[-3]:
		menu_tree.pop(-1)
		menu_tree.pop(-1)

	if menu_tree[-1] == None:
		# quit program
		break
	elif type(menu_tree[-1]) is Launcher:
		menu_tree[-1].launch()
		menu_tree.pop(-1)
	elif type(menu_tree[-1]) is Menu:
		menu_tree[-1].open(prev_menu=menu_tree[-2])
		menu_tree[-1].clear()
		menu_tree.append(menu_tree[-1].next_item)

