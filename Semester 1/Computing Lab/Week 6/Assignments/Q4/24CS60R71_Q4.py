from ortools.linear_solver import pywraplp

def create_data_model():
    """Create the data for the optimization problem."""
    data = {}
    
    # List of projects
    data['projects'] = [1, 2, 3, 4]  # Projects are 1, 2, 3, 4
    
    # Return for each project
    data['return'] = {1: 0.2, 2: 0.3, 3: 0.5, 4: 0.1}
    
    # Capital requirements for each year (project, year)
    data['cost'] = {
        (1, 1): 0.5, (1, 2): 0.3, (1, 3): 0.2,
        (2, 1): 1.0, (2, 2): 0.8, (2, 3): 0.2,
        (3, 1): 1.5, (3, 2): 1.5, (3, 3): 0.3,
        (4, 1): 0.1, (4, 2): 0.4, (4, 3): 0.1
    }
    
    # Available capital for each year
    data['available_capital'] = {1: 3.1, 2: 2.5, 3: 0.4}
    
    return data


def project_investment(data):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    x={}
    for i in data['projects']:
        x[i] = solver.IntVar(0,1, f'x[{i}]')

    for j in data['available_capital']:
        solver.Add(sum(data['cost'][(i,j)]*x[i] for i in data['projects']) <= data['available_capital'][j])

    solver.Maximize(solver.Sum(data['return'][i] * x[i] for i in data['projects']))

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        selected_projects = []
        for i in data['projects']:
            if x[i].solution_value() > 0:
                selected_projects.append(i)
        total_return = sum(data['return'][i] for i in selected_projects)

        with open('output.txt', 'w') as output_file:
            for i in data['projects']:
                output_file.write(f"{int(x[i].solution_value())}\n")
            output_file.write(f'{total_return}\n')

    else:
        print("No optimal result was found!!")
                
data=create_data_model()

project_investment(data)