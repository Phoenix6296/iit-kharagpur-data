from ortools.linear_solver import pywraplp

def solve_diet_problem(A,B):
    
    solver = pywraplp.Solver.CreateSolver('GLOP')
    chicken = solver.NumVar(0, solver.infinity(), 'chicken')
    rice = solver.NumVar(0, solver.infinity(), 'rice')
    broccoli = solver.NumVar(0, solver.infinity(), 'broccoli')
    salmon = solver.NumVar(0, solver.infinity(), 'salmon')
    quinoa = solver.NumVar(0, solver.infinity(), 'quinoa')

    calories = [250, 200, 50, 300, 200]
    protein = [30, 5, 4, 25, 8]
    carbs = [0,45,10,0,39]
    fat=[10,1,0.5,20,4]
    cost=[5,2,1,8,4]

    solver.Add(chicken*calories[0]+rice*calories[1]+broccoli*calories[2]+salmon*calories[3]+quinoa*calories[4] >= A)
    solver.Add(chicken*protein[0]+rice*protein[1]+broccoli*protein[2]+salmon*protein[3]+quinoa*protein[4] >= B)
    solver.Add(chicken*carbs[0]+rice*carbs[1]+broccoli*carbs[2]+salmon*carbs[3]+quinoa*carbs[4] >= 150)
    solver.Add(chicken*fat[0]+rice*fat[1]+broccoli*fat[2]+salmon*fat[3]+quinoa*fat[4] >= 40)

    solver.Minimize(chicken*cost[0]+rice*cost[1]+broccoli*cost[2]+salmon*cost[3]+quinoa*cost[4])

    status = solver.Solve()

    with open('output.txt', 'w') as output_file:
        if status == pywraplp.Solver.OPTIMAL:
            output_file.write(f'{solver.Objective().Value():.2f}\n')
            output_file.write(f'{chicken.solution_value():.2f}\n')
            output_file.write(f'{rice.solution_value():.2f}\n')
            output_file.write(f'{broccoli.solution_value():.2f}\n')
            output_file.write(f'{salmon.solution_value():.2f}\n')
            output_file.write(f'{quinoa.solution_value():.2f}\n')
            
        else:
            output_file.write('No optimal solution was found!!')


with open('input.txt') as f:
    lines=f.readlines()

A=float(lines[0])
B=float(lines[1])
solve_diet_problem(A,B)