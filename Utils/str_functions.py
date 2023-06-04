prep = ["a", "ante", "bajo", "cabe", "con", "contra", "de", "desde", "en", "entre", "hacia", "hasta", "para", "por",
        "según", "sin", "so", "sobre", "tras", "el", "la", "los"]
signos = [',', ';', '?', '¿', '!', '¡', '(', ')', '-', '_', '.', "á", "é", "í", "ó", "ú", "Á", "É", "Í", "Ó", "Ú"]


def clean_str_sig(str):
    for c in str:
        if c in signos:
            str = str.replace(c, '')

    return str.lower()


def build_list(str):
    p = str.split()
    lista = []
    for i in p:
        a = clean_str_sig(i)
        if a not in prep:
            lista.append(a)

    return lista



