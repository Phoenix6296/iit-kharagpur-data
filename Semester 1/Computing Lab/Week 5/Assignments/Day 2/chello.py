import math
from ortools.linear_solver import pywraplp

def create_data_model():
    """Create the data for the problem."""
    data = {}
    data['products'] = ['A', 'B', 'C', 'D']
    data['factories'] = [1, 2, 3]
    
    data['price'] = {'A': 100, 'B': 120, 'C': 80, 'D': 150}
    
    data['cost'] = {
        ('A', 1): 60, ('A', 2): 65, ('A', 3): 55,
        ('B', 1): 70, ('B', 2): 75, ('B', 3): 80,
        ('C', 1): 40, ('C', 2): 45, ('C', 3): 50,
        ('D', 1): 90, ('D', 2): 100, ('D', 3): 95
    }
    
    data['raw_material'] = {'A': 2, 'B': 3, 'C': 1.5, 'D': 4}
    data['labor_hours'] = {'A': 3, 'B': 4, 'C': 2, 'D': 5}
    data['co2_emissions'] = {'A': 5, 'B': 7, 'C': 3, 'D': 8}
    
    data['total_raw_material'] = 5000
    data['labor_hours_per_factory'] = 800
    data['production_capacity_per_factory'] = 1000
    data['min_production_per_product'] = 100
    data['max_storage_per_product'] = 2000
    data['max_co2_emissions'] = 10000
    data['max_production_budget'] = 500000
    
    data['market_demand'] = {'A': 1500, 'B': 1200, 'C': 1800, 'D': 1000}
    
    return data

def ceil_or_floor(x):
    fractional_part = x - math.floor(x)
    return math.ceil(x) if fractional_part > 0.5 else math.floor(x)

def create_variables(solver, data):
    x = {}
    for p in data['products']:
        for f in data['factories']:
            x[(p, f)] = solver.IntVar(0, data['production_capacity_per_factory'], f'x_{p}_{f}')
    return x

def set_objective(solver, x, data):
    terms = []
    for p in data['products']:
        for f in data['factories']:
            terms.append(x[(p, f)] * (data['price'][p] - data['cost'][(p, f)]))
    profit = solver.Sum(terms)
    solver.Maximize(profit)

def add_constraints(solver, x, data):
    # Total raw material usage constraint
    terms = []
    for p in data['products']:
        for f in data['factories']:
            terms.append(x[(p, f)] * data['raw_material'][p])
    solver.Add(solver.Sum(terms) <= data['total_raw_material'])
    
    # Labor hours per factory constraint
    for f in data['factories']:
        terms = []
        for p in data['products']:
            terms.append(x[(p, f)] * data['labor_hours'][p])
        solver.Add(solver.Sum(terms) <= data['labor_hours_per_factory'])
    
    # Market demand, minimum production, and storage capacity constraints
    for p in data['products']:
        terms = []
        for f in data['factories']:
            terms.append(x[(p, f)])
        solver.Add(solver.Sum(terms) <= data['market_demand'][p])
        solver.Add(solver.Sum(terms) >= data['min_production_per_product'])
        solver.Add(solver.Sum(terms) <= data['max_storage_per_product'])

    # CO2 emissions constraint
    terms = []
    for p in data['products']:
        for f in data['factories']:
            terms.append(x[(p, f)] * data['co2_emissions'][p])
    solver.Add(solver.Sum(terms) <= data['max_co2_emissions'])
    
    # Production budget constraint
    terms = []
    for p in data['products']:
        for f in data['factories']:
            terms.append(x[(p, f)] * data['cost'][(p, f)])
    solver.Add(solver.Sum(terms) <= data['max_production_budget'])

def write_solution_to_file(status, solver, x, data):
    with open('output.txt', 'w') as file:
        if status == pywraplp.Solver.OPTIMAL:
            for p in data['products']:
                for f in data['factories']:
                    quantity = x[(p, f)].solution_value()
                    file.write(f'{ceil_or_floor(quantity)}\n')
            
            total_raw_material = 0
            total_labor_hours = 0
            total_co2_emissions = 0
            total_production_cost = 0
            
            for p in data['products']:
                for f in data['factories']:
                    total_raw_material += x[(p, f)].solution_value() * data["raw_material"][p]
                    total_labor_hours += x[(p, f)].solution_value() * data["labor_hours"][p]
                    total_co2_emissions += x[(p, f)].solution_value() * data["co2_emissions"][p]
                    total_production_cost += x[(p, f)].solution_value() * data["cost"][(p, f)]
            
            file.write(f'{ceil_or_floor(total_raw_material)} / {data["total_raw_material"]}\n')
            file.write(f'{ceil_or_floor(total_labor_hours)} / {len(data["factories"]) * data["labor_hours_per_factory"]}\n')
            file.write(f'{ceil_or_floor(total_co2_emissions)} / {data["max_co2_emissions"]}\n')
            file.write(f'{ceil_or_floor(total_production_cost)} / {data["max_production_budget"]}\n')
        else:
            file.write('No optimal solution found.\n')

def globtech_manufacturing_solution(data):
    solver = pywraplp.Solver.CreateSolver('GLOP')
    x = create_variables(solver, data)
    set_objective(solver, x, data)
    add_constraints(solver, x, data)
    status = solver.Solve()
    write_solution_to_file(status, solver, x, data)

data = create_data_model()
globtech_manufacturing_solution(data)
