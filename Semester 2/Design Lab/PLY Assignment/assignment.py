import ply.lex as lex
import ply.yacc as yacc

# Lexer
tokens = [
    'LABEL', 'DOLLAR', 'OPCODE', 'REG', 'NUMBER', 'STRING', 'COMMA', 'COMPARISON', 'IF', 'GOTO'
]

t_DOLLAR = r'\$\$\$'
t_OPCODE = r'STOR|PRINT|HLT|SUM'  # Add any additional opcodes here
t_IF = r'IF'
t_GOTO = r'GOTO'
t_COMPARISON = r'==|!=|<|>|<=|>='
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
    '''instruction : LABEL DOLLAR OPCODE operands
    | LABEL DOLLAR GOTO LABEL
    | condition'''
    p[0] = {'label': p[1], 'opcode': p[3], 'operands': p[4]}

def p_condition(p):
    '''condition : LABEL DOLLAR IF comparison OPCODE operands
    | LABEL DOLLAR IF comparison GOTO LABEL'''
    p[0] = {'label': p[1], 'opcode': p[5], 'operands': p[6], 'comparison': p[4]}

def p_comparison(p):
    '''comparison : operand COMPARISON operand'''
    p[0] = (p[1], p[2], p[3])

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
        size = len(instructions)
        i = 0
        while i < size:
            inst = instructions[i]
            opcode = inst['opcode']
            operands = inst['operands']

            if opcode == 'STOR':
                self.stor(operands)
            elif opcode == 'SUM':
                self.summation(operands)
            elif opcode == 'PRINT':
                self.print_register(operands)
            elif opcode == 'IF':
                a, sign, b = inst['comparison']
                if sign == '==':
                    if a == b:
                        i = self.goto(inst['label'])
                elif sign == '!=':
                    if a != b:
                        i = self.goto(inst['label'])
                elif sign == '<':
                    if a < b:
                        i = self.goto(inst['label'])
                elif sign == '>':
                    if a > b:
                        i = self.goto(inst['label'])
                elif sign == '<=':
                    if a <= b:
                        i = self.goto(inst['label'])
                elif sign == '>=':
                    if a >= b:
                        i = self.goto(inst['label'])
                else:
                    print(f"Unknown comparison operator: {sign}")
                
            elif opcode == 'GOTO':
                i = self.goto(inst['operands'][0])
            elif opcode == 'HLT':
                print("Halting execution.")
                break
            else:
                print(f"Unknown opcode: {opcode}")

            i += 1

    def goto(self, label):
        #return the position of the label
        for i in range(len(instructions)):
            if instructions[i]['label'] == label:
                print(f"Jumping to label {label}")
                return i
        print(f"Error: Label {label} not found.")

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
L6 $$$ IF a <= 100 GOTO L4
L7 $$$ PRINT "Done"
L8 $$$ GOTO L10
L9 $$$ PRINT "Unreachable"
L10 $$$ PRINT "End"
L11 $$$ HLT

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
