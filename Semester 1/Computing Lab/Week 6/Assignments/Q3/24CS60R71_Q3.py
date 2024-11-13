import math
from ortools.linear_solver import pywraplp

def create_data_model():
    """Define the data for the optimization problem."""
    data = {
        'products': ['A', 'B', 'C', 'D'],
        'factories': [1, 2, 3],
        'price': {'A': 100, 'B': 120, 'C': 80, 'D': 150},
        'cost': {
            ('A', 1): 60, ('A', 2): 65, ('A', 3): 55,
            ('B', 1): 70, ('B', 2): 75, ('B', 3): 80,
            ('C', 1): 40, ('C', 2): 45, ('C', 3): 50,
            ('D', 1): 90, ('D', 2): 100, ('D', 3): 95
        },
        'raw_material': {'A': 2, 'B': 3, 'C': 1.5, 'D': 4},
        'labor_hours': {'A': 3, 'B': 4, 'C': 2, 'D': 5},
        'co2_emissions': {'A': 5, 'B': 7, 'C': 3, 'D': 8},
        'totalRawMaterial': 5000,
        'labor_hours_per_factory': 800,
        'production_capacity_per_factory': 1000,
        'min_production_per_product': 100,
        'max_storage_per_product': 2000,
        'max_co2_emissions': 10000,
        'max_production_budget': 500000,
        'market_demand': {'A': 1500, 'B': 1200, 'C': 1800, 'D': 1000}
    }
    return data

def solve_manufacturing_problem(data):
    """Solve the manufacturing optimization problem to maximize profit."""
    solver = pywraplp.Solver.CreateSolver('GLOP')

    # Define decision variables
    production = {}
    for product in data['products']:
        for factory in data['factories']:
            production[(product, factory)] = solver.IntVar(
                0, data['production_capacity_per_factory'], f'prod_{product}_{factory}'
            )

    # Define the objective function to maximize profit
    profit = solver.Sum(
        production[(product, factory)] * (data['price'][product] - data['cost'][(product, factory)])
        for product in data['products'] for factory in data['factories']
    )
    solver.Maximize(profit)

    # Add constraints
    # Raw material usage
    totalRawMaterial_used = 0
    for product in data['products']:
        for factory in data['factories']:
            totalRawMaterial_used += production[(product, factory)] * data['raw_material'][product]
    solver.Add(totalRawMaterial_used <= data['totalRawMaterial'])

    # Labor hours per factory
    for factory in data['factories']:
        totalRawMaterial_used = 0
        for product in data['products']:
            totalRawMaterial_used += production[(product, factory)] * data['labor_hours'][product]
        solver.Add(totalRawMaterial_used <= data['labor_hours_per_factory'])

    # Market demand and storage constraints
    for product in data['products']:
        total_production = 0
        for factory in data['factories']:
            total_production += production[(product, factory)]
        solver.Add(total_production <= data['market_demand'][product])
        solver.Add(total_production >= data['min_production_per_product'])
        solver.Add(total_production <= data['max_storage_per_product'])

    # CO2 emissions constraint
    totalCo2Emissions = 0
    for product in data['products']:
        for factory in data['factories']:
            totalCo2Emissions += production[(product, factory)] * data['co2_emissions'][product]
    solver.Add(totalCo2Emissions <= data['max_co2_emissions'])

    # Production budget constraint
    totalProductionCost = 0
    for product in data['products']:
        for factory in data['factories']:
            totalProductionCost += production[(product, factory)] * data['cost'][(product, factory)]
    solver.Add(totalProductionCost <= data['max_production_budget'])

    # Solve the problem
    status = solver.Solve()

    with open('output.txt', 'w') as file:
        if status == pywraplp.Solver.OPTIMAL:
            # Write production results
            for product in data['products']:
                for factory in data['factories']:
                    file.write(f'{round(production[(product, factory)].solution_value())}\n')

            # Write resource utilization results
            totalRawMaterial = 0
            for product in data["products"]:
                for factory in data["factories"]:
                    totalRawMaterial += production[(product, factory)].solution_value() * data["raw_material"][product]
            totalRawMaterial = round(totalRawMaterial)
            
            totalRawMaterial = 0
            for product in data["products"]:
                for factory in data["factories"]:
                    totalRawMaterial += production[(product, factory)].solution_value() * data["labor_hours"][product]
            totalRawMaterial = round(totalRawMaterial)

            totalCo2Emissions = 0
            for product in data["products"]:
                for factory in data["factories"]:
                    totalCo2Emissions += production[(product, factory)].solution_value() * data["co2_emissions"][product]
            totalCo2Emissions = round(totalCo2Emissions)

            totalProductionCost = 0
            for product in data["products"]:
                for factory in data["factories"]:
                    totalProductionCost += production[(product, factory)].solution_value() * data["cost"][(product, factory)]
            totalProductionCost = round(totalProductionCost)

            file.write(f'{totalRawMaterial} / {data["totalRawMaterial"]}\n')
            file.write(f'{totalRawMaterial} / {len(data["factories"]) * data["labor_hours_per_factory"]}\n')
            file.write(f'{totalCo2Emissions} / {data["max_co2_emissions"]}\n')
            file.write(f'{totalProductionCost} / {data["max_production_budget"]}\n')
        else:
            file.write('No optimal solution found.\n')

data = create_data_model()
solve_manufacturing_problem(data)
