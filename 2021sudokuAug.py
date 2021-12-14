# go to C:\\Python_2018 (?)

# the class Sudoku takes in a (n x n) array with zeroes for blanks and an integer between 1 and n elsewhere, where n = GAME_SIZE
# and returns a (n x n) array where the zeroes are replaced with nonnegative integers
# such that each cell contains a single integer between 1 and n
# where no column contains duplicates, no row contains duplicates, and no gridded subsquare (box) contains duplicates

GAME_SIZE = 9
BOX_SIZE = 3

# import Set
import copy

# input array to Sudoku must be a list of lists
class Sudoku:

	# impossible_puzzle = 0

	def __init__(self, array, g_size=GAME_SIZE, b_size=BOX_SIZE):
		# self.impossible_puzzle = false
		self.impossible_puzzle = "false"
		self.g_size = g_size
		self.b_size = b_size
		self.grid = array
		self.one_elim_fill = "false"
		self.uniq_cand = "false"
		self.wrong_guess_hole = "false"
		self.guessing = "false"

		### keep and options are the bedrock. Keep, the list of uncertain cells, 
		### will be updated constantly with removal of certain fills. The same goes for options:
		### (by changing options to just "0")
		###
		self.keep = self.create_keep(array)
		self.options = self.create_options(array) 
		
		self.keep_ind = 0
		self.keep_length = len(self.keep)
		self.option_inds = self.create_option_inds() 

		self.one_elim_list = []
		self.uniq_cand_list = []

		# need a backup keep and options free of guesses
		#self.guess_keep = self.reset(self.keep)
		#self.guess_options = self.reset(self.options)
		self.backup_grid = copy.deepcopy(self.grid)
		self.backup_keep = copy.deepcopy(self.keep)
		self.backup_options = copy.deepcopy(self.options)
		self.guess_list = []
		self.first_elim_fill = 0
		self.first_uniq_fill = 0
		self.guess_seeds = []
		self.guess_seeds_trunc = []
		self.all_guess_seeds = []
		self.new_guess_start = "true"

	def __bool__(self):
		return self.impossible_puzzle != 0

	# below method creates a list of coordinates of all blank (zero) cells, 
	# so that we don't waste time combing through the already-filled starter cells
	def create_keep(self, array):
		# keeps = array
		# keeps.append([0])
		keeps = []
		for i in range(self.g_size):
			for j in range(self.g_size):
				if array[i][j] == 0:
					keeps.append((i,j))
		return keeps

	# below method creates array of all possibilities for each cell, with just the number "0" for starter cells
	def create_options(self, array):
		opts = []
		for i in range(self.g_size):
			opts.append([])
			for j in range(self.g_size):
				opts[i].append([])
				if array[i][j] == 0: # assuming the "blanks" in keep are populated with zeroes
					for k in range(1,self.g_size+1):
						# if self.in_row(i,k) or self.in_col(j,k) or self.in_box(i,j,k):
						if self.already_in(i,j,k):					
							continue
						opts[i][j].append(k)
					if not(opts[i][j]):
						self.impossible_puzzle = 1
				else:
					opts[i][j].append(0)
		return opts

	#def reset(self, src_list, dest_list):
	#	for elem in list:


	# the "leaving off" point for each cell as we are combing through possibilities
	def create_option_inds(self):
		inds = []
		for i in range(self.g_size):
			inds.append([])
			for j in range(self.g_size):
				inds[i].append(0)
		return inds

	# pretty self-explanatory - returns the row list
	def row(self, row):
		return self.grid[row]

	# returns column list
	def col(self, col):
		dummy_col = []
		for row in self.grid:
			dummy_col.append(row[col])
		return dummy_col

	# returns subsquare/box list
	def box(self, row, col):
		row_root = row // self.b_size
		col_root = col // self.b_size
		dummy_box = []
		for i in range(self.b_size):
			for j in range(self.b_size):
				dummy_box.append(self.grid[row_root*self.b_size+i][col_root*self.b_size+j])
		return dummy_box

	def solved(self):
		puzzle_complete = "true"
		for i in range(self.g_size):
			for j in range(self.g_size):
				if self.grid[i][j] == 0:
					puzzle_complete = "false"
					break
		return puzzle_complete


	# Boolean for whether the number is already in the row, column or box
	def already_in(self, row, col, num):
		return num in set(self.row(row)) | set(self.col(col)) | set(self.box(row, col))

	# all cells in row, column and box EXCEPT cells in self.guess_seeds
	def combine_surrounding_cells(self, row, col) -> set():
		combined_surr_cells = set()
		for key in self.keep:
			row_root = row // self.b_size
			col_root = col // self.b_size
			#if key not in self.guess_seeds_trunc:
			if key[0] == row or key[1] == col or ((key[0] // 3 == row_root) and (key[1] // 3 == col_root)):
				combined_surr_cells.add(key)
		return combined_surr_cells

	def combine_surrounding_options(self, row, col) -> set():
		combined_options_row = []
		combined_options_col = []
		combined_options_box = []
		for key in self.keep:
			if key[0] == row and key[1] == col:
				continue
			else:
				row_root = row // self.b_size
				col_root = col // self.b_size
				dummy_box = []	
				if key[0] == row:
					combined_options_row.extend(self.options[key[0]][key[1]])
				if key[1] == col:
					combined_options_col.extend(self.options[key[0]][key[1]])		
				if ((key[0] // 3) == row_root) and ((key[1] // 3) == col_root):
					combined_options_box.extend(self.options[key[0]][key[1]])
		combined_options_setlist = [set(combined_options_row), set(combined_options_col), set(combined_options_box)]
		return combined_options_setlist

	def fill_elim_and_uniq_cand(self): 
		self.one_elim_fill = "false"
		self.uniq_cand = "false"
		#if self.guessing == "false":
		self.one_elim_list = []
		self.uniq_cand_list = []
		for key in self.keep:
			i = key[0]
			j = key[1]
			# doing elim_fill
			if len(self.options[i][j]) == 1:
				fill = self.options[i][j][0]
				self.one_elim_fill = "true"
				#if self.guessing == "true":
				#	self.first_elim_fill = (i,j,fill)
				self.one_elim_list.append( (i,j,fill) )

			elif len(self.options[i][j]) == 0:
				self.wrong_guess_hole = "true"
				break
			else:
				# doing unique_cand_fill
				comb_opt_setlist = self.combine_surrounding_options(i, j)
				for value in self.options[i][j]:
					if value not in comb_opt_setlist[0]:
						self.uniq_cand_list.append( (i,j,value) )
						#if not self.first_uniq_fill:
						#	self.first_uniq_fill = (i,j,value)
						self.uniq_cand = "true"
						break
					elif value not in comb_opt_setlist[1]:
						self.uniq_cand_list.append( (i,j,value) )
						#if not self.first_uniq_fill:
						#	self.first_uniq_fill = (i,j,value)
						self.uniq_cand = "true"
						break
					elif value not in comb_opt_setlist[2]:
						self.uniq_cand_list.append( (i,j,value) )
						#if not self.first_uniq_fill:
						#	self.first_uniq_fill = (i,j,value)
						self.uniq_cand = "true"
						break
		
		#if self.one_elim_fill == "true":
		#	if self.guessing == "true":
		#		oel_index = self.one_elim_list.index(self.first_elim_fill)
		#	else:
		#		oel_index = 0
		#else:
		#	oel_index = len(self.one_elim_list)
		#print("check 3: self.options:(",1,",",0,"):",self.options[1][0])
		#for elim_fill in self.one_elim_list[oel_index:]:
		for elim_fill in self.one_elim_list:
			# check that puzzle still on solution path
			if len(self.options[elim_fill[0]][elim_fill[1]]) == 0 or self.already_in(elim_fill[0],elim_fill[1],elim_fill[2]):
				self.wrong_guess_hole = "true"
				if len(self.options[elim_fill[0]][elim_fill[1]]) == 0:
					print("all options for cell (", [elim_fill[0]], ",", [elim_fill[1]], ") were eliminated")
				else:
					print("the value", elim_fill[2], " is already present around (", [elim_fill[0]], ",", [elim_fill[1]], ")")
				break
			# add value to grid
			self.grid[elim_fill[0]][elim_fill[1]] = elim_fill[2]
			if self.guessing == "true":
				self.guess_list.append(elim_fill)
			# remove the value from surrounding cells' options
			comb_cell_set = self.combine_surrounding_cells(elim_fill[0], elim_fill[1])
			for coord in comb_cell_set:
				if elim_fill[2] in self.options[coord[0]][coord[1]]:
					self.options[coord[0]][coord[1]].remove(elim_fill[2])
					if coord[0] != elim_fill[0] and coord[1] != elim_fill[1]:
						if len(self.options[coord[0]][coord[1]]) == 0:
							print("all options for cell (", [coord[0]], ",", [coord[1]], ") were eliminated")
							self.wrong_guess_hole = "true"
							break
			# self.options[elim_fill[0]][elim_fill[1]] = 0
			# remove value from keep and adjust keep_ind
			keep_index = self.keep.index((elim_fill[0],elim_fill[1]))
			del self.keep[keep_index]
			self.keep_length -= 1
			if self.keep_ind > keep_index:
				self.keep_ind -= 1

		#if self.uniq_cand == "true":
		#	if self.guessing == "true":
		#		ucl_index = self.uniq_cand_list.index(self.first_uniq_fill)
		#	else:
		#		ucl_index = 0
		#else:
		#	ucl_index = len(self.uniq_cand_list)
		#for unique_fill in self.uniq_cand_list[ucl_index:]:
		#print("check 4: self.options:(",1,",",0,"):",self.options[1][0])
		for unique_fill in self.uniq_cand_list:
			# check that puzzle still on solution path
			if len(self.options[unique_fill[0]][unique_fill[1]]) == 0 or self.already_in(unique_fill[0],unique_fill[1],unique_fill[2]):
				self.wrong_guess_hole = "true"
				if len(self.options[unique_fill[0]][unique_fill[1]]) == 0:
					print("all options for cell (", [unique_fill[0]], ",", [unique_fill[1]], ") were eliminated")
				else:
					print("the value", [unique_fill[2]], " is already present around (", [unique_fill[0]], ",", [unique_fill[1]], ")")
				break
			# add value to grid
			self.grid[unique_fill[0]][unique_fill[1]] = unique_fill[2]
			if self.guessing == "true":
				self.guess_list.append(unique_fill)
			# remove the value from surrounding cells' options
			comb_cell_set = self.combine_surrounding_cells(unique_fill[0], unique_fill[1])
			for coord in comb_cell_set:
				if unique_fill[2] in self.options[coord[0]][coord[1]]:
					self.options[coord[0]][coord[1]].remove(unique_fill[2])
					if coord[0] != unique_fill[0] and coord[1] != unique_fill[1]:
						if len(self.options[coord[0]][coord[1]]) == 0:
							print("all options for cell (", [coord[0]], ",", [coord[1]], ") were eliminated")
							self.wrong_guess_hole = "true"
							break
			# self.options[unique_fill[0]][unique_fill[1]] = 0
			# remove value from keep and adjust keep_ind
			keep_index = self.keep.index((unique_fill[0],unique_fill[1]))
			del self.keep[keep_index]
			self.keep_length -= 1
			if self.keep_ind > keep_index:
				self.keep_ind -= 1
		print("all_guess_seeds5:", self.all_guess_seeds)
		print("guess_seeds5:", self.guess_seeds)
		print("check 5: self.options:(",1,",",0,"):",self.options[1][0])
		print("check 5: self.backup_options:(",1,",",0,"):",self.backup_options[1][0])
		print("check 5: self.options:(",0,",",1,"):",self.options[0][1])
		print("check 5: self.backup_options:(",0,",",1,"):",self.backup_options[0][1])
		#print("guess_list5:",self.guess_list)
		#print("check 5: self.options:(",row,",",col,"):",self.options[row][col])
		if self.wrong_guess_hole == "true":
			#print("check 6: self.options:(",1,",",0,"):",self.options[1][0])
			self.backtrack_guess()
			#print("check 7: self.options:(",1,",",0,"):",self.options[1][0])
		



	def backtrack_guess(self):
		# need to restore options and keep
		# need to move onto next index
		# if guess_seed.length = 1, remove guess_seed as option, reset first_elim_fill, first_uniq_fill, guess_seeds,...
		#				...guess_list, uniq_cand_list, one_elim_list
		# need to empty uniq_cand_list and one_elim_list
		# need to reset self.wrong_guess_hole, 
		undo_stop = self.guess_seeds.pop()
		while len(self.options[undo_stop[0]][undo_stop[1]]) == 0:
			for itera in self.all_guess_seeds:
				if itera[0] == undo_stop[0] and itera[1] == undo_stop[1]:
					self.all_guess_seeds.remove(itera)
			undo_stop = self.guess_seeds.pop()
			if len(self.guess_seeds) == 0 and len(self.options[undo_stop[0]][undo_stop[1]]) == 0:
				self.impossible_puzzle = "true"
				break
		if len(self.guess_seeds) == 0:
			#print("check 0: self.options:(",1,",",0,"):",self.options[1][0])
			#print("check 0: self.backup_options:(",1,",",0,"):",self.backup_options[1][0])
			#trash = self.guess_seeds.pop()
			#print("trash1: ", trash)
			self.backup_options[undo_stop[0]][undo_stop[1]].remove(undo_stop[2])
			self.options = copy.deepcopy(self.backup_options)
			self.keep = copy.deepcopy(self.backup_keep)
			self.grid = copy.deepcopy(self.backup_grid)
			self.keep_length = len(self.keep)
			self.guess_list = []
			print("all_guess_seeds6:", self.all_guess_seeds)
			#print("guess_seeds6:", self.guess_seeds)
			print("check 6: self.options:(",1,",",0,"):",self.options[1][0])
			print("check 6: self.backup_options:(",1,",",0,"):",self.backup_options[1][0])
			print("check 6: self.options:(",0,",",1,"):",self.options[0][1])
			print("check 6: self.backup_options:(",0,",",1,"):",self.backup_options[0][1])
		else:
			#print("all_guess_seeds6:", self.all_guess_seeds)
			#print("guess_seeds6:", self.guess_seeds)
			#print("check 6: self.options:(",1,",",0,"):",self.options[1][0])
			#print("check 6: self.backup_options:(",1,",",0,"):",self.backup_options[1][0])
			#print("check 6: self.options:(",0,",",1,"):",self.options[0][1])
			#print("check 6: self.backup_options:(",0,",",1,"):",self.backup_options[0][1])
			self.options = copy.deepcopy(self.backup_options)
			self.keep = copy.deepcopy(self.backup_keep)
			self.grid = copy.deepcopy(self.backup_grid)
			self.keep_length = len(self.keep)
			#print("guess_list:", self.guess_list)
			self.guess_list = self.guess_list[:self.guess_list.index(undo_stop)]
			#print("guess_list:", self.guess_list)
			print("keep:", self.keep[0:7])
			print("backup_keep:", self.backup_keep[0:7])
			# restoring working variables to position of last guess
			#count = 0
			for guess in self.guess_list:
				if undo_stop[0] == 1 or undo_stop[0] == 0:
					print("guess: ", guess)
				self.grid[guess[0]][guess[1]] = guess[2]
				comb_cell_set = self.combine_surrounding_cells(guess[0], guess[1])
				if undo_stop[0] == 1 or undo_stop[0] == 0:
					print("comb_cell_set:", comb_cell_set)
				for coord in comb_cell_set:
					if guess[2] in self.options[coord[0]][coord[1]]:
						self.options[coord[0]][coord[1]].remove(guess[2])
				# self.options[guess[0]][guess[1]] = 0
				# remove value from keep and adjust keep_ind
				keep_index = self.keep.index((guess[0],guess[1]))
				del self.keep[keep_index]
				self.keep_length -= 1
				if self.keep_ind > keep_index:
					self.keep_ind -= 1
			print("keep:", self.keep[0:7])
			print("backup_keep:", self.backup_keep[0:7])
			print("all_guess_seeds7:", self.all_guess_seeds)
			#print("guess_seeds7:", self.guess_seeds)
			print("check 7: self.options:(",1,",",0,"):",self.options[1][0])
			
			print("check 7: self.backup_options:(",1,",",0,"):",self.backup_options[1][0])
			print("check 7: self.options:(",0,",",1,"):",self.options[0][1])
			print("check 7: self.backup_options:(",0,",",1,"):",self.backup_options[0][1])
			# undo_stop = self.guess_seeds.pop()
			#if len(self.options[undo_stop[0]][undo_stop[1]]) == 1:


			# print("trash2: ", trash)
			# move to next iteration of guessing from position of last guess
			#print("guess_list:", self.guess_list)
			for itera in self.all_guess_seeds:
				if itera[2] in self.options[itera[0]][itera[1]]:
					self.options[itera[0]][itera[1]].remove(itera[2])
			#print("guess_list:", self.guess_list)
		#self.first_elim_fill = 0
		#self.first_uniq_fill = 0
		#self.one_elim_list = []
		#self.uniq_cand_list = []
		self.uniq_cand = "false"
		self.one_elim_fill = "false"
		self.wrong_guess_hole = "false"
		
		#print("guess_list7:",self.guess_list)
		#print("check 7: self.options:(",row,",",col,"):",self.options[row][col])
		#for i in range(len(self.guess_list)):
		#	self.grid[self.guess_list[-1][0]][self.guess_list[-1][1]] = 0
		#	del self.guess_list[-1]

		

	# method for going back and erasing when we get it wrong (recursive)
	def options_erase(self, row, col):
		self.option_inds[row][col] += 1
		if len(self.options[row][col]) == self.option_inds[row][col]: # see if we've tried all possibilities
			self.option_inds[row][col] = 0
			self.keep_ind -= 1
			n_row = self.keep[self.keep_ind][0]
			n_col = self.keep[self.keep_ind][1]
			self.grid[n_row][n_col] = 0
			self.options_erase(n_row, n_col)

	# method for trying out numbers to see if they work (recursive)
	def guess_option(self, ki): #ki refers to a coord-tuple in self.keep
		if self.impossible_puzzle == "true":
			return "false"
		if (ki[0] == 1 and ki[1] == 1) or (ki[0] == 8 and ki[1] == 6):
			return "false"
		row = ki[0]
		col = ki[1]
		#print("check 1: self.options:(",7,",",3,"):",self.options[7][3])
		print("currently guessing on: self.options:(",row,",",col,"):",self.options[row][col])
		print("check 1: self.options:(",1,",",0,"):",self.options[1][0])
		print("check 1: self.backup_options:(",1,",",0,"):",self.backup_options[1][0])
		print("check 1: self.options:(",0,",",1,"):",self.options[0][1])
		print("check 1: self.backup_options:(",0,",",1,"):",self.backup_options[0][1])
		k = self.options[row][col][self.option_inds[row][col]]
		if self.already_in(row,col,k):
			print("whoops options_erase!")
			self.options_erase(row, col)
		else:
			self.grid[row][col] = k
			self.guess_list.append((row, col, k))
			self.guess_seeds.append((row, col, k))
			self.guess_seeds_trunc.append((row, col))
			self.all_guess_seeds.append((row, col, k))
			comb_cell_set = self.combine_surrounding_cells(row, col)
			#print("all_guess_seeds8:", self.all_guess_seeds)
			#print("guess_seeds8:", self.guess_seeds)
			#print("guess_list8:",self.guess_list)
			
			#print("check 8: self.options:(",row,",",col,"):",self.options[row][col])
			#print("check 8: self.options:(",1,",",0,"):",self.options[1][0])
			for coord in comb_cell_set:
				if k in self.options[coord[0]][coord[1]]:
					self.options[coord[0]][coord[1]].remove(k)
					#print("check 8: self.options:(",1,",",0,"):",self.options[1][0])
			#print("check 10: self.options:(",1,",",0,"):",self.options[1][0])
			print("check 10: self.options:(",row,",",col,"):",self.options[row][col])
			#self.options[row][col] = 0
			print("all_guess_seeds10:", self.all_guess_seeds)
			print("guess_seeds10:", self.guess_seeds)
			#print("guess_list10:",self.guess_list)
			keep_index = self.keep.index((row,col))
			del self.keep[keep_index]
			self.keep_length -= 1
			if self.keep_ind > keep_index:
				self.keep_ind -= 1
			# self.keep_ind += 1
		#if self.keep_ind == (self.keep_length - 1):
		#	try_out = 0
		#	n_row2 = self.keep[self.keep_ind][0]
		#	n_col2 = self.keep[self.keep_ind][1]
		#	while try_out < 9:
		#		try_out += 1
		#		if not self.already_in(n_row2, n_col2, try_out):
		#			self.grid[n_row2][n_col2] = try_out
		#	return "true"
		return self.solve()

	# solve the Sudoku
	def solve(self):
		self.fill_elim_and_uniq_cand()
		if self.solved() == "true":
			return "true"
		elif self.uniq_cand == "true" or self.one_elim_fill == "true":
			return self.solve()
		else:
			if self.guessing == "false":
				self.backup_keep = copy.deepcopy(self.keep)
				self.backup_options = copy.deepcopy(self.options)
				self.backup_grid = copy.deepcopy(self.grid)
			self.guessing = "true"
			if self.new_guess_start == "false":
				self.new_guess_start = "true"
			return self.guess_option(self.keep[self.keep_ind])

	def solve_sudoku(self):
		if self.impossible_puzzle == "true":
			print("There is no solution to this puzzle.")
		elif self.solve() == "true":
			print("Here is a solution:")
			print(self.grid)
		else: 
			print("There is no solution to this puzzle. Further examination has proved this.")

############################
############################
############################

# easy 1
grid1 =[ [4, 0, 1, 3, 0, 0, 0, 0, 8], 
         [0, 2, 6, 0, 0, 0, 0, 9, 3], 
         [0, 0, 0, 0, 7, 0, 0, 2, 0], 
         [1, 9, 5, 6, 0, 2, 8, 3, 0], 
         [0, 0, 0, 0, 9, 0, 6, 1, 0], 
         [0, 8, 2, 7, 1, 3, 4, 5, 0], 
         [2, 0, 9, 0, 8, 7, 0, 0, 0], 
         [0, 4, 0, 0, 0, 0, 0, 0, 1], 
         [0, 0, 0, 2, 0, 4, 0, 8, 0] ]

# easy 2
grid2 =[ [3, 0, 6, 5, 0, 8, 4, 0, 0], 
         [5, 2, 0, 0, 0, 0, 0, 0, 0], 
         [0, 8, 7, 0, 0, 0, 0, 3, 1], 
         [0, 0, 3, 0, 1, 0, 0, 8, 0], 
         [9, 0, 0, 8, 6, 3, 0, 0, 5], 
         [0, 5, 0, 0, 9, 0, 6, 0, 0], 
         [1, 3, 0, 0, 0, 0, 2, 5, 0], 
         [0, 0, 0, 0, 0, 0, 0, 7, 4], 
         [0, 0, 5, 2, 0, 6, 3, 0, 0] ]

# hard
grid3 =[ [1,0,6,0,0,0,0,5,0],
		 [0,7,0,0,3,0,0,0,4],
		 [0,9,0,0,0,5,2,0,0],
		 [0,0,2,0,6,0,0,0,7],
		 [0,0,0,1,0,8,0,0,0],
		 [0,4,7,0,2,0,0,0,0],
		 [0,0,0,0,0,0,8,0,3],
		 [0,0,3,2,0,0,0,0,6],
		 [0,0,0,0,0,0,0,0,2] ]

# easy, but requires guessing
grid4 =[ [0,0,2,5,0,0,0,9,8],
		 [4,9,0,0,2,0,0,0,5],
		 [3,0,5,9,0,0,2,0,0],
		 [8,6,4,3,1,2,7,5,9],
		 [1,5,3,7,9,8,0,2,0],
		 [9,2,7,6,5,4,8,3,1],
		 [2,0,1,0,0,5,9,0,3],
		 [0,0,0,0,3,0,5,8,2],
		 [5,3,0,2,0,0,1,0,0] ]

sudo = Sudoku(grid3)
sudo.solve_sudoku()


