import re

def validar_nome(nome):
    if not nome or len(nome.strip().split()) < 2:
        return False, "O nome deve ser completo."
    if any(char.isdigit() for char in nome):
        return False, "O nome não pode conter números."
    return True, ""

def validar_peso(peso):
    try:
        p = float(peso)
        if 0.1 <= p <= 150.0:
            return True, ""
        return False, "O peso deve estar entre 0.1kg e 150kg."
    except:
        return False, "Digite um peso válido."

def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11:
        return False, "O CPF deve ter 11 dígitos."
    return True, ""