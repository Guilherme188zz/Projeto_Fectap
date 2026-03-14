import re


# ---------------------------------------------------------------------------
# Validação de Nome
# ---------------------------------------------------------------------------

def validar_nome(nome: str) -> tuple[bool, str]:
    """Valida o nome do tutor: mínimo 2 palavras, sem números, sem caracteres especiais."""
    if not nome or not nome.strip():
        return False, "O nome não pode estar vazio."
    nome = nome.strip()
    if any(caractere.isdigit() for caractere in nome):
        return False, "O nome não pode conter números."
    if not re.match(r"^[A-Za-zÀ-ÿ\s'-]+$", nome):
        return False, "O nome contém caracteres inválidos."
    partes = [parte for parte in nome.split() if parte]
    if len(partes) < 2:
        return False, "Informe o nome completo (nome e sobrenome)."
    if any(len(parte) < 2 for parte in partes):
        return False, "Cada parte do nome deve ter pelo menos 2 letras."
    return True, ""


def validar_nome_pet(nome: str) -> tuple[bool, str]:
    """Valida o nome do pet: mínimo 2 palavras, sem números, sem caracteres especiais."""
    if not nome or not nome.strip():
        return False, "O nome do pet não pode estar vazio."
    nome = nome.strip()
    if any(caractere.isdigit() for caractere in nome):
        return False, "O nome do pet não pode conter números."
    if not re.match(r"^[A-Za-zÀ-ÿ\s'-]+$", nome):
        return False, "O nome do pet contém caracteres inválidos."
    partes = [parte for parte in nome.split() if parte]
    if len(partes) < 2:
        return False, "Informe o nome completo do pet (ex: Rex Silva)."
    return True, ""


# ---------------------------------------------------------------------------
# Validação de Peso
# ---------------------------------------------------------------------------

def validar_peso(peso) -> tuple[bool, str]:
    """Valida o peso do pet: deve estar entre 0,1 kg e 150 kg."""
    try:
        valor = float(peso)
        if 0.1 <= valor <= 150.0:
            return True, ""
        return False, "O peso deve estar entre 0,1 kg e 150 kg."
    except (ValueError, TypeError):
        return False, "Digite um peso válido."


# ---------------------------------------------------------------------------
# Validação de CPF — algoritmo oficial com dígitos verificadores
# ---------------------------------------------------------------------------

def validar_cpf(cpf: str) -> tuple[bool, str]:
    """Valida o CPF usando o algoritmo oficial da Receita Federal."""
    # Remove tudo que não for dígito
    cpf_limpo = re.sub(r'\D', '', cpf)

    if not cpf_limpo:
        return False, "O CPF não pode estar vazio."
    if not cpf_limpo.isdigit():
        return False, "O CPF deve conter apenas números."
    if len(cpf_limpo) != 11:
        return False, "O CPF deve ter 11 dígitos."

    # Rejeita sequências repetidas como 111.111.111-11 ou 000.000.000-00
    if len(set(cpf_limpo)) == 1:
        return False, "CPF inválido."

    # Cálculo do 1º dígito verificador
    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    resto = (soma * 10) % 11
    primeiro_digito = 0 if resto >= 10 else resto

    if primeiro_digito != int(cpf_limpo[9]):
        return False, "CPF inválido — dígito verificador incorreto."

    # Cálculo do 2º dígito verificador
    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    resto = (soma * 10) % 11
    segundo_digito = 0 if resto >= 10 else resto

    if segundo_digito != int(cpf_limpo[10]):
        return False, "CPF inválido — dígito verificador incorreto."

    return True, ""


# ---------------------------------------------------------------------------
# Validação de Telefone
# ---------------------------------------------------------------------------

def validar_telefone(telefone: str) -> tuple[bool, str]:
    """Valida o telefone: opcional, mas se preenchido deve ter DDD + 8 ou 9 dígitos."""
    somente_numeros = re.sub(r'\D', '', telefone)
    if somente_numeros and len(somente_numeros) not in (10, 11):
        return False, "Telefone inválido. Use (DDD) + número com 8 ou 9 dígitos."
    return True, ""