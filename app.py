import streamlit as st
import re
import pandas as pd

# Função para carregar os dados do arquivo txt
def load_data(uploaded_file):
    if uploaded_file is not None:
        # Conteúdo txt
            with open("Conversa do WhatsApp com PROJETOS.txt", "r", encoding="utf-8") as f:
                linhas = f.readlines()

            # Counteúdo linhas
            dados = []

            # Regex mensagens no formato correto
            padrao = r"(\d{1,2}/\d{1,2}/\d{4}) (\d{1,2}:\d{2}) (da (manhã|tarde|noite)) - (.+?): (.+)"

            # Para mensagens que não seguem o padrão 
            padrao_midia = r"(\d{1,2}/\d{1,2}/\d{4}) (\d{1,2}:\d{2}) (da (manhã|tarde|noite)) - (.+?): (<Mídia oculta>)"

            mensagem_atual = None  

            for linha in linhas:
                # Verifica se a linha segue o padrão 
                match = re.match(padrao, linha)
                
                # Caso não siga, verificar o padrão midia
                if not match:  
                    match = re.match(padrao_midia, linha)
                
                # Se seguir algum dos padrões
                if match:  
                    # Se já houver alguma mensagem antes, adicionar à lista
                    if mensagem_atual:
                        dados.append(mensagem_atual)  

                    # Atribuindo os espaços às variáveis
                    data, hora, periodo, _, usuario, mensagem = match.groups()

                    # Removendo o 'da '
                    periodo = periodo.split("da ")[1].capitalize()

                    # Armazena a mensagem organizada
                    mensagem_atual = [data, hora, periodo, usuario, mensagem]  

                # Caso não se encaixe no padrão, deve ser uma continuação de uma mensagem
                else:
                    # Se realmente for uma continuação da última mensagem
                    if mensagem_atual:  
                        mensagem_atual[4] += f" {linha.strip()}"  # Então adiciona à 'mensagem'

            # Adicionando última mensagem
            if mensagem_atual:
                dados.append(mensagem_atual)

            # Criando Df 
            df = pd.DataFrame(dados, columns=["Data", "Hora", "Turno", "Usuário", "Mensagem"])

            return df
    return None

# Filtrar mensagens por palavras chave e data
def filter_messages(df, palavras_key, start_date, end_date):
    pattern = '(?i)' + '|'.join(palavras_key)
    matches = df['Mensagem'].str.contains(pattern, na=False)
    df_filtered = df[matches]

    df_filtered["Data"] = pd.to_datetime(df_filtered["Data"], format= '%d/%m/%Y')
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    date_filtered = df_filtered[(df_filtered["Data"] >= start_date) & (df_filtered["Data"] <= end_date)]
    date_filtered["Data"] = date_filtered["Data"].dt.date

    return date_filtered

# Título 
st.title('Filtrador de Mensagens')

# Carregamento do arquivo txt
uploaded_file = st.file_uploader("Escolha um arquivo TXT", type="txt")


# Filtrando Data
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Data de Início", value=pd.to_datetime("2025-01-01"))

with col2:
    end_date = st.date_input("Data de Término", value=pd.to_datetime("2025-12-31"))


# Palavras chave
palavras_key_input = st.text_input("Digite as palavras chave, separadas por vírgula:", "confirmado, ajustar, bronca")
palavras_key = [palavra.strip() for palavra in palavras_key_input.split(",")]


# Botão para carregar e filtrar os dados
if st.button("Carregar e Filtrar Dados"):
    df = load_data(uploaded_file)
    if df is not None:
        df_filtrado = filter_messages(df, palavras_key, start_date, end_date)
        if df_filtrado.shape[0] >= 1:
            st.write("Mensagens Filtradas:")
            st.dataframe(df_filtrado)
        else:
            st.write("Não foi encontrar qualquer mensagem!")
    else:
        st.write("Por favor, carregue um arquivo TXT.")
