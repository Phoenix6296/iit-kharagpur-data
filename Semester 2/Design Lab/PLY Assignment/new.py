import ply.lex as lex
import ply.yacc as yacc

# --- Tokens ---
tokens = (
    "LABEL",  # e.g., L0, L1
    "DOLLAR",  # $$$
    "ID",  # Identifiers (e.g., registers A, B, etc.)
    "MEMREF",  # Memory reference
    "NUMBER",  # Numeric values
    "STRING",  # String values
    "COMMA",  # ,
    "EQ", "NE", "GT", "LT",  # Relational operators
    "STOR", "SUM", "SUB", "MUL", "DIV", "MOD",  # Arithmetic operations
    "AND", "OR", "XOR", "NOT", "SHL", "SHR",  # Logical and bitwise operations
    "IF", "GOTO", "HLT", "PRINT",  # Control flow and commands
    "CONCAT", "LENGTH", "SUBSTR",  # String operations
)

# --- Regular Expressions ---
t_DOLLAR = r'\$\$\$'
t_COMMA = r',' 
t_EQ = r'==' 
t_NE = r'!=' 
t_GT = r'>' 
t_LT = r'<'

def t_LABEL(t):
    r'[Ll]\d+'
    return t

def t_MEMREF(t):
    r'@[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value.upper() in keyword_map:
        t.type = t.value.upper()
    return t

def t_NUMBER(t):
    r'-?\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    return t

def t_STRING(t):
    r'"([^\\"]|\\")*"'
    t.value = t.value[1:-1]
    return t

t_ignore = ' \t'

# Map keywords to token types
keyword_map = {
    'STOR': 'STOR', 'SUM': 'SUM', 'SUB': 'SUB', 'MUL': 'MUL', 'DIV': 'DIV', 'MOD': 'MOD',
    'AND': 'AND', 'OR': 'OR', 'XOR': 'XOR', 'NOT': 'NOT', 'SHL': 'SHL', 'SHR': 'SHR',
    'IF': 'IF', 'GOTO': 'GOTO', 'HLT': 'HLT', 'PRINT': 'PRINT',
    'CONCAT': 'CONCAT', 'LENGTH': 'LENGTH', 'SUBSTR': 'SUBSTR'
}

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"LEX ERROR: Illegal character '{t.value[0]}' at line {t.lexer.lineno}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# --- Registers and Memory ---
registers = {}  # For registers (e.g., A, B, C)
memory = {}     # For memory locations (e.g., @mem1, @mem2)

# --- Print State Function ---
def print_state():
    print("Current State of Registers:")
    for reg, value in registers.items():
        print(f"{reg}: {value}")
    print("Current State of Memory:")
    for mem, value in memory.items():
        print(f"{mem}: {value}")
    print("-" * 30)

# --- Parser Rules ---
def p_program(p):
    '''program : instruction_list'''
    p[0] = p[1]

def p_instruction_list(p):
    '''instruction_list : instruction instruction_list
                        | instruction'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_instruction(p):
    '''instruction : opt_label command'''
    if p[1]:
        p[2]['label'] = p[1]
    p[0] = p[2]
    # After processing each instruction, print the current state of registers and memory
    print_state()

def p_opt_label(p):
    '''opt_label : LABEL DOLLAR
                 | empty'''
    p[0] = p[1] if len(p) == 3 else None

def p_command(p):
    '''command : memory_command
               | arithmetic_command
               | logical_command
               | control_flow_command
               | print_command
               | string_command'''
    p[0] = p[1]

def p_memory_command(p):
    '''memory_command : STOR operand COMMA operand'''
    target = p[2]
    value = p[4]
    if isinstance(target, str) and target.startswith('@'):
        memory[target] = value
    else:
        registers[target] = value
    p[0] = {'opcode': 'STOR', 'operands': [p[2], p[4]]}

def p_arithmetic_command(p):
    '''arithmetic_command : SUM operand COMMA operand
                          | SUB operand COMMA operand
                          | MUL operand COMMA operand
                          | DIV operand COMMA operand
                          | MOD operand COMMA operand'''
    # Ensure that both operands are treated as numbers
    operand1 = p[2]
    operand2 = p[4]

    # Check if operands are numbers, if not, convert them
    if isinstance(operand1, str):
        operand1 = float(operand1) if '.' in operand1 else int(operand1)
    if isinstance(operand2, str):
        operand2 = float(operand2) if '.' in operand2 else int(operand2)

    # Perform the operation
    if p[1].upper() == 'SUM':
        p[0] = operand1 + operand2
    elif p[1].upper() == 'SUB':
        p[0] = operand1 - operand2
    elif p[1].upper() == 'MUL':
        p[0] = operand1 * operand2
    elif p[1].upper() == 'DIV':
        p[0] = operand1 / operand2
    elif p[1].upper() == 'MOD':
        p[0] = operand1 % operand2


def p_logical_command(p):
    '''logical_command : AND operand COMMA operand
                       | OR operand COMMA operand
                       | XOR operand COMMA operand
                       | NOT operand
                       | SHL operand COMMA operand
                       | SHR operand COMMA operand'''
    if p[1].upper() == 'NOT':
        p[0] = {'opcode': 'NOT', 'operands': [p[2]]}
    else:
        p[0] = {'opcode': p[1].upper(), 'operands': [p[2], p[4]]}

def p_control_flow_command(p):
    '''control_flow_command : IF condition command
                            | GOTO LABEL
                            | HLT'''
    if p[1].upper() == 'IF':
        p[0] = {'opcode': 'IF', 'condition': p[2], 'then': p[3]}
    elif p[1].upper() == 'GOTO':
        p[0] = {'opcode': 'GOTO', 'label_target': p[2]}
    elif p[1].upper() == 'HLT':
        p[0] = {'opcode': 'HLT'}

def p_print_command(p):
    '''print_command : PRINT operand'''
    p[0] = {'opcode': 'PRINT', 'operands': [p[2]]}

def p_string_command(p):
    '''string_command : CONCAT operand COMMA operand
                      | LENGTH operand
                      | SUBSTR operand COMMA operand COMMA operand'''
    if p[1].upper() == 'CONCAT':
        p[0] = {'opcode': 'CONCAT', 'operands': [p[2], p[4]]}
    elif p[1].upper() == 'LENGTH':
        p[0] = {'opcode': 'LENGTH', 'operands': [p[2]]}
    elif p[1].upper() == 'SUBSTR':
        p[0] = {'opcode': 'SUBSTR', 'operands': [p[2], p[4], p[6]]}

def p_condition(p):
    '''condition : operand EQ operand
                 | operand NE operand
                 | operand GT operand
                 | operand LT operand'''
    p[0] = (p[1], p[2], p[3])

def p_operand(p):
    '''operand : NUMBER
               | STRING
               | MEMREF
               | ID'''
    # If the operand is a number, just return it
    if isinstance(p[1], (int, float)):
        p[0] = p[1]
    # If it's a string, return it as a string value
    elif isinstance(p[1], str):
        p[0] = p[1]
    # If it's a memory reference, we need to get the value stored in memory
    elif p[1].startswith('@'):
        p[0] = memory.get(p[1], 0)  # Return the value stored in memory (default 0 if not found)
    # If it's an identifier (register), return the value in the register
    else:
        p[0] = registers.get(p[1], 0)  # Return the register value (default 0 if not found)

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"PARSE ERROR: Unexpected token '{p.value}' at line {p.lineno}")
    else:
        print("PARSE ERROR: End of input")

# Build the parser
parser = yacc.yacc()

# --- Main Execution ---
if __name__ == "__main__":
    print("Enter your program line by line (end with an empty line):")
    input_lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        input_lines.append(line)
    
    input_code = "\n".join(input_lines)
    result = parser.parse(input_code, lexer=lexer)
    print("Parsed Output:")
    print(result)

    # Print final state of registers and memory after execution
    print("Final State of Registers and Memory:")
    print_state()