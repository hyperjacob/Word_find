import random

def dictionary(filename, stage):
    if stage == 1:
        start = 3
        finish = 4
    elif stage == 2:
        start = 5
        finish = 8
    elif stage == 3:
        start = 9
        finish = 15
    else:
        start = 3
        finish = 6
    word = ""
    with open(filename) as words:
        lines = words.readlines()
        while True:
            random_line = random.choice(lines).strip()
            if (len(random_line) >= start) and (len(random_line) <= finish):
                word = random_line
                break
    return word
