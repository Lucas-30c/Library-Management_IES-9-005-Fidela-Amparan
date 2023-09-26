import string
from unidecode import unidecode

prep = ["a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "en", "entre", "hacia", "hasta", "para", "por",
        "según", "sin", "so", "sobre", "tras", "el", "la", "los"]


def clean_str_sig(str):
    clean_str = unidecode(str)
    clean_str = ''.join(
        char for char in clean_str if char not in string.punctuation)

    return clean_str.lower()


def build_list(str):
    words = str.split()
    word_list = []
    for i in words:
        cleaned_word = clean_str_sig(i)
        if cleaned_word not in prep and len(cleaned_word) > 0:
            word_list.append(cleaned_word)

    return word_list
