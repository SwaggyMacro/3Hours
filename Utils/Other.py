import random


def random_replace_star(string: str) -> str:
    for i in range(int(len(string) / 4)):
        string = string.replace(string[random.randint(0, len(string) - 1)], '*')
    return string
