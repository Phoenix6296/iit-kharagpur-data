from ortools.linear_solver import pywraplp

def n_queens(n):
    
    solver = pywraplp.Solver.CreateSolver('CBC')
    
    x = [[solver.BoolVar(f'x[{i}],{j}') for j in range(n)] for i in range(n)]
    for i in range(n):
        solver.Add(sum(x[i][j] for j in range(n)) == 1)
    for j in range(n):
        solver.Add(sum(x[i][j] for i in range(n)) == 1)
    for k in range(-n + 1, n):
        solver.Add(sum(x[i][j] for i in range(n) for j in range(n) if i - j == k) <= 1)
    for k in range(2 * n - 1):
        solver.Add(sum(x[i][j] for i in range(n) for j in range(n) if i + j == k) <= 1)

    solver.Minimize(0)
    status = solver.Solve()

    with open('output.txt', 'w') as output_file:
        if status == pywraplp.Solver.OPTIMAL:
            for i in range(n):
                row = ['_' for _ in range(n)]
                for j in range(n):
                    if x[i][j].solution_value() == 1:
                        row[j] = 'Q'
                output_file.write(" ".join(row) + "\n")
        else:
            output_file.write("No output file was found!!")


with open('input.txt') as f:
    lines=f.readlines()

n=int(lines[0])
n_queens(n)
