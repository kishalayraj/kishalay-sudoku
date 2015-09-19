
def test_cell(s, row, col):
    
    present = [0,0,0,0,0,0,0,0,0,0]
    present[0] = 1
    block_row = row // 3
    block_col = col // 3

    for i in range(9):
        present[s[i][col]] = 1;
        present[s[row][i]] = 1;

    for i in range(3):
        for j in range(3):
            present[s[i + block_row*3][j + block_col*3]] = 1

    return present

def initial_fill(s):
    
    stuck = False

    while not stuck:
        stuck = True
        
        for row in range(9):
            for col in range(9):
                present = test_cell(s, row, col)
                
                if present.count(0) != 1:
                    continue

                for i in range(1, 10):
                    
                    if s[row][col] == 0 and present[i] == 0:
                        s[row][col] = i
                        stuck = False
                        break

def solve(s, row, col):
    
    if row == 8 and col == 8:
        present = test_cell(s, row, col)
        if 0 in present:
            s[row][col] = present.index(0)
        return True

    if col == 9:
        row = row+1
        col = 0

    if s[row][col] == 0:
        present = test_cell(s, row, col)
        for i in range(1, 10):
            if present[i] == 0:
                s[row][col] = i
                if solve(s, row, col+1):
                    return True

        
        s[row][col] = 0
        return False

    return solve(s, row, col+1)

