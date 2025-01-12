d Program:")
while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)