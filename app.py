import streamlit as st
import pandas as pd
from main import conectar, cadastrar_tutor, cadastrar_pet, listar_clientes_e_pets
from validacoes import validar_nome, validar_peso, validar_cpf

st.set_page_config(page_title="Gnuvet Sistema", page_icon="🐾")

menu = st.sidebar.selectbox("Menu", ["🏠 Início", "📝 Cadastrar Dono", "🐶 Cadastrar Pet", "📊 Painel e Consultas"])

if menu == "🏠 Início":
    st.title("🏥 Bem-vindo ao Sistema Gnuvet")
    st.write("Selecione uma opção no menu lateral para começar.")

elif menu == "📝 Cadastrar Dono":
    st.subheader("Cadastro de Novo Tutor")
    nome = st.text_input("Nome Completo")
    cpf = st.text_input("CPF")
    tel = st.text_input("Telefone")
    
    if st.button("Salvar Tutor"):
        v_nome, msg_n = validar_nome(nome)
        v_cpf, msg_c = validar_cpf(cpf)
        if v_nome and v_cpf:
            if cadastrar_tutor(nome, cpf, tel): st.success("Tutor cadastrado!")
            else: st.error("Erro ao salvar (CPF já existe?)")
        else: st.error(msg_n or msg_c)

elif menu == "🐶 Cadastrar Pet":
    st.subheader("Cadastro de Pet")
    conn = conectar()
    tutores = pd.read_sql_query("SELECT id, nome FROM tutores", conn)
    conn.close()
    
    if not tutores.empty:
        tutor_selecionado = st.selectbox("Selecione o Dono", tutores['nome'])
        tutor_id = tutores[tutores['nome'] == tutor_selecionado]['id'].values[0]
        
        nome_p = st.text_input("Nome do Pet")
        peso_p = st.number_input("Peso (kg)", min_value=0.0, max_value=200.0)
        
        if st.button("Salvar Pet"):
            v_peso, msg_p = validar_peso(peso_p)
            if v_peso:
                if cadastrar_pet(nome_p, "Canina", "SRD", int(tutor_id), peso_p): st.success("Pet cadastrado!")
            else: st.error(msg_p)
    else:
        st.warning("Cadastre um tutor primeiro!")

elif menu == "📊 Painel e Consultas":
    st.subheader("Visualização Geral")
    df = listar_clientes_e_pets()
    st.dataframe(df)