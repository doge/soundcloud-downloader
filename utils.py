import re


def remove_forbidden_chars(string):
    return re.sub(r'[\\/*?:"<>|]', "", string)
