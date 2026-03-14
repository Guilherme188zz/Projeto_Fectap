import sqlite3


def criar_banco():
    """Cria todas as tabelas do banco de dados caso ainda não existam."""
    conexao = sqlite3.connect('clinica_gnuvet.db')
    cursor = conexao.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tutores (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nome      TEXT    NOT NULL,
            cpf       TEXT    NOT NULL UNIQUE,
            telefone  TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nome     TEXT    NOT NULL,
            especie  TEXT    NOT NULL,
            raca     TEXT    NOT NULL,
            tutor_id INTEGER NOT NULL,
            peso     REAL    NOT NULL,
            FOREIGN KEY (tutor_id) REFERENCES tutores(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consultas (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id         INTEGER NOT NULL,
            data_consulta  TEXT    NOT NULL,
            horario        TEXT    NOT NULL,
            motivo         TEXT,
            status         TEXT    NOT NULL DEFAULT 'agendada',
            observacoes    TEXT,
            FOREIGN KEY (pet_id) REFERENCES pets(id)
        )
    ''')

    # Migração segura: adiciona coluna peso se o banco antigo não a tiver
    try:
        cursor.execute("ALTER TABLE pets ADD COLUMN peso REAL NOT NULL DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # Coluna já existe, nenhuma ação necessária

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicos (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            nome           TEXT    NOT NULL,
            crm            TEXT    NOT NULL UNIQUE,
            especialidade  TEXT    NOT NULL,
            especies       TEXT    NOT NULL,
            dias_trabalho  TEXT    NOT NULL,
            horario_inicio TEXT    NOT NULL DEFAULT '08:00',
            horario_fim    TEXT    NOT NULL DEFAULT '18:00',
            telefone       TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            login      TEXT    NOT NULL UNIQUE,
            senha      TEXT    NOT NULL,
            perfil     TEXT    NOT NULL,
            nome       TEXT    NOT NULL,
            medico_id  INTEGER
        )
    ''')

    # Cria usuários padrão se a tabela estiver vazia
    total_usuarios = cursor.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    if total_usuarios == 0:
        import hashlib
        def h(s): return hashlib.sha256(s.encode()).hexdigest()

        usuarios_padrao = [
            # Médicos em ordem alfabética — sala crescente
            ('anderson', h('Anderson1'),  'medico',    'Dr. Anderson Brito Leal',     None),
            ('bruno',    h('Bruno2'),     'medico',    'Dr. Bruno Nascimento Pires',  None),
            ('carlos',   h('Carlos3'),    'medico',    'Dr. Carlos Eduardo Mendes',   None),
            ('felipe',   h('Felipe4'),    'medico',    'Dr. Felipe Santos Barros',    None),
            ('gustavo',  h('Gustavo5'),   'medico',    'Dr. Gustavo Pereira Ramos',   None),
            ('paulo',    h('Paulo6'),     'medico',    'Dr. Paulo Henrique Torres',   None),
            ('ricardo',  h('Ricardo7'),   'medico',    'Dr. Ricardo Alves Costa',     None),
            ('rodrigo',  h('Rodrigo8'),   'medico',    'Dr. Rodrigo Cavalcante Lima', None),
            ('camila',   h('Camila9'),    'medico',    'Dra. Camila Ferreira Nunes',  None),
            ('fernanda', h('Fernanda10'), 'medico',    'Dra. Fernanda Lima Rocha',    None),
            ('juliana',  h('Juliana11'),  'medico',    'Dra. Juliana Martins Souza',  None),
            ('leticia',  h('Leticia12'),  'medico',    'Dra. Letícia Cardoso Melo',   None),
            ('mariana',  h('Mariana13'),  'medico',    'Dra. Mariana Oliveira Cruz',  None),
            ('patricia', h('Patricia14'), 'medico',    'Dra. Patrícia Gomes Vieira',  None),
            ('vanessa',  h('Vanessa15'),  'medico',    'Dra. Vanessa Teixeira Dias',  None),
            # Atendentes
            ('atendente1', h('CuidarAfeto1'), 'atendente', 'Atendente 1', None),
            ('atendente2', h('CuidarAfeto2'), 'atendente', 'Atendente 2', None),
            # Administrador
            ('guilherme', h('Programadorn1'), 'admin', 'Guilherme', None),
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO usuarios (login, senha, perfil, nome, medico_id) VALUES (?,?,?,?,?)",
            usuarios_padrao
        )

    # Migração segura: adiciona colunas novas na tabela consultas se necessário
    colunas_novas = [
        "ALTER TABLE consultas ADD COLUMN status TEXT NOT NULL DEFAULT 'agendada'",
        "ALTER TABLE consultas ADD COLUMN observacoes TEXT",
        "ALTER TABLE consultas ADD COLUMN horario TEXT NOT NULL DEFAULT '00:00'",
        "ALTER TABLE consultas ADD COLUMN tipo_consulta TEXT NOT NULL DEFAULT 'Consulta Geral'",
        "ALTER TABLE consultas ADD COLUMN medico_id INTEGER",
    ]
    for comando in colunas_novas:
        try:
            cursor.execute(comando)
        except sqlite3.OperationalError:
            pass  # Coluna já existe, nenhuma ação necessária

    conexao.commit()
    conexao.close()
    print("✅ Banco de dados pronto!")


if __name__ == "__main__":
    criar_banco()