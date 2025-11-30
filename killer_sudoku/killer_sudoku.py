import math
import subprocess
from argparse import ArgumentParser

def load_instance(input_file):
    # read the input file
    # the instance is the size of the grid and then the tiles

    global GRID_SIZE, BOX_SIZE, NR_TILES, NR_CAGES
    cages = []

    with open(input_file, "r") as file:
        lines = [line.strip() for line in file if line.strip()]
        GRID_SIZE = int(lines[0])
        NR_CAGES = int(lines[1])
        for line in lines[2:2 + NR_CAGES]:
            nums = list(map(int, line.split()))

            cage_sum = nums[0]
            k = nums[1]

            cells_flat = nums[2:]
            assert len(cells_flat) == 2 * k, f"Expected {2 * k} coordinates, got {len(cells_flat)}"
            # convert list to list of (r,c)
            cells = [(cells_flat[i], cells_flat[i + 1]) for i in range(0, len(cells_flat), 2)]

            cages.append((cage_sum, cells))

        BOX_SIZE = int(math.isqrt(GRID_SIZE))
        NR_TILES = GRID_SIZE * GRID_SIZE

        return cages

def cage_combinations(target_sum, total_numbers):
    # we find all possible ways to fill a cage generating sequences of unique numbers whose sum equal exactyl the target sum
    numbers = list(range(1, GRID_SIZE + 1))
    valid = []

    sequences = [((), 0, set())]  # sequence tuple, sum_so_far, set of used numbers

    for _ in range(total_numbers):
        new_sequences = []
        for seq, s, used in sequences:
            for n in numbers:
                if n not in used and s + n <= target_sum:
                    new_sequences.append((seq + (n,), s + n, used | {n}))
        sequences = new_sequences

    for seq, s, _ in sequences:
        if s == target_sum:
            valid.append(list(seq))

    return valid


def dimacs(rows, cols, number):
    # mapping to unique dimacs number
    return (rows - 1) * GRID_SIZE * GRID_SIZE + (cols - 1) * GRID_SIZE + number

def encode(instance):
    # given the instance, create a cnf formula, i.e. a list of lists of integers
    # also return the total number of variables used

    cnf = []
    # for the variables we are going to use a format of x(r, c, n) where r is the row, c is the column and n is the number
    nr_vars = GRID_SIZE * GRID_SIZE * GRID_SIZE

    # each cell has at least one number
    for row in range(1, GRID_SIZE + 1):
        for col in range(1, GRID_SIZE + 1):
            clause = [dimacs(row, col, number) for number in range(1, GRID_SIZE + 1)]
            cnf.append(clause)
            for num_1 in range(1, GRID_SIZE + 1):
                for num_2 in range(num_1 + 1, GRID_SIZE + 1):
                    cnf.append([-dimacs(row, col, num_1), -dimacs(row, col, num_2)])

    # row uniqueness
    for row in range(1, GRID_SIZE + 1):
        for number in range(1, GRID_SIZE + 1):
            for col_1 in range(1, GRID_SIZE + 1):
                for col_2 in range(col_1 + 1, GRID_SIZE + 1):
                    cnf.append([-dimacs(row, col_1, number), -dimacs(row, col_2, number)])

    # column uniqueness
    for col in range(1, GRID_SIZE + 1):
        for number in range(1, GRID_SIZE + 1):
            for row_1 in range(1, GRID_SIZE + 1):
                for row_2 in range(row_1 + 1, GRID_SIZE + 1):
                    cnf.append([-dimacs(row_1, col, number), -dimacs(row_2, col, number)])

    # 3x3 box
    for box_row in range(0, BOX_SIZE):
        for box_col in range(0, BOX_SIZE):
            cells = [(box_row * BOX_SIZE + r, box_col * BOX_SIZE + c)for r in range(1, BOX_SIZE + 1)for c in range(1, BOX_SIZE + 1)]
            for number in range(1, GRID_SIZE + 1):
                for i in range(len(cells)):
                    for j in range(i + 1, len(cells)):
                        row_1, col_1 = cells[i]
                        row_2, col_2 = cells[j]
                        cnf.append([-dimacs(row_1, col_1, number),-dimacs(row_2, col_2, number)])

    # cage constraints
    for cage_sum, cells in instance:
        length = len(cells)
        combos = cage_combinations(cage_sum, length)

        # we handle impossible scenario, and forces the first to be true and false
        if not combos:
            return [[1], [-1]], GRID_SIZE * GRID_SIZE * GRID_SIZE

        cage_clause = []
        # we now take the matching variables in the grid that match the specific combination
        # logically equivalent to cell_1 and cell_2 and .... and cell_n
        for combo in combos:
            matching_vars = nr_vars + 1
            nr_vars += 1

            # implication
            conj_literals = []
            for (row, col), n in zip(cells, combo):
                literal = dimacs(row, col, n)
                cnf.append([-matching_vars, literal])

                conj_literals.append(literal)

            # reverse implication
            cnf.append([-l for l in conj_literals] + [matching_vars])

            cage_clause.append(matching_vars)

        # at least one
        cnf.append(cage_clause)

        # at most one
        for i in range(len(cage_clause)):
            for j in range(i + 1, len(cage_clause)):
                matching_i = cage_clause[i]
                matching_j = cage_clause[j]
                cnf.append([-matching_i, -matching_j])


    return cnf, nr_vars


def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + "\n")
        for clause in cnf:
            file.write(' '.join(str(lit) for lit in clause) + ' 0\n')

    return subprocess.run(['./' + solver_name, '-model', '-verb=' + str(verbosity) , output_name], stdout=subprocess.PIPE)


def print_solution_grid(solution_line):

    N_cube = NR_TILES * GRID_SIZE  # 729 for a 9x9

    parts = solution_line.split()
    true_vars = [int(p) for p in parts[1:] if int(p) > 0 and int(p) <= N_cube]

    # 2. Initialize the empty grid
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

    # 3. Decode each TRUE variable
    for v_id in true_vars:
        # Subtract 1 because formula is based on 0-indexed variables
        v_id_0 = v_id - 1

        # DIMACS (R, C, N) decoding based on the standard formula:
        row_0 = v_id_0 // NR_TILES  # Row (0-indexed)
        col_0 = (v_id_0 % NR_TILES) // GRID_SIZE  # Column (0-indexed)
        num = (v_id_0 % GRID_SIZE) + 1  # Number (1-indexed)

        grid[row_0][col_0] = num

    box_size = int(math.isqrt(GRID_SIZE))

    print()
    print("####################################################################")
    print("###########[ Human readable result of the killer sudoku ]###########")
    print("####################################################################")
    print()


    # Print top border
    print(" " + "---" * GRID_SIZE + "---")

    for r in range(GRID_SIZE):
        row_output = "| "
        for c in range(GRID_SIZE):
            # Add the number, padding for alignment
            row_output += str(grid[r][c]).center(2)

            # Add vertical box separator
            if (c + 1) % box_size == 0 and c < GRID_SIZE - 1:
                row_output += "| "
            else:
                row_output += " "

        row_output += "|"
        print(row_output)

        # Add horizontal box separator
        if (r + 1) % box_size == 0 and r < GRID_SIZE - 1:
            print("|" + ("---" * box_size + "+") * box_size)  # Adjusted horizontal separator

    # Print bottom border
    print(" " + "---" * GRID_SIZE + "---")


def main():
    parser = ArgumentParser()
    parser.add_argument("-i","--input", default="instances/input_9x9_working.in")
    parser.add_argument("-o","--output", default="formula.cnf")
    parser.add_argument("-s","--solver", default="glucose")
    parser.add_argument("-v","--verb", type=int, default=1, choices=[0,1])
    args = parser.parse_args()

    instance = load_instance(args.input)
    cnf, nr_vars = encode(instance)
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)
    solver_output = result.stdout.decode()
    print(solver_output)
    if "s SATISFIABLE" in solver_output:
        solution_line = next((line for line in solver_output.splitlines() if line.startswith('v ')), None)

        if solution_line:
            print_solution_grid(solution_line)
    else:
        print("\nProblem is UNSATISFIABLE. No solution grid to display.")


if __name__=="__main__":
    main()