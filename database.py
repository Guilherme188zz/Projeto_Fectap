import sqlite3

def criar_banco():
    conn = sqlite3.connect('clinica_gnuvet.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS tutores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cpf TEXT, telefone TEXT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS pets (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, especie TEXT, raca TEXT, tutor_id INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS consultas (id INTEGER PRIMARY KEY AUTOINCREMENT, pet_id INTEGER, data_consulta TEXT, horario TEXT, motivo TEXT)')
    conn.commit()
    conn.close()
    print("✅ Banco pronto!")

if __name__ == "__main__":
    criar_banco()