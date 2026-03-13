import sqlite3
import pandas as pd

def conectar():
    return sqlite3.connect('clinica_gnuvet.db')

def cadastrar_tutor(nome, cpf, telefone):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tutores (nome, cpf, telefone) VALUES (?, ?, ?)", (nome, cpf, telefone))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def cadastrar_pet(nome, especie, raca, tutor_id, peso):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO pets (nome, especie, raca, tutor_id, peso) VALUES (?, ?, ?, ?, ?)", 
                       (nome, especie, raca, tutor_id, peso))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def listar_clientes_e_pets():
    conn = conectar()
    query = """
    SELECT tutores.id, tutores.nome as Dono, pets.nome as Pet, pets.especie 
    FROM tutores LEFT JOIN pets ON tutores.id = pets.tutor_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df