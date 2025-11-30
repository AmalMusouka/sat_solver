This is a solution to the homework "Killer Sudoku" with $n$ constraints(size of square grid) for Propositional and Predicate Logic (NAIL062). The provided Python code encodes, solves and decodes (if successful) the killer sudoku puzzle via reduction to SAT.

Problem Description

Killer Sudoku is a puzzle played on a {n×n} grid containing nxn cells. The cells are filled in with numbers from the set {1…n}. Each row and column must contain all numbers {1…n}. Each of the n non-overlapping sqrt(n)xsqrt(n) subsquares (named boxes) must also contain all numbers {1…n}

Each Killer Sudoku puzzle has a set of cages. A cage is a set of contiguous cells and a total; the numbers in the cells must add up to the total. Also, the cells in a cage cannot contain the same number more than once. The cages do not overlap, and they cover all cells. Cages typically contain two to four cells. Typically a Killer Sudoku puzzle will have exactly one solution. 

The input is given in a format where the first line gives the size of the grid, the second line gives the total number of cages and following it is the cages one by one on each line in the following format

sum num_of_cells_in_this_cage cell_1(row1 col1) cell_2 ....

An example of a valid input format is


Encoding

The problem is encodes using 
