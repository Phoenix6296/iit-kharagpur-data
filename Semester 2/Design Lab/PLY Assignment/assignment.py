import ply.lex as lex
import ply.yacc as yacc

# Lexer
tokens = [
    'LABEL', 'DOLLAR', 'OPCODE', 'REG', 'NUMBER', 'STRING', 'COMMA'
]

t_DOLLAR = r'\$\$\$'
t_OPCODE = r'STOR|PRINT|HLT|SUM'  # Add any additional opcodes here
t_REG = r'[A-Za-z]'
t_COMMA = r','
t_ignore = ' \t'

def t_LABEL(t):
    r'L\d+'
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value.strip('"')  # Remove quotes
    return t

def t_NUMBER(t):
    r'-?\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character {t.value[0]} at line {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# Parser
def p_program(p):
    '''program : instructions'''
    p[0] = p[1]

def p_instructions(p):
    '''instructions : instructions instruction
                    | instruction'''
    p[0] = p[1] + [p[2]] if len(p) == 3 else [p[1]]

def p_instruction(p):
    '''instruction : LABEL DOLLAR OPCODE operands'''
    p[0] = {'label': p[1], 'opcode': p[3], 'operands': p[4]}

def p_operands(p):
    '''operands : operand COMMA operands
                | operand'''
    p[0] = [p[1]] + p[3] if len(p) == 4 else [p[1]]

def p_operand(p):
    '''operand : REG
               | NUMBER
               | STRING'''
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' on line {p.lineno}")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()

class VirtualMachine:
    def __init__(self):
        self.registers = {}

    def execute(self, instructions):
        for inst in instructions:
            opcode = inst['opcode']
            operands = inst['operands']

            if opcode == 'STOR':
                self.stor(operands)
            elif opcode == 'SUM':
                self.summation(operands)
            elif opcode == 'PRINT':
                self.print_register(operands)
            elif opcode == 'HLT':
                print("Halting execution.")
                break
            else:
                print(f"Unknown opcode: {opcode}")

    def stor(self, operands):
        reg = operands[0]
        value = operands[1]
        self.registers[reg] = value
        print(f"Stored {value} in register {reg}")

    def summation(self, operands):
        reg = operands[0]
        if reg not in self.registers:
            print(f"Error: Register {reg} not initialized.")
            return
        value = operands[1]
        self.registers[reg] += value
        print(f"Added {value} to register {reg}, new value: {self.registers[reg]}")

    def print_register(self, operands):
        reg = operands[0]
        if reg in self.registers:
            print(f"Value in register {reg}: {self.registers[reg]}")
        else:
            print(f"Error: Register {reg} not initialized.")

# Parse the program
program = """
L0 $$$ STOR A, "Study the examples"
L1 $$$ STOR a, 10
L2 $$$ STOR b, 2
L3 $$$ STOR @b, 35
L4 $$$ SUM a, 5
L5 $$$ PRINT a
"""

instructions = parser.parse(program)

if instructions:
    print("\nParsed Instructions:")
    for inst in instructions:
        print(inst)

    # Execute the parsed instructions
    vm = VirtualMachine()
    print("\nExecuting Program:")
    vm.execute(instructions)
else:
    print("No instructions to execute.")
