This is a solution to the homework "Killer Sudoku" with $n$ constraints(size of square grid) for Propositional and Predicate Logic (NAIL062). The provided Python code encodes, solves and decodes (if successful) the killer sudoku puzzle via reduction to SAT.

# Problem Description

Killer Sudoku is a puzzle played on a {n×n} grid containing nxn cells. The cells are filled in with numbers from the set {1…n}. Each row and column must contain all numbers {1…n}. Each of the n non-overlapping sqrt(n)xsqrt(n) subsquares (named boxes) must also contain all numbers {1…n}

Each Killer Sudoku puzzle has a set of cages. A cage is a set of contiguous cells and a total; the numbers in the cells must add up to the total. Also, the cells in a cage cannot contain the same number more than once. The cages do not overlap, and they cover all cells. Cages typically contain two to four cells. Typically a Killer Sudoku puzzle will have exactly one solution. 

The input is given in a format where the first line gives the size of the grid, the second line gives the total number of cages and following it is the cages one by one on each line in the following format

sum num_of_cells_in_this_cage cell_1(row1 col1) cell_2 ....

An example of a valid input format is


# Encoding

The problem is encoded using two sets of variables. Variable $num(r,c,n)$ represents the number $n$ located in the cell at row $r$ and column $c$ and the variable $combo(c,i)$ is the matching variable for the $i^{th}$ valid combination of numbers selected for the $c^{th}$ cage.

## Constraints

We consider the grid size as $G$ and the box size as $B$.

- Cell contains at least one number - $\bigwedge_{r,c} \bigvee^{G}_{n=1} num(r,c,n)$

- Cell $(r,c)$ cannot contain two different numbers - $\bigwedge_{r,c} \bigwedge_{n_1<n_2} \neg num(r,c,n_1) \vee \neg num(r,c,n_2)$

- Cells in the same row $r$ cannot have the same number - $\bigwedge_{r,n} \bigwedge_{c_1<c_2} \neg num(r,c_1,n) \vee \neg num(r,c_2,n)$

- Cells in the same column $c$ cannot have the same number - $\bigwedge_{c,n} \bigwedge_{r_1<r_2} \neg num(r_1,c,n) \vee \neg num(r_2,c,n)$

- No two cells in the same box $BxB$ can have the same number - $\bigwedge_B \bigwedge_n \bigwedge_{(r_1,c_1)<(r_2,c_2)\in B} \neg num(r_1,c_1,n) \vee \neg num(r_2,c_2,n)$

- (Implication) If a combination $i$ is chosen for the cage $C$, then if $combo(C,i)$ is true then all cell assignemnts in teh combination must be true - $\bigwedge_i \bigwedge_{(r,c), n \in combo_i} \neg combo(C, i) \vee num(r,c,n)$

- (Backward Implication) If all the cell assignments are true, then the $combo(C,i)$ must also be true - $\bigwedge_i ((\bigvee_{(r,c), n \in combo_i} \neg num(r,c,n) ) \vee combo(c,i)$

- At least one valid combination must be chosen for the cage - $\bigvee_i combo(C,i)$

- For one cage, we cant have two different combinations - $\bigwedge_{i_1<i_2} \neg combo(C,i_1) \vee \neg combo(C, i_2)$

- No two cells in the same cage $C$ with a set of coordinates $X_c$ can have the same number $n$ - $\bigwedge_n \bigwedge_{(r_1,c_1) < (r_2,c_2) \in X_C} \neg num(r_1,c_1,n) \vee \neg num(r_2,c_2,n($
