import sys
current_word = None
current_count = 0

for line in sys.stdin:
    try:
        word, count = line.strip().split('\t')
        try:
            count = int(count)
        except ValueError:
            continue

        if current_word == word and current_count < 10:
            current_count += count
        else:
            if current_word:
                print(f"{current_word}\t{current_count}")
            current_word = word
            current_count = count
    except ValueError:
        continue

if current_word:
    print(f"{current_word}\t{current_count}")