import nltk
import ply.lex as lex
import ply.yacc as yacc
from nltk.corpus import brown

# Download NLTK resources
# nltk.download('brown')
# nltk.download('universal_tagset')

# Extract POS-tagged words
def extract_words(pos_tags, max_words=10):
    words = [word.lower() for word, tag in brown.tagged_words(tagset='universal') if tag in pos_tags]
    return list(set(words))[:max_words]

# Extract specific word groups
articles = extract_words(['DET'], 10)
nouns = extract_words(['NOUN'], 10)
adjectives = extract_words(['ADJ'], 10)
verbs = extract_words(['VERB'], 10)
verbca = ['is', 'am', 'was', 'are', 'were']
verbcb = ['sleeping', 'talking', 'crying', 'laughing', 'feeding', 'eating', 'bathing', 'grumbling', 'loitering', 'watching']

# Define tokens
tokens = [
    'ARTICLE', 'NOUN', 'ADJECTIVE', 'VERB', 'VERBCA', 'VERBCB'
]

# Token definitions with boundaries
t_ignore = ' \t'
t_ARTICLE = r'\b(?:' + r'|'.join(articles) + r')\b'
t_NOUN = r'\b(?:' + r'|'.join(nouns) + r')\b'
t_ADJECTIVE = r'\b(?:' + r'|'.join(adjectives) + r')\b'
t_VERB = r'\b(?:' + r'|'.join(verbs) + r')\b'
t_VERBCA = r'\b(?:' + r'|'.join(verbca) + r')\b'
t_VERBCB = r'\b(?:' + r'|'.join(verbcb) + r')\b'

# Handle newline characters
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Error handler
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at position {t.lexpos}")
    t.lexer.skip(1)

# Build lexer
lexer = lex.lex()

# Grammar rules
def p_sentence_single_verb(p):
    'sentence : ARTICLE NOUN VERB'
    p[0] = f"Valid Statement. POS: Article Noun Verb"

def p_sentence_double_verb(p):
    'sentence : ARTICLE NOUN VERBCA VERBCB'
    p[0] = f"Valid Statement. POS: Article Noun VerbCA VerbCB"

def p_error(p):
    if p:
        print(f"Syntax error at token '{p.value}', line {p.lineno}")
    else:
        print("Syntax error at EOF")

# Build parser
parser = yacc.yacc()

# Main program
def main():
    print("Enter a sentence (2-8 words, lowercase only):")
    input_sentence = input().strip()
    
    # Validate length
    words = input_sentence.split()
    if len(words) < 2 or len(words) > 8:
        print("Invalid Statement: Sentence must have between 2 and 8 words.")
        return
    
    # Lex and parse
    try:
        lexer.input(input_sentence.lower())
        tokens = [(tok.type, tok.value) for tok in lexer]
        print("Tokens:", tokens)
        
        result = parser.parse(input_sentence.lower())
        if result:
            print(result)
        else:
            print("Invalid Statement.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
