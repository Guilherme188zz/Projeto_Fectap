"""
Script de população do banco de dados Gnuvet.
Execute com: python popular_banco.py
Cria: 15 médicos, 30 tutores, ~45 pets e ~3 meses de consultas.
"""

import sqlite3
import random
from datetime import date, timedelta

DB = 'clinica_gnuvet.db'


def conectar():
    return sqlite3.connect(DB)


# ---------------------------------------------------------------------------
# Dados base
# ---------------------------------------------------------------------------

MEDICOS = [
    # (nome, crm, especialidade, especies, dias, h_inicio, h_fim, telefone)
    ("Dr. Carlos Eduardo Mendes",   "12345-SP", "Clínico Geral",             "Canina,Felina",                      "Segunda,Terça,Quarta,Quinta,Sexta",   "08:00", "17:00", "11991110001"),
    ("Dra. Fernanda Lima Rocha",    "23456-SP", "Clínico Geral",             "Canina,Felina,Roedor,Ave",           "Segunda,Quarta,Sexta",                "09:00", "18:00", "11991110002"),
    ("Dr. Ricardo Alves Costa",     "34567-SP", "Cirurgião",                 "Canina,Felina",                      "Terça,Quarta,Quinta",                 "07:00", "16:00", "11991110003"),
    ("Dra. Juliana Martins Souza",  "45678-SP", "Dermatologista",            "Canina,Felina,Roedor",               "Segunda,Terça,Quinta,Sexta",          "08:00", "17:00", "11991110004"),
    ("Dr. Paulo Henrique Torres",   "56789-SP", "Oncologista",               "Canina,Felina",                      "Quarta,Quinta,Sexta",                 "08:00", "16:00", "11991110005"),
    ("Dra. Camila Ferreira Nunes",  "67890-SP", "Cardiologista",             "Canina,Felina,Ave",                  "Segunda,Terça,Quarta",                "09:00", "18:00", "11991110006"),
    ("Dr. Anderson Brito Leal",     "78901-SP", "Ortopedista",               "Canina,Felina",                      "Terça,Quinta,Sexta",                  "07:00", "15:00", "11991110007"),
    ("Dra. Patrícia Gomes Vieira",  "89012-SP", "Clínico Geral",             "Canina,Felina,Réptil,Ave,Aquático",  "Segunda,Quarta,Quinta,Sexta",         "08:00", "17:00", "11991110008"),
    ("Dr. Bruno Nascimento Pires",  "90123-SP", "Oftalmologista",            "Canina,Felina",                      "Segunda,Terça,Quarta,Quinta",         "09:00", "17:00", "11991110009"),
    ("Dra. Letícia Cardoso Melo",   "01234-SP", "Nutricionista",             "Canina,Felina,Roedor,Ave",           "Terça,Quarta,Sexta",                  "08:00", "16:00", "11991110010"),
    ("Dr. Gustavo Pereira Ramos",   "11223-SP", "Clínico Geral",             "Réptil,Ave,Aquático,Roedor",         "Segunda,Terça,Quarta,Quinta,Sexta",   "08:00", "17:00", "11991110011"),
    ("Dra. Mariana Oliveira Cruz",  "22334-SP", "Dermatologista",            "Canina,Felina,Réptil",               "Segunda,Quarta,Sexta",                "09:00", "18:00", "11991110012"),
    ("Dr. Felipe Santos Barros",    "33445-SP", "Anestesiologista",          "Canina,Felina",                      "Terça,Quarta,Quinta",                 "07:00", "15:00", "11991110013"),
    ("Dra. Vanessa Teixeira Dias",  "44556-SP", "Odontologista Veterinário", "Canina,Felina",                      "Segunda,Terça,Quinta,Sexta",          "08:00", "17:00", "11991110014"),
    ("Dr. Rodrigo Cavalcante Lima", "55667-SP", "Clínico Geral",             "Canina,Felina,Ave,Roedor,Aquático",  "Segunda,Terça,Quarta,Quinta,Sexta",   "08:00", "18:00", "11991110015"),
]

TUTORES = [
    ("Ana Clara Ferreira",    "52998765432", "11981230001"),
    ("Bruno Henrique Silva",  "11144477735", "11981230002"),
    ("Carla Regina Sousa",    "22255588847", "11981230003"),
    ("Daniel Augusto Lima",   "33366699951", "11981230004"),
    ("Eliane Costa Martins",  "44477711162", "11981230005"),
    ("Fábio Rodrigues Neto",  "55588822274", "11981230006"),
    ("Gabriela Mendes Pinto", "66699933385", "11981230007"),
    ("Henrique Barros Cruz",  "77711044496", "11981230008"),
    ("Isabela Teixeira Melo", "88822155508", "11981230009"),
    ("João Pedro Alves",      "99933266610", "11981230010"),
    ("Karen Lopes Vieira",    "12312312387", "11981230011"),
    ("Lucas Pereira Gomes",   "23423423498", "11981230012"),
    ("Mariana Santos Rocha",  "34534534509", "11981230013"),
    ("Nelson Araújo Dias",    "45645645610", "11981230014"),
    ("Olivia Carvalho Reis",  "56756756721", "11981230015"),
    ("Pedro Nascimento Brum", "67867867832", "11981230016"),
    ("Quintina Farias Luz",   "78978978943", "11981230017"),
    ("Rafael Moreira Viana",  "89089089054", "11981230018"),
    ("Sandra Borges Queiroz", "90190190165", "11981230019"),
    ("Thiago Cunha Macedo",   "01201201276", "11981230020"),
    ("Úrsula Prado Freitas",  "12312312398", "11981230021"),
    ("Vinícius Esteves Lago", "23423423409", "11981230022"),
    ("Wanda Correia Falcão",  "34534534511", "11981230023"),
    ("Xavier Monteiro Pais",  "45645645622", "11981230024"),
    ("Yasmin Ribeiro Fontes", "56756756733", "11981230025"),
    ("Zélia Andrade Braga",   "67867867844", "11981230026"),
    ("Aldo Figueiredo Costa", "78978978955", "11981230027"),
    ("Beatriz Sampaio Nunes", "89089089066", "11981230028"),
    ("Cláudio Rezende Porto", "90190190177", "11981230029"),
    ("Débora Lacerda Maia",   "01201201288", "11981230030"),
]

# (nome_pet, especie, raca, peso_min, peso_max)
PETS_POOL = [
    ("Thor",      "Canina",  "Labrador Retriever",         20.0, 35.0),
    ("Luna",      "Felina",  "SRD (Sem Raça Definida)",    3.0,  5.0),
    ("Max",       "Canina",  "Golden Retriever",           25.0, 38.0),
    ("Mel",       "Felina",  "Persa",                      3.5,  5.5),
    ("Bob",       "Canina",  "Beagle",                     9.0,  14.0),
    ("Nina",      "Felina",  "Siamês",                     3.0,  4.5),
    ("Rex",       "Canina",  "Pastor Alemão",              25.0, 40.0),
    ("Pitoca",    "Canina",  "Poodle",                     5.0,  8.0),
    ("Simba",     "Felina",  "Maine Coon",                 5.0,  8.0),
    ("Bolinha",   "Canina",  "Shih Tzu",                   4.0,  7.0),
    ("Fifi",      "Felina",  "Ragdoll",                    4.0,  7.0),
    ("Toby",      "Canina",  "Yorkshire Terrier",          2.0,  4.0),
    ("Cacau",     "Canina",  "Dachshund",                  5.0,  9.0),
    ("Biscuit",   "Canina",  "Bulldog Francês",            8.0,  14.0),
    ("Kira",      "Felina",  "Bengal",                     4.0,  6.0),
    ("Pipoca",    "Ave",     "Calopsita",                  0.08, 0.12),
    ("Polly",     "Ave",     "Periquito Australiano",      0.03, 0.05),
    ("Tweety",    "Ave",     "Canário",                    0.02, 0.04),
    ("Loro",      "Ave",     "Papagaio",                   0.35, 0.55),
    ("Hammy",     "Roedor",  "Hamster",                    0.08, 0.15),
    ("Fofinha",   "Roedor",  "Cobaia (porquinho-da-índia)",0.5,  1.2),
    ("Chincho",   "Roedor",  "Chinchila",                  0.4,  0.7),
    ("Iggy",      "Réptil",  "Iguana",                     1.0,  4.0),
    ("Jabuti",    "Réptil",  "Jabuti",                     0.5,  3.0),
    ("Nemo",      "Peixe",   "Betta",                      0.01, 0.02),
    ("Ariel",     "Peixe",   "Koi",                        0.5,  2.0),
    ("Duque",     "Canina",  "Rottweiler",                 35.0, 55.0),
    ("Princesa",  "Felina",  "Russo Azul",                 3.0,  5.0),
    ("Bento",     "Canina",  "Border Collie",              14.0, 22.0),
    ("Zara",      "Canina",  "Husky Siberiano",            20.0, 30.0),
]

TIPOS_CONSULTA = [
    "Consulta Geral", "Vacinação", "Retorno",
    "Cirurgia", "Exame", "Emergência",
]

MOTIVOS = {
    "Consulta Geral": [
        "Check-up anual", "Avaliação geral", "Queixa de letargia",
        "Perda de apetite", "Exame de rotina", "Avaliação de peso",
    ],
    "Vacinação": [
        "Vacina V10", "Vacina antirrábica", "Vacina tríplice felina",
        "Reforço vacinal anual", "Vacina Giardia", "Vacina gripe canina",
    ],
    "Retorno": [
        "Retorno pós-cirurgia", "Retorno pós-tratamento",
        "Acompanhamento de quadro clínico", "Reavaliação dermatológica",
    ],
    "Cirurgia": [
        "Castração", "Extração dentária", "Remoção de nódulo",
        "Correção de fratura", "Cirurgia exploratória",
    ],
    "Exame": [
        "Hemograma completo", "Ultrassom abdominal", "Raio-X torácico",
        "Exame parasitológico", "Ecocardiograma", "Cultivo e antibiograma",
    ],
    "Emergência": [
        "Ingestão de corpo estranho", "Convulsão", "Trauma por atropelamento",
        "Dispneia aguda", "Intoxicação", "Sangramento intenso",
    ],
}

STATUS_PESOS = {
    "realizada": 60,
    "agendada":  30,
    "cancelada": 10,
}

HORARIOS = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30",
            "11:00", "11:30", "13:00", "13:30", "14:00", "14:30",
            "15:00", "15:30", "16:00", "16:30", "17:00"]

DIAS_SEMANA_MAP = {0:"Segunda",1:"Terça",2:"Quarta",3:"Quinta",4:"Sexta",5:"Sábado",6:"Domingo"}


def cpf_valido(cpf_str: str) -> str:
    """Garante que o CPF tenha 11 dígitos."""
    return cpf_str.zfill(11)[:11]


def popular():
    conexao = conectar()
    cursor  = conexao.cursor()

    # ── Garante estrutura do banco ────────────────────────────────────────
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS tutores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL, cpf TEXT NOT NULL UNIQUE, telefone TEXT
        );
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL, especie TEXT NOT NULL, raca TEXT NOT NULL,
            tutor_id INTEGER NOT NULL, peso REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS medicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL, crm TEXT NOT NULL UNIQUE,
            especialidade TEXT NOT NULL, especies TEXT NOT NULL,
            dias_trabalho TEXT NOT NULL,
            horario_inicio TEXT NOT NULL DEFAULT '08:00',
            horario_fim    TEXT NOT NULL DEFAULT '18:00',
            telefone TEXT
        );
        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL, data_consulta TEXT NOT NULL,
            horario TEXT NOT NULL, motivo TEXT,
            status TEXT NOT NULL DEFAULT 'agendada',
            observacoes TEXT, tipo_consulta TEXT DEFAULT 'Consulta Geral',
            medico_id INTEGER
        );
    """)

    # Migração segura
    for cmd in [
        "ALTER TABLE consultas ADD COLUMN tipo_consulta TEXT DEFAULT 'Consulta Geral'",
        "ALTER TABLE consultas ADD COLUMN medico_id INTEGER",
        "ALTER TABLE pets ADD COLUMN peso REAL NOT NULL DEFAULT 0",
        "ALTER TABLE consultas ADD COLUMN horario TEXT NOT NULL DEFAULT '00:00'",
        "ALTER TABLE consultas ADD COLUMN status TEXT NOT NULL DEFAULT 'agendada'",
        "ALTER TABLE consultas ADD COLUMN observacoes TEXT",
    ]:
        try:
            cursor.execute(cmd)
        except Exception:
            pass

    conexao.commit()

    # ── Médicos ───────────────────────────────────────────────────────────
    print("Inserindo médicos...")
    ids_medicos = []
    for m in MEDICOS:
        try:
            cursor.execute(
                "INSERT INTO medicos (nome,crm,especialidade,especies,dias_trabalho,horario_inicio,horario_fim,telefone) VALUES (?,?,?,?,?,?,?,?)",
                m
            )
            ids_medicos.append(cursor.lastrowid)
        except sqlite3.IntegrityError:
            row = cursor.execute("SELECT id FROM medicos WHERE crm=?", (m[1],)).fetchone()
            if row:
                ids_medicos.append(row[0])
    conexao.commit()
    print(f"  ✅ {len(ids_medicos)} médicos prontos.")

    # ── Tutores ───────────────────────────────────────────────────────────
    print("Inserindo tutores...")
    ids_tutores = []
    for t in TUTORES:
        cpf_limpo = cpf_valido(t[1])
        try:
            cursor.execute(
                "INSERT INTO tutores (nome,cpf,telefone) VALUES (?,?,?)",
                (t[0], cpf_limpo, t[2])
            )
            ids_tutores.append(cursor.lastrowid)
        except sqlite3.IntegrityError:
            row = cursor.execute("SELECT id FROM tutores WHERE cpf=?", (cpf_limpo,)).fetchone()
            if row:
                ids_tutores.append(row[0])
    conexao.commit()
    print(f"  ✅ {len(ids_tutores)} tutores prontos.")

    # ── Pets — 1 a 2 pets por tutor ───────────────────────────────────────
    print("Inserindo pets...")
    ids_pets_info = []  # (pet_id, especie)
    pets_embaralhados = PETS_POOL.copy()
    random.shuffle(pets_embaralhados)
    idx_pet = 0

    for tutor_id in ids_tutores:
        qtd = random.randint(1, 2)
        for _ in range(qtd):
            pet = pets_embaralhados[idx_pet % len(pets_embaralhados)]
            idx_pet += 1
            nome_p, especie, raca, pmin, pmax = pet
            peso = round(random.uniform(pmin, pmax), 1)
            # Sobrenome do tutor no nome do pet para realismo
            cursor.execute(
                "INSERT INTO pets (nome,especie,raca,tutor_id,peso) VALUES (?,?,?,?,?)",
                (nome_p, especie, raca, tutor_id, peso)
            )
            ids_pets_info.append((cursor.lastrowid, especie))

    conexao.commit()
    print(f"  ✅ {len(ids_pets_info)} pets prontos.")

    # ── Consultas — 3 meses (passado + futuro) ────────────────────────────
    print("Inserindo consultas...")
    hoje      = date.today()
    inicio    = hoje - timedelta(days=60)   # 2 meses atrás
    fim       = hoje + timedelta(days=30)   # 1 mês à frente
    delta     = (fim - inicio).days

    # Pré-carrega médicos com dias/espécies para busca rápida
    medicos_db = cursor.execute(
        "SELECT id, dias_trabalho, especies FROM medicos"
    ).fetchall()

    total_consultas = 0
    # Gera ~5 consultas por pet
    for pet_id, especie in ids_pets_info:
        num_consultas = random.randint(4, 7)
        datas_usadas: set = set()

        for _ in range(num_consultas):
            # Escolhe data aleatória no período
            for tentativa in range(20):
                offset = random.randint(0, delta)
                data_c = inicio + timedelta(days=offset)
                # Evita duplicatas no mesmo dia para o mesmo pet
                if data_c not in datas_usadas:
                    datas_usadas.add(data_c)
                    break
            else:
                continue

            dia_semana_pt = DIAS_SEMANA_MAP[data_c.weekday()]
            horario = random.choice(HORARIOS)
            tipo    = random.choices(
                list(TIPOS_CONSULTA),
                weights=[30, 25, 15, 10, 15, 5]
            )[0]
            motivo  = random.choice(MOTIVOS[tipo])

            # Define status baseado na data
            if data_c < hoje:
                status = random.choices(
                    ["realizada", "cancelada"],
                    weights=[85, 15]
                )[0]
            elif data_c == hoje:
                status = "agendada"
            else:
                status = random.choices(
                    ["agendada", "cancelada"],
                    weights=[90, 10]
                )[0]

            # Encontra médico compatível (dia + espécie)
            medico_id = None
            candidatos = [
                m[0] for m in medicos_db
                if dia_semana_pt in m[1] and especie in m[2]
            ]
            if candidatos:
                medico_id = random.choice(candidatos)

            try:
                cursor.execute(
                    """INSERT INTO consultas
                       (pet_id, data_consulta, horario, motivo, status, tipo_consulta, medico_id)
                       VALUES (?,?,?,?,?,?,?)""",
                    (pet_id, str(data_c), horario, motivo, status, tipo, medico_id)
                )
                total_consultas += 1
            except Exception:
                pass

    conexao.commit()
    print(f"  ✅ {total_consultas} consultas geradas.")
    conexao.close()

    print("\n🎉 Banco populado com sucesso!")
    print(f"   • {len(ids_medicos)} médicos")
    print(f"   • {len(ids_tutores)} tutores")
    print(f"   • {len(ids_pets_info)} pets")
    print(f"   • {total_consultas} consultas (de {inicio} até {fim})")


if __name__ == "__main__":
    popular()
