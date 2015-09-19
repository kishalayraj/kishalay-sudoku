import Solver
import random

def valid_cell(s, row, col):
    block_row = row // 3
    block_col = col // 3

    for i in range(9):
        if s[row][i] != 0 and i != col and s[row][i] == s[row][col]:
            return False
        if s[i][col] != 0 and i != row and s[i][col] == s[row][col]:
            return False

    for i in range(3):
        for j in range(3):
            new_row = i + block_row*3
            new_col = j + block_col*3
            if s[new_row][new_col] != 0 and new_row != row and new_col != col and s[new_row][new_col ] == s[row][col]:
		return False

    return True

def fill_sudoku(s, row, col):
    
    if row == 8 and col == 8:
        present = Solver.test_cell(s, row, col)
        s[row][col] = present.index(0)
        return True

    if col == 9:
        row = row+1
        col = 0

    sequence = [1,2,3,4,5,6,7,8,9]
    random.shuffle(sequence)
    
    for i in range(9):
        s[row][col] = sequence[i]
        if valid_cell(s, row, col):
            if fill_sudoku(s, row, col+1):
                return True
    
    s[row][col] = 0
    return False

def number_solutions(copy_s, row, col):
    
    num_solutions = 0

    if row == 8 and col == 8:
        return num_solutions + 1

    if col == 9:
        row = row+1
        col = 0

    if copy_s[row][col] == 0:
        present = Solver.test_cell(copy_s, row, col)
        
        if 0 not in present:
            return 0

        while 0 in present:
            copy_s[row][col] = present.index(0)
            present[present.index(0)] = 1
            num_solutions += number_solutions(copy_s, row, col+1)

        
        copy_s[row][col] = 0
        return num_solutions

    num_solutions += number_solutions(copy_s, row, col+1)
    return num_solutions

def reduce_sudoku(s, difficulty):
    
    elements = list(range(81))
    random.shuffle(elements)

    while elements:
        row = elements[0] // 9
        col = elements[0] % 9
        temp = s[row][col]
        s[row][col] = 0
        elements = elements[1:]
        
        copy_s = [[0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0],
	     [0,0,0,0,0,0,0,0,0]]

        for i in range(9):
            for j in range(9):
		copy_s[i][j] = s[i][j]	

        Solver.initial_fill(copy_s)

        for line in copy_s:
            if 0 in line:
                num_solutions = number_solutions(copy_s, 0, 0)
                
                if num_solutions > 1:
                    s[row][col] = temp
                    if difficulty == 1:
			return
		    if difficulty == 2 and len(elements)<=40:
			return
		    if difficulty == 3 and len(elements)<=24:
			return
                break

    return
