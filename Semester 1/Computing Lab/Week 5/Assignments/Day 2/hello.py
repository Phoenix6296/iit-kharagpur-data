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
    return math.ceil(x) if x % 1 > 0.5 else math.floor(x)

def globtech_manufacturing_solution(data):
    solver = pywraplp.Solver.CreateSolver('GLOP')
    
    # Decision variables
    x = {}
    for p in data['products']:
        for f in data['factories']:
            x[(p, f)] = solver.IntVar(0, data['production_capacity_per_factory'], f'x_{p}_{f}')
    
    # Objective function: Maximize profit
    profit = solver.Sum(x[(p, f)] * (data['price'][p] - data['cost'][(p, f)]) for p in data['products'] for f in data['factories'])
    solver.Maximize(profit)
    
    # Constraints
    # Total raw material constraint
    solver.Add(solver.Sum(x[(p, f)] * data['raw_material'][p] for p in data['products'] for f in data['factories']) <= data['total_raw_material'])
    
    # Labor hours constraint per factory
    for f in data['factories']:
        solver.Add(solver.Sum(x[(p, f)] * data['labor_hours'][p] for p in data['products']) <= data['labor_hours_per_factory'])
    
    # Market demand constraint
    for p in data['products']:
        solver.Add(solver.Sum(x[(p, f)] for f in data['factories']) <= data['market_demand'][p])
    
    # Minimum production per product
    for p in data['products']:
        solver.Add(solver.Sum(x[(p, f)] for f in data['factories']) >= data['min_production_per_product'])
    
    # Maximum storage per product
    for p in data['products']:
        solver.Add(solver.Sum(x[(p, f)] for f in data['factories']) <= data['max_storage_per_product'])
    
    # CO2 emissions constraint
    solver.Add(solver.Sum(x[(p, f)] * data['co2_emissions'][p] for p in data['products'] for f in data['factories']) <= data['max_co2_emissions'])
    
    # Budget constraint
    solver.Add(solver.Sum(x[(p, f)] * data['cost'][(p, f)] for p in data['products'] for f in data['factories']) <= data['max_production_budget'])

    status = solver.Solve()
    
    with open('output.txt', 'w') as file:
        if status == pywraplp.Solver.OPTIMAL:
            # Write the production quantities in sequence with ceiling value
            for p in data['products']:
                for f in data['factories']:
                    file.write(f'{ceil_or_floor(x[(p, f)].solution_value())}\n')
            
            # Write the resource utilization with ceiling value
            total_raw_material = ceil_or_floor(sum(x[(p, f)].solution_value() * data["raw_material"][p] for p in data["products"] for f in data["factories"]))
            total_labor_hours = ceil_or_floor(sum(x[(p, f)].solution_value() * data["labor_hours"][p] for p in data["products"] for f in data["factories"]))
            total_co2_emissions = ceil_or_floor(sum(x[(p, f)].solution_value() * data["co2_emissions"][p] for p in data["products"] for f in data["factories"]))
            total_production_cost = ceil_or_floor(sum(x[(p, f)].solution_value() * data["cost"][(p, f)] for p in data["products"] for f in data["factories"]))
            
            file.write(f'{total_raw_material} / {data["total_raw_material"]}\n')
            file.write(f'{total_labor_hours} / {len(data["factories"]) * data["labor_hours_per_factory"]}\n')
            file.write(f'{total_co2_emissions} / {data["max_co2_emissions"]}\n')
            file.write(f'{total_production_cost} / {data["max_production_budget"]}\n')
        else:
            file.write('No optimal solution found.\n')

data = create_data_model()
globtech_manufacturing_solution(data)