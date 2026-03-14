import streamlit as st
import pandas as pd
import hashlib
from datetime import date, time
from main import (
    conectar, cadastrar_tutor, cadastrar_pet,
    listar_clientes_e_pets, listar_pets_por_tutor,
    agendar_consulta, listar_consultas_agendadas,
    listar_historico_consultas, atualizar_consulta,
    dados_grafico_consultas_por_mes, dados_grafico_vacinacao_por_mes,
    vacinacoes_hoje,
    cadastrar_medico, listar_medicos, medicos_disponiveis, excluir_medico,
    ESPECIALIDADES, ESPECIES_ATENDIDAS, DIAS_SEMANA,
)
from validacoes import validar_nome, validar_nome_pet, validar_peso, validar_cpf, validar_telefone

# ---------------------------------------------------------------------------
# Dados de domínio
# ---------------------------------------------------------------------------

ESPECIES_RACAS: dict[str, list[str]] = {
    "Canina": [
        "SRD (Sem Raça Definida)", "Labrador Retriever", "Golden Retriever",
        "Bulldog Francês", "Pastor Alemão", "Poodle", "Shih Tzu", "Yorkshire Terrier",
        "Beagle", "Rottweiler", "Dachshund", "Boxer", "Husky Siberiano",
        "Border Collie", "Maltês", "Pinscher", "Lhasa Apso", "Chow Chow",
        "Akita", "Dálmata",
    ],
    "Felina": [
        "SRD (Sem Raça Definida)", "Persa", "Siamês", "Maine Coon",
        "Ragdoll", "Bengal", "Abissínio", "Sphynx", "Angorá",
        "Scottish Fold", "Birmanês", "Russo Azul",
    ],
    "Ave":    ["Calopsita", "Periquito Australiano", "Agapornis", "Papagaio", "Canário", "Cacatua", "Arara", "Manon"],
    "Roedor": ["Hamster", "Cobaia (porquinho-da-índia)", "Gerbil", "Chinchila", "Rato Doméstico"],
    "Réptil": ["Iguana", "Gecko Leopardo", "Tartaruga", "Jabuti", "Cágado", "Dragão Barbudo"],
    "Coelho": ["SRD (Sem Raça Definida)", "Angorá", "Holland Lop", "Mini Rex"],
    "Peixe":  ["Betta", "Kinguio", "Koi", "Acará Disco", "Neon Tetra"],
    "Outro":  ["Outro"],
}

STATUS_CORES = {"agendada": "🟡", "realizada": "🟢", "cancelada": "🔴"}
EMOJI_TIPO   = {"Vacinação": "💉", "Consulta Geral": "🩺", "Retorno": "🔄",
                "Exame": "🔬", "Emergência": "⚠️", "Cirurgia": "🏥"}

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Cuidar & Afeto", page_icon="🐾", layout="wide")

# ---------------------------------------------------------------------------
# Funções de autenticação
# ---------------------------------------------------------------------------

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def autenticar(login: str, senha: str):
    """Retorna dict do usuário se credenciais corretas, senão None."""
    conexao = conectar()
    try:
        row = conexao.execute(
            "SELECT id, login, perfil, nome, medico_id FROM usuarios WHERE login = ? AND senha = ?",
            (login.strip().lower(), hash_senha(senha))
        ).fetchone()
        if row:
            return {"id": row[0], "login": row[1], "perfil": row[2], "nome": row[3], "medico_id": row[4]}
        return None
    finally:
        conexao.close()


# ---------------------------------------------------------------------------
# Controle de tentativas de login
# ---------------------------------------------------------------------------

import time as _time

MAX_TENTATIVAS  = 5
TEMPO_BLOQUEIO  = 300  # 5 minutos em segundos

if "tentativas_login"   not in st.session_state:
    st.session_state.tentativas_login   = 0
if "bloqueado_ate"      not in st.session_state:
    st.session_state.bloqueado_ate      = None

# ---------------------------------------------------------------------------
# Tema
# ---------------------------------------------------------------------------

if "tema" not in st.session_state:
    st.session_state.tema = "🌙 Escuro"

tema = st.session_state.tema

if tema == "🌙 Escuro":
    st.markdown("""<style>
        .stApp{background-color:#0e1117;color:#fafafa}
        section[data-testid="stSidebar"]{background-color:#161b22}
        div[data-testid="metric-container"]{background-color:#1c2333;border:1px solid #30363d;border-radius:10px;padding:12px}
        .stTextInput input,.stNumberInput input,.stTextArea textarea{background-color:#161b22!important;color:#fafafa!important;border-color:#30363d!important}
        .stButton>button{background-color:#238636;color:white;border:none;border-radius:6px}
        .stButton>button:hover{background-color:#2ea043}
        .stTabs [data-baseweb="tab"]{background-color:#161b22;color:#8b949e}
        .stTabs [aria-selected="true"]{color:#fafafa!important;border-bottom:2px solid #58a6ff}
        hr{border-color:#30363d}
        .login-box{background-color:#161b22;border:1px solid #30363d;border-radius:12px;padding:2rem}
    </style>""", unsafe_allow_html=True)
else:
    st.markdown("""<style>
        .stApp{background-color:#ffffff;color:#1f2328}
        section[data-testid="stSidebar"]{background-color:#f6f8fa}
        div[data-testid="metric-container"]{background-color:#f6f8fa;border:1px solid #d0d7de;border-radius:10px;padding:12px}
        .stButton>button{background-color:#0969da;color:white;border:none;border-radius:6px}
        .stButton>button:hover{background-color:#0550ae}
        .login-box{background-color:#f6f8fa;border:1px solid #d0d7de;border-radius:12px;padding:2rem}
    </style>""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TELA DE LOGIN
# ---------------------------------------------------------------------------

if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.image("logo_gnuvet.png", use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Acesso ao Sistema")

        # Verifica se está bloqueado
        agora = _time.time()
        bloqueado = (
            st.session_state.bloqueado_ate is not None and
            agora < st.session_state.bloqueado_ate
        )

        if bloqueado:
            segundos_restantes = int(st.session_state.bloqueado_ate - agora)
            minutos = segundos_restantes // 60
            segundos = segundos_restantes % 60
            st.error(f"🔒 Acesso bloqueado por excesso de tentativas.")
            st.warning(f"⏳ Tente novamente em **{minutos}m {segundos:02d}s**.")
            st.info("Recarregue a página após o tempo de bloqueio.")
        else:
            # Reseta bloqueio se já passou o tempo
            if st.session_state.bloqueado_ate is not None and agora >= st.session_state.bloqueado_ate:
                st.session_state.tentativas_login = 0
                st.session_state.bloqueado_ate    = None

            tentativas_restantes = MAX_TENTATIVAS - st.session_state.tentativas_login
            if st.session_state.tentativas_login > 0:
                st.warning(f"⚠️ Tentativas restantes: **{tentativas_restantes}**")

            with st.form("form_login"):
                login_input = st.text_input("Login", placeholder="Ex: anderson")
                senha_input = st.text_input("Senha", type="password", placeholder="Sua senha")
                entrar      = st.form_submit_button("🔐 Entrar", use_container_width=True)

            if entrar:
                usuario = autenticar(login_input, senha_input)
                if usuario:
                    st.session_state.usuario          = usuario
                    st.session_state.tentativas_login = 0
                    st.session_state.bloqueado_ate    = None
                    st.rerun()
                else:
                    st.session_state.tentativas_login += 1
                    restantes = MAX_TENTATIVAS - st.session_state.tentativas_login

                    if st.session_state.tentativas_login >= MAX_TENTATIVAS:
                        st.session_state.bloqueado_ate = _time.time() + TEMPO_BLOQUEIO
                        st.error("🔒 Muitas tentativas incorretas. Acesso bloqueado por **5 minutos**.")
                    else:
                        st.error(f"❌ Login ou senha incorretos. Tentativas restantes: **{restantes}**")
    st.stop()

# ---------------------------------------------------------------------------
# USUÁRIO LOGADO — variáveis de sessão
# ---------------------------------------------------------------------------

usuario  = st.session_state.usuario
perfil   = usuario["perfil"]       # 'medico', 'atendente' ou 'admin'
eh_medico    = perfil == "medico"
eh_atendente = perfil in ("atendente", "admin")
eh_admin     = perfil == "admin"

# ---------------------------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------------------------

st.sidebar.image("logo_gnuvet.png", use_container_width=True)
st.sidebar.divider()
st.sidebar.markdown(f"👤 **{usuario['nome']}**")
st.sidebar.caption(f"Perfil: {'Médico' if eh_medico else 'Administrador' if eh_admin else 'Atendente'}")
st.sidebar.divider()

# Médico não pode editar — menu reduzido
if eh_medico:
    opcoes_menu = ["🏠 Início", "📅 Consultas", "👨‍⚕️ Médicos", "📊 Painel Geral"]
else:
    opcoes_menu = ["🏠 Início", "📝 Cadastrar Tutor", "🐶 Cadastrar Pet",
                   "👨‍⚕️ Médicos", "📅 Consultas", "📊 Painel Geral", "⚙️ Configurações"]

menu = st.sidebar.selectbox("Menu", opcoes_menu)

if st.sidebar.button("🚪 Sair"):
    st.session_state.usuario = None
    st.rerun()

# ---------------------------------------------------------------------------
# INÍCIO
# ---------------------------------------------------------------------------

if menu == "🏠 Início":
    st.title("🏥 Sistema Cuidar & Afeto")
    st.divider()

    conexao = conectar()
    total_tutores    = pd.read_sql_query("SELECT COUNT(*) as n FROM tutores", conexao).iloc[0]["n"]
    total_pets       = pd.read_sql_query("SELECT COUNT(*) as n FROM pets", conexao).iloc[0]["n"]
    total_agendadas  = pd.read_sql_query("SELECT COUNT(*) as n FROM consultas WHERE status='agendada'", conexao).iloc[0]["n"]
    total_realizadas = pd.read_sql_query("SELECT COUNT(*) as n FROM consultas WHERE status='realizada'", conexao).iloc[0]["n"]
    conexao.close()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👤 Tutores Cadastrados",  total_tutores)
    col2.metric("🐾 Pets Cadastrados",     total_pets)
    col3.metric("📅 Consultas Agendadas",  total_agendadas)
    col4.metric("✅ Consultas Realizadas", total_realizadas)
    st.divider()

    col_grafico, col_hoje = st.columns([2, 1])
    with col_grafico:
        st.markdown("#### 📈 Cadastros na Clínica")
        df_cad = pd.DataFrame({"Categoria": ["Tutores", "Pets"], "Total": [total_tutores, total_pets]})
        st.bar_chart(df_cad.set_index("Categoria"), use_container_width=True)

    with col_hoje:
        st.markdown("#### 🗓️ Consultas de Hoje")
        df_hoje  = vacinacoes_hoje()
        hoje_fmt = date.today().strftime("%d/%m/%Y")
        if df_hoje.empty:
            st.info("Nenhuma consulta agendada para hoje.")
        else:
            for _, linha in df_hoje.iterrows():
                emoji = EMOJI_TIPO.get(linha["Tipo"], "🏥")
                st.markdown(f"{emoji} **{linha['Tutor']}** · {hoje_fmt} · ⏰ {linha['Horário']} · {linha['Motivo']} · *{linha['Tipo']}*")
                st.divider()

# ---------------------------------------------------------------------------
# CADASTRAR TUTOR — só atendente
# ---------------------------------------------------------------------------

elif menu == "📝 Cadastrar Tutor":
    st.subheader("Cadastro de Novo Tutor")
    with st.form("form_tutor", clear_on_submit=True):
        nome = st.text_input("Nome Completo *", placeholder="Ex: João da Silva")
        cpf  = st.text_input("CPF *", placeholder="000.000.000-00")
        tel  = st.text_input("Telefone", placeholder="(11) 99999-9999")
        submitted = st.form_submit_button("💾 Salvar Tutor")
    if submitted:
        erros = []
        ok_nome, msg_nome = validar_nome(nome)
        ok_cpf,  msg_cpf  = validar_cpf(cpf)
        ok_tel,  msg_tel  = validar_telefone(tel)
        if not ok_nome: erros.append(f"• {msg_nome}")
        if not ok_cpf:  erros.append(f"• {msg_cpf}")
        if not ok_tel:  erros.append(f"• {msg_tel}")
        if erros:
            st.error("Corrija os erros abaixo:\n\n" + "\n".join(erros))
        else:
            ok, msg = cadastrar_tutor(nome, cpf, tel)
            st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

# ---------------------------------------------------------------------------
# CADASTRAR PET — só atendente
# ---------------------------------------------------------------------------

elif menu == "🐶 Cadastrar Pet":
    st.subheader("Cadastro de Pet")
    conexao = conectar()
    tutores = pd.read_sql_query("SELECT id, nome FROM tutores ORDER BY nome", conexao)
    conexao.close()
    if tutores.empty:
        st.warning("⚠️ Cadastre um tutor primeiro!")
    else:
        tutor_nome = st.selectbox("Selecione o Tutor *", tutores["nome"])
        tutor_id   = int(tutores[tutores["nome"] == tutor_nome]["id"].values[0])
        nome_p     = st.text_input("Nome Completo do Pet *", placeholder="Ex: Rex Silva")
        especie    = st.selectbox("Espécie *", list(ESPECIES_RACAS.keys()))
        raca       = st.selectbox("Raça *", ESPECIES_RACAS[especie])
        peso_p     = st.number_input("Peso (kg) *", min_value=0.0, max_value=200.0, step=0.1, format="%.2f")
        if st.button("💾 Salvar Pet"):
            erros = []
            ok_nome, msg_nome = validar_nome_pet(nome_p)
            ok_peso, msg_peso = validar_peso(peso_p)
            if not ok_nome: erros.append(f"• {msg_nome}")
            if not ok_peso: erros.append(f"• {msg_peso}")
            if erros:
                st.error("Corrija os erros abaixo:\n\n" + "\n".join(erros))
            else:
                ok, msg = cadastrar_pet(nome_p, especie, raca, tutor_id, peso_p)
                st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

# ---------------------------------------------------------------------------
# MÉDICOS
# ---------------------------------------------------------------------------

elif menu == "👨‍⚕️ Médicos":
    st.subheader("👨‍⚕️ Gerenciamento de Médicos Veterinários")

    if eh_medico:
        # Médico só visualiza
        st.info("🔒 Você tem acesso somente para visualização.")
        df_med = listar_medicos()
        if df_med.empty:
            st.info("Nenhum médico cadastrado.")
        else:
            st.dataframe(df_med.drop(columns=["id"]), use_container_width=True)
    else:
        # Atendente pode tudo
        aba = st.tabs(["📋 Lista de Médicos", "➕ Cadastrar Médico", "🗑️ Remover Médico"])

        with aba[0]:
            df_med = listar_medicos()
            if df_med.empty:
                st.info("Nenhum médico cadastrado ainda.")
            else:
                st.dataframe(df_med.drop(columns=["id"]), use_container_width=True)

        with aba[1]:
            with st.form("form_medico", clear_on_submit=True):
                col1, col2 = st.columns(2)
                nome_med  = col1.text_input("Nome Completo *", placeholder="Dr. Carlos Souza")
                crm_med   = col2.text_input("CRM *", placeholder="Ex: 12345-SP")
                tel_med   = col1.text_input("Telefone", placeholder="(11) 99999-9999")
                espec_med = col2.selectbox("Especialidade *", ESPECIALIDADES)
                st.markdown("**Espécies que atende *:**")
                cols_esp = st.columns(len(ESPECIES_ATENDIDAS))
                especies_sel = [esp for i, esp in enumerate(ESPECIES_ATENDIDAS) if cols_esp[i].checkbox(esp, key=f"esp_{esp}")]
                st.markdown("**Dias de trabalho *:**")
                cols_dias = st.columns(len(DIAS_SEMANA))
                dias_sel = [dia for i, dia in enumerate(DIAS_SEMANA) if cols_dias[i].checkbox(dia, key=f"dia_{dia}")]
                col3, col4 = st.columns(2)
                h_inicio = col3.time_input("Horário de entrada *", value=time(8, 0))
                h_fim    = col4.time_input("Horário de saída *",   value=time(18, 0))
                submitted = st.form_submit_button("💾 Salvar Médico")
            if submitted:
                erros = []
                ok_nome, msg_nome = validar_nome(nome_med)
                ok_tel,  msg_tel  = validar_telefone(tel_med)
                if not ok_nome:         erros.append(f"• {msg_nome}")
                if not ok_tel:          erros.append(f"• {msg_tel}")
                if not crm_med.strip(): erros.append("• O CRM não pode estar vazio.")
                if not especies_sel:    erros.append("• Selecione ao menos uma espécie.")
                if not dias_sel:        erros.append("• Selecione ao menos um dia de trabalho.")
                if h_inicio >= h_fim:   erros.append("• O horário de entrada deve ser antes do horário de saída.")
                if erros:
                    st.error("Corrija os erros abaixo:\n\n" + "\n".join(erros))
                else:
                    ok, msg = cadastrar_medico(nome_med, crm_med, espec_med, especies_sel, dias_sel,
                                               h_inicio.strftime("%H:%M"), h_fim.strftime("%H:%M"), tel_med)
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

        with aba[2]:
            df_med = listar_medicos()
            if df_med.empty:
                st.info("Nenhum médico cadastrado.")
            else:
                opcoes = {f"{row['Nome']} — CRM {row['CRM']}": row["id"] for _, row in df_med.iterrows()}
                selecionado = st.selectbox("Selecione o médico", list(opcoes.keys()))
                if st.button("🗑️ Remover Médico", type="primary"):
                    ok, msg = excluir_medico(opcoes[selecionado])
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

# ---------------------------------------------------------------------------
# CONSULTAS
# ---------------------------------------------------------------------------

elif menu == "📅 Consultas":
    abas_consulta = ["📋 Agendadas", "📜 Histórico"]
    if eh_atendente:
        abas_consulta = ["📋 Agendadas", "➕ Agendar Nova", "📜 Histórico", "✏️ Editar / Cancelar"]

    aba = st.tabs(abas_consulta)

    # ── Agendadas ──────────────────────────────────────────────────────────
    with aba[0]:
        st.subheader("Consultas Agendadas")
        df_ag = listar_consultas_agendadas()
        # Médico vê apenas suas próprias consultas
        if eh_medico and usuario["medico_id"]:
            df_ag = df_ag  # já filtrado abaixo via query — aqui mantém visão geral
        if df_ag.empty:
            st.info("Nenhuma consulta agendada no momento.")
        else:
            st.dataframe(df_ag, use_container_width=True)

    # ── Histórico ──────────────────────────────────────────────────────────
    with aba[1] if eh_medico else aba[2]:
        st.subheader("Histórico de Consultas")
        df_hist = listar_historico_consultas()
        if df_hist.empty:
            st.info("Nenhuma consulta registrada ainda.")
        else:
            status_filtro = st.multiselect("Filtrar por status", ["agendada", "realizada", "cancelada"],
                                           default=["agendada", "realizada", "cancelada"])
            df_f = df_hist[df_hist["Status"].isin(status_filtro)].copy()
            df_f["Status"] = df_f["Status"].apply(lambda s: f"{STATUS_CORES.get(s,'')} {s.capitalize()}")
            st.dataframe(df_f, use_container_width=True)

    # ── Agendar Nova — só atendente ────────────────────────────────────────
    if eh_atendente:
        with aba[1]:
            st.subheader("Agendar Nova Consulta")
            conexao = conectar()
            tutores = pd.read_sql_query("SELECT id, nome FROM tutores ORDER BY nome", conexao)
            conexao.close()
            if tutores.empty:
                st.warning("⚠️ Cadastre um tutor primeiro!")
            else:
                tutor_nome  = st.selectbox("Tutor *", tutores["nome"], key="ag_tutor")
                tutor_id    = int(tutores[tutores["nome"] == tutor_nome]["id"].values[0])
                pets_tutor  = listar_pets_por_tutor(tutor_id)
                if pets_tutor.empty:
                    st.warning("Este tutor não possui pets cadastrados.")
                else:
                    pet_nome    = st.selectbox("Pet *", pets_tutor["nome"], key="ag_pet")
                    pet_id      = int(pets_tutor[pets_tutor["nome"] == pet_nome]["id"].values[0])
                    especie_pet = pets_tutor[pets_tutor["nome"] == pet_nome]["especie"].values[0]
                    tipo_consulta = st.selectbox("Tipo de Consulta *",
                        ["Consulta Geral","Vacinação","Retorno","Cirurgia","Exame","Emergência","Outro"], key="ag_tipo")
                    col1, col2 = st.columns(2)
                    data_c  = col1.date_input("Data *", min_value=date.today(), key="ag_data")
                    horario = col2.time_input("Horário *", value=time(8, 0), step=1800, key="ag_hora")
                    st.markdown("---")
                    st.markdown("**👨‍⚕️ Médico Responsável**")
                    df_disp = medicos_disponiveis(str(data_c), especie_pet, tipo_consulta)
                    if df_disp.empty:
                        st.warning("⚠️ Nenhum médico disponível para esta data e espécie.")
                        medico_id = None
                    else:
                        opcoes_med = {"— Sem médico —": None}
                        for _, m in df_disp.iterrows():
                            opcoes_med[f"{m['Nome']} ({m['Especialidade']}) · {m['Início']} às {m['Fim']}"] = int(m["id"])
                        med_sel   = st.selectbox("Selecione o médico", list(opcoes_med.keys()), key="ag_med")
                        medico_id = opcoes_med[med_sel]
                    motivo = st.text_area("Motivo da Consulta *", placeholder="Ex: Vacinação anual...", key="ag_motivo")
                    if st.button("📅 Agendar Consulta"):
                        if not motivo.strip():
                            st.error("❌ Informe o motivo da consulta.")
                        else:
                            ok, msg = agendar_consulta(pet_id, str(data_c), horario.strftime("%H:%M"),
                                                       motivo.strip(), tipo_consulta, medico_id)
                            st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

        # ── Editar / Cancelar — só atendente ──────────────────────────────
        with aba[3]:
            st.subheader("Editar ou Cancelar Consulta")
            df_edit = listar_consultas_agendadas()
            if df_edit.empty:
                st.info("Nenhuma consulta agendada para editar.")
            else:
                opcoes = {f"#{row['id']} | {row['Pet']} ({row['Tutor']}) — {row['Data']} {row['Horário']}": row['id']
                          for _, row in df_edit.iterrows()}
                selecionada = st.selectbox("Selecione a consulta", list(opcoes.keys()))
                with st.form("form_editar"):
                    novo_status = st.selectbox("Novo Status", ["agendada", "realizada", "cancelada"])
                    observacoes = st.text_area("Observações (opcional)")
                    submitted   = st.form_submit_button("💾 Salvar Alteração")
                if submitted:
                    ok, msg = atualizar_consulta(opcoes[selecionada], novo_status, observacoes)
                    st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")

# ---------------------------------------------------------------------------
# PAINEL GERAL
# ---------------------------------------------------------------------------

elif menu == "📊 Painel Geral":
    st.subheader("📊 Painel Geral — Tutores e Pets")
    col_esq, col_dir = st.columns(2)
    with col_esq:
        st.markdown("#### 💉 Vacinações por Mês (últimos 12 meses)")
        df_vac = dados_grafico_vacinacao_por_mes()
        if df_vac.empty:
            st.info("ℹ️ Nenhuma vacinação com status 'realizada' ainda.")
        else:
            st.line_chart(df_vac.set_index("Mês"), y="Vacinações", use_container_width=True)
    with col_dir:
        st.markdown("#### 🐾 Atendimentos por Mês (últimos 12 meses)")
        df_cons = dados_grafico_consultas_por_mes()
        if df_cons.empty:
            st.info("ℹ️ Nenhuma consulta com status 'realizada' ainda.")
        else:
            st.line_chart(df_cons.set_index("Mês"), y="Atendimentos", use_container_width=True)
    st.divider()
    st.markdown("#### 📋 Lista Completa de Tutores e Pets")
    df = listar_clientes_e_pets()
    if df.empty:
        st.info("Nenhum dado cadastrado ainda.")
    else:
        st.dataframe(df, use_container_width=True)
        st.download_button("⬇️ Exportar CSV", data=df.to_csv(index=False).encode("utf-8"),
                           file_name="gnuvet_clientes_pets.csv", mime="text/csv")

# ---------------------------------------------------------------------------
# CONFIGURAÇÕES — só atendente
# ---------------------------------------------------------------------------

elif menu == "⚙️ Configurações":
    st.subheader("⚙️ Configurações do Sistema")
    st.divider()
    st.markdown("#### 🎨 Tema da Interface")
    col_t, _ = st.columns([1, 2])
    with col_t:
        novo_tema = st.radio("Selecione o tema", ["🌙 Escuro", "☀️ Claro"],
                             index=0 if st.session_state.tema == "🌙 Escuro" else 1)
        if st.button("✅ Aplicar Tema"):
            st.session_state.tema = novo_tema
            st.success(f"Tema alterado para **{novo_tema}**!")
            st.rerun()