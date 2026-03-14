import sqlite3
import pandas as pd
from datetime import date
from database import criar_banco

# Garante que o banco existe e está atualizado ao importar o módulo
criar_banco()


# ---------------------------------------------------------------------------
# Conexão com o banco de dados
# ---------------------------------------------------------------------------

def conectar() -> sqlite3.Connection:
    """Retorna uma conexão com o banco de dados da clínica."""
    return sqlite3.connect('clinica_gnuvet.db')


# ---------------------------------------------------------------------------
# Tutores
# ---------------------------------------------------------------------------

def cadastrar_tutor(nome: str, cpf: str, telefone: str) -> tuple[bool, str]:
    """Cadastra um novo tutor no banco de dados."""
    cpf_limpo = cpf.replace('.', '').replace('-', '').strip()
    conexao = conectar()
    try:
        conexao.execute(
            "INSERT INTO tutores (nome, cpf, telefone) VALUES (?, ?, ?)",
            (nome.strip(), cpf_limpo, telefone.strip())
        )
        conexao.commit()
        return True, "Tutor cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "CPF já cadastrado no sistema."
    except sqlite3.Error as erro:
        return False, f"Erro no banco de dados: {erro}"
    finally:
        conexao.close()


def buscar_tutor_por_cpf(cpf: str) -> dict | None:
    """Busca um tutor pelo CPF. Retorna um dicionário ou None se não encontrado."""
    cpf_limpo = cpf.replace('.', '').replace('-', '').strip()
    conexao = conectar()
    try:
        cursor = conexao.execute("SELECT * FROM tutores WHERE cpf = ?", (cpf_limpo,))
        linha = cursor.fetchone()
        if linha:
            colunas = [descricao[0] for descricao in cursor.description]
            return dict(zip(colunas, linha))
        return None
    finally:
        conexao.close()


# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

def cadastrar_pet(nome: str, especie: str, raca: str, tutor_id: int, peso: float) -> tuple[bool, str]:
    """Cadastra um novo pet vinculado a um tutor."""
    conexao = conectar()
    try:
        conexao.execute(
            "INSERT INTO pets (nome, especie, raca, tutor_id, peso) VALUES (?, ?, ?, ?, ?)",
            (nome.strip(), especie, raca, tutor_id, peso)
        )
        conexao.commit()
        return True, "Pet cadastrado com sucesso!"
    except sqlite3.Error as erro:
        return False, f"Erro no banco de dados: {erro}"
    finally:
        conexao.close()


def listar_pets_por_tutor(tutor_id: int) -> pd.DataFrame:
    """Retorna todos os pets de um tutor específico."""
    conexao = conectar()
    try:
        df = pd.read_sql_query(
            "SELECT id, nome, especie, raca, peso FROM pets WHERE tutor_id = ?",
            conexao, params=(tutor_id,)
        )
        return df
    finally:
        conexao.close()


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------

def agendar_consulta(pet_id: int, data: str, horario: str, motivo: str,
                     tipo_consulta: str = "Consulta Geral",
                     medico_id: int | None = None) -> tuple[bool, str]:
    """Agenda uma nova consulta para um pet, verificando conflito de horário."""
    conexao = conectar()
    try:
        # Verifica se já existe consulta para este pet no mesmo horário
        cursor = conexao.execute(
            "SELECT id FROM consultas WHERE pet_id = ? AND data_consulta = ? AND horario = ? AND status != 'cancelada'",
            (pet_id, data, horario)
        )
        if cursor.fetchone():
            return False, "Já existe uma consulta agendada para este pet neste horário."

        # Verifica conflito de horário do médico
        if medico_id:
            cursor = conexao.execute(
                "SELECT id FROM consultas WHERE medico_id = ? AND data_consulta = ? AND horario = ? AND status != 'cancelada'",
                (medico_id, data, horario)
            )
            if cursor.fetchone():
                return False, "Este médico já possui uma consulta neste horário. Escolha outro horário ou médico."

        conexao.execute(
            """INSERT INTO consultas
               (pet_id, data_consulta, horario, motivo, status, tipo_consulta, medico_id)
               VALUES (?, ?, ?, ?, 'agendada', ?, ?)""",
            (pet_id, data, horario, motivo, tipo_consulta, medico_id)
        )
        conexao.commit()
        return True, "Consulta agendada com sucesso!"
    except sqlite3.Error as erro:
        return False, f"Erro no banco de dados: {erro}"
    finally:
        conexao.close()


def listar_consultas_agendadas() -> pd.DataFrame:
    """Retorna todas as consultas com status 'agendada', ordenadas por data e horário."""
    conexao = conectar()
    try:
        consulta_sql = """
            SELECT
                c.id,
                t.nome  AS Tutor,
                p.nome  AS Pet,
                p.especie AS Espécie,
                c.data_consulta AS Data,
                c.horario       AS Horário,
                c.motivo        AS Motivo,
                c.status        AS Status
            FROM consultas c
            JOIN pets    p ON c.pet_id   = p.id
            JOIN tutores t ON p.tutor_id = t.id
            WHERE c.status = 'agendada'
            ORDER BY c.data_consulta, c.horario
        """
        return pd.read_sql_query(consulta_sql, conexao)
    finally:
        conexao.close()


def listar_historico_consultas() -> pd.DataFrame:
    """Retorna o histórico completo de consultas, da mais recente para a mais antiga."""
    conexao = conectar()
    try:
        consulta_sql = """
            SELECT
                c.id,
                t.nome  AS Tutor,
                p.nome  AS Pet,
                p.especie AS Espécie,
                c.data_consulta AS Data,
                c.horario       AS Horário,
                c.motivo        AS Motivo,
                c.status        AS Status,
                c.observacoes   AS Observações
            FROM consultas c
            JOIN pets    p ON c.pet_id   = p.id
            JOIN tutores t ON p.tutor_id = t.id
            ORDER BY c.data_consulta DESC, c.horario DESC
        """
        return pd.read_sql_query(consulta_sql, conexao)
    finally:
        conexao.close()


def atualizar_consulta(consulta_id: int, novo_status: str, observacoes: str = "") -> tuple[bool, str]:
    """Atualiza o status e as observações de uma consulta existente."""
    status_permitidos = ('agendada', 'realizada', 'cancelada')
    if novo_status not in status_permitidos:
        return False, f"Status inválido. Use um dos seguintes: {status_permitidos}"
    conexao = conectar()
    try:
        cursor = conexao.execute(
            "UPDATE consultas SET status = ?, observacoes = ? WHERE id = ?",
            (novo_status, observacoes, consulta_id)
        )
        conexao.commit()
        if cursor.rowcount == 0:
            return False, "Consulta não encontrada."
        return True, f"Consulta atualizada para '{novo_status}' com sucesso."
    except sqlite3.Error as erro:
        return False, f"Erro no banco de dados: {erro}"
    finally:
        conexao.close()


def listar_clientes_e_pets() -> pd.DataFrame:
    """Retorna uma visão geral de todos os tutores e seus respectivos pets."""
    conexao = conectar()
    try:
        consulta_sql = """
            SELECT
                t.id,
                t.nome      AS Tutor,
                t.cpf       AS CPF,
                t.telefone  AS Telefone,
                p.nome      AS Pet,
                p.especie   AS Espécie,
                p.raca      AS Raça,
                p.peso      AS "Peso (kg)"
            FROM tutores t
            LEFT JOIN pets p ON t.id = p.tutor_id
            ORDER BY t.nome
        """
        return pd.read_sql_query(consulta_sql, conexao)
    finally:
        conexao.close()


# ---------------------------------------------------------------------------
# Dados para gráficos
# ---------------------------------------------------------------------------

def vacinacoes_hoje() -> pd.DataFrame:
    """Retorna todas as consultas agendadas para o dia de hoje."""
    conexao = conectar()
    try:
        hoje = date.today().isoformat()
        consulta_sql = """
            SELECT
                t.nome        AS Tutor,
                p.nome        AS Pet,
                c.horario     AS Horário,
                c.motivo      AS Motivo,
                c.tipo_consulta AS Tipo
            FROM consultas c
            JOIN pets    p ON c.pet_id   = p.id
            JOIN tutores t ON p.tutor_id = t.id
            WHERE c.data_consulta = ?
              AND c.status = 'agendada'
            ORDER BY c.horario
        """
        return pd.read_sql_query(consulta_sql, conexao, params=(hoje,))
    finally:
        conexao.close()


def dados_grafico_consultas_por_mes() -> pd.DataFrame:
    """Retorna o total de atendimentos realizados agrupados por mês (últimos 12 meses)."""
    conexao = conectar()
    try:
        consulta_sql = """
            SELECT
                strftime('%Y-%m', data_consulta) AS mes_ano,
                COUNT(*) AS total
            FROM consultas
            WHERE status = 'realizada'
              AND data_consulta >= date('now', '-12 months')
            GROUP BY mes_ano
            ORDER BY mes_ano
        """
        df = pd.read_sql_query(consulta_sql, conexao)
        if df.empty:
            return pd.DataFrame(columns=["Mês", "Atendimentos"])
        df.columns = ["Mês", "Atendimentos"]
        df["Mês"] = pd.to_datetime(df["Mês"]).dt.strftime("%b/%Y")
        return df
    finally:
        conexao.close()


def dados_grafico_vacinacao_por_mes() -> pd.DataFrame:
    """Retorna o total de vacinações realizadas agrupadas por mês (últimos 12 meses)."""
    conexao = conectar()
    try:
        consulta_sql = """
            SELECT
                strftime('%Y-%m', data_consulta) AS mes_ano,
                COUNT(*) AS total
            FROM consultas
            WHERE tipo_consulta = 'Vacinação'
              AND status = 'realizada'
              AND data_consulta >= date('now', '-12 months')
            GROUP BY mes_ano
            ORDER BY mes_ano
        """
        df = pd.read_sql_query(consulta_sql, conexao)
        if df.empty:
            return pd.DataFrame(columns=["Mês", "Vacinações"])
        df.columns = ["Mês", "Vacinações"]
        df["Mês"] = pd.to_datetime(df["Mês"]).dt.strftime("%b/%Y")
        return df
    finally:
        conexao.close()


# ---------------------------------------------------------------------------
# Médicos
# ---------------------------------------------------------------------------

DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

ESPECIALIDADES = [
    "Clínico Geral",
    "Cirurgião Veterinário",
    "Dermatologista Veterinário",
    "Oncologista Veterinário",
    "Cardiologista Veterinário",
    "Ortopedista Veterinário",
    "Oftalmologista Veterinário",
    "Nutricionista Veterinário",
    "Anestesiologista Veterinário",
    "Radiologista Veterinário",
    "Odontologista Veterinário",
    "Neurologista Veterinário",
    "Endocrinologista Veterinário",
    "Nefrologista Veterinário",
    "Infectologista Veterinário",
    "Médico de Animais Selvagens",
    "Médico de Animais Aquáticos",
    "Comportamentalista Animal",
    "Acupunturista Veterinário",
    "Homeopata Veterinário",
]

ESPECIES_ATENDIDAS = ["Canina", "Felina", "Ave", "Roedor", "Réptil", "Coelho", "Peixe", "Outro"]


def cadastrar_medico(nome: str, crm: str, especialidade: str, especies: list[str],
                     dias: list[str], horario_inicio: str, horario_fim: str,
                     telefone: str) -> tuple[bool, str]:
    """Cadastra um novo médico veterinário."""
    conexao = conectar()
    try:
        conexao.execute(
            """INSERT INTO medicos
               (nome, crm, especialidade, especies, dias_trabalho, horario_inicio, horario_fim, telefone)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                nome.strip(),
                crm.strip().upper(),
                especialidade,
                ",".join(especies),
                ",".join(dias),
                horario_inicio,
                horario_fim,
                telefone.strip(),
            )
        )
        conexao.commit()
        return True, "Médico cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "CRM já cadastrado no sistema."
    except sqlite3.Error as erro:
        return False, f"Erro no banco de dados: {erro}"
    finally:
        conexao.close()


def listar_medicos() -> pd.DataFrame:
    """Retorna todos os médicos cadastrados."""
    conexao = conectar()
    try:
        consulta_sql = """
            SELECT
                id,
                nome        AS Nome,
                crm         AS CRM,
                especialidade AS Especialidade,
                especies    AS "Espécies Atendidas",
                dias_trabalho AS "Dias de Trabalho",
                horario_inicio || ' às ' || horario_fim AS Horário,
                telefone    AS Telefone
            FROM medicos
            ORDER BY nome
        """
        return pd.read_sql_query(consulta_sql, conexao)
    finally:
        conexao.close()


def medicos_disponiveis(data: str, especie_pet: str, tipo_consulta: str) -> pd.DataFrame:
    """Retorna médicos disponíveis para uma data, espécie e tipo de consulta."""
    conexao = conectar()
    try:
        # Descobre o dia da semana da data escolhida em português
        dias_pt = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
        dia_semana = dias_pt[pd.Timestamp(data).dayofweek]

        todos = pd.read_sql_query(
            "SELECT id, nome, crm, especialidade, especies, dias_trabalho, horario_inicio, horario_fim FROM medicos",
            conexao
        )
        if todos.empty:
            return pd.DataFrame()

        # Filtra por dia de trabalho
        trabalha_no_dia = todos[todos["dias_trabalho"].str.contains(dia_semana, na=False)]

        # Filtra por espécie que atende
        atende_especie = trabalha_no_dia[trabalha_no_dia["especies"].str.contains(especie_pet, na=False)]

        if atende_especie.empty:
            return pd.DataFrame()

        # Monta exibição
        resultado = atende_especie[["id", "nome", "crm", "especialidade", "horario_inicio", "horario_fim"]].copy()
        resultado.columns = ["id", "Nome", "CRM", "Especialidade", "Início", "Fim"]
        return resultado
    finally:
        conexao.close()


def excluir_medico(medico_id: int) -> tuple[bool, str]:
    """Remove um médico do sistema."""
    conexao = conectar()
    try:
        cursor = conexao.execute("DELETE FROM medicos WHERE id = ?", (medico_id,))
        conexao.commit()
        if cursor.rowcount == 0:
            return False, "Médico não encontrado."
        return True, "Médico removido com sucesso."
    except sqlite3.Error as erro:
        return False, f"Erro no banco de dados: {erro}"
    finally:
        conexao.close()