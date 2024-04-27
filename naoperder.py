import streamlit as st
import re
import datetime
import pdfplumber
import pandas as pd

st.set_page_config(
    page_title="Consultas - DETRAN",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.markdown(
    "<div align='center'><img src='https://github.com/PAlab0/PAlab0/blob/main/logoPA.png?raw=true' width='85'></div>",
    unsafe_allow_html=True,
)

st.sidebar.markdown(""" """)
st.sidebar.title("""Consultas DETRAN 📝""")

def pdf_dnit(uploaded_file):
    st.title("""Resultados - DNIT 📝""")
    # Abre o PDF e obtém o número total de páginas
    with pdfplumber.open(uploaded_file) as pdf:
        total_paginas = len(pdf.pages)

        # Inicializa uma lista vazia para armazenar os dados extraídos
        todas_tabelas = []

        # Expressão regular otimizada para identificar as linhas da tabela
        padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2}\s/\s[A-Z]{2})\s([A-Z]\d{9})\s(\d{2}/\d{2}/\d{4})\s(\d{3}-\d)\s/\s(\d)"

        # Inicializa o texto para exibir o número da página processada
        texto_progresso = st.empty()

        # Inicializa a barra de progresso
        progress_bar = st.progress(0)

        # Loop para percorrer todas as páginas do relatório
        for idx, pagina in enumerate(pdf.pages, start=1):
            porc = (idx/total_paginas)*100
            # Atualiza o texto para exibir o número da página processada
            texto_progresso.text(f"Processando página {idx} de {total_paginas} - {porc:.1f}%")

            # Atualiza a barra de progresso com a porcentagem de páginas processadas
            progress_bar.progress(idx / total_paginas)

            # Procura pelas linhas da tabela usando a expressão regular
            tabelas_pagina = re.findall(padrao_linha_tabela, pagina.extract_text())

            # Acrescenta as tabelas encontradas na página atual à lista de todas as tabelas
            todas_tabelas.extend(tabelas_pagina)
    # Remove a barra de progresso ao final do processamento
    progress_bar.empty()

    # Cria o DataFrame final com todas as informações extraídas de todas as páginas
    df = pd.DataFrame(todas_tabelas, columns=["Placa/UF", "Nº do Auto de Infração", "Data da Infração", "Código da Infração", "Desdobramento"])

    # Filtra as linhas que contêm "/RS" na coluna "Placa/UF"
    df = df[df["Placa/UF"].str.contains(" / RS")]
    df = df[df["Código da Infração"] == "747-1"]
    df = df[df["Desdobramento"] == "0"]

    # Remove as colunas indesejadas do DataFrame
    df.drop(columns=["Nº do Auto de Infração", "Data da Infração", "Código da Infração", "Desdobramento"], inplace=True)

    # Remove o UF da coluna "Placa/UF"
    df["Placa/UF"] = df["Placa/UF"].str.split("/", n=1).str[0]

    # Salva o DataFrame como um arquivo Excel
    df.to_excel('DNIT_RS.xlsx', index=False)

    # Lê o conteúdo do arquivo Excel como bytes
    with open('DNIT_RS.xlsx', 'rb') as f:
        excel_bytes = f.read()

    # Exibe uma mensagem de sucesso
    st.success('Processamento concluído!', icon="✅")

    # Exibe um botão para baixar o arquivo Excel
    if st.download_button(
        label="Clique aqui para baixar o arquivo em Excel",
        data=excel_bytes,
        file_name='DNIT_RS.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ):
        st.success('Dataframe salvo como DNIT_RS.xlsx!', icon="✅")

    # Exibe o DataFrame
    st.dataframe(df, hide_index=True, use_container_width=st.session_state.get("use_container_width", True))

def pdf_detran_MS_processos(uploaded_file):
    st.title("""Resultados - DETRAN - MS Processos📝""")
    # Abre o PDF e obtém o número total de páginas
    with pdfplumber.open(uploaded_file) as pdf:
        total_paginas = len(pdf.pages)

        # Inicializa uma lista vazia para armazenar os dados extraídos
        todas_tabelas = []

        # Expressão regular otimizada para identificar as linhas da tabela
        padrao_linha_tabela = r"Condutor:\s+(.*?)\n"

        # Inicializa o texto para exibir o número da página processada
        texto_progresso = st.empty()

        # Inicializa a barra de progresso
        progress_bar = st.progress(0)

        # Loop para percorrer todas as páginas do relatório
        for idx, pagina in enumerate(pdf.pages, start=1):
            porc = (idx/total_paginas)*100
            # Atualiza o texto para exibir o número da página processada
            texto_progresso.text(f"Processando página {idx} de {total_paginas} - {porc:.1f}%")

            # Atualiza a barra de progresso com a porcentagem de páginas processadas
            progress_bar.progress(idx / total_paginas)

            # Procura pelas linhas da tabela usando a expressão regular
            tabelas_pagina = re.findall(padrao_linha_tabela, pagina.extract_text())

            # Acrescenta as tabelas encontradas na página atual à lista de todas as tabelas
            todas_tabelas.extend(tabelas_pagina)
    # Remove a barra de progresso ao final do processamento
    progress_bar.empty()

    # Cria o DataFrame final com todas as informações extraídas de todas as páginas
    df = pd.DataFrame(todas_tabelas, columns=["Condutor"])

    # Salva o DataFrame como um arquivo Excel
    df.to_excel('DETRAN - MS.xlsx', index=False)

    # Lê o conteúdo do arquivo Excel como bytes
    with open('DETRAN - MS.xlsx', 'rb') as f:
        excel_bytes = f.read()

    # Exibe uma mensagem de sucesso
    st.success('Processamento concluído!', icon="✅")

    # Exibe um botão para baixar o arquivo Excel
    if st.download_button(
        label="Clique aqui para baixar o arquivo em Excel",
        data=excel_bytes,
        file_name='DETRAN - MS.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ):
        st.success('Dataframe salvo como DETRAN - MS.xlsx!', icon="✅")

    # Exibe o DataFrame
    st.dataframe(df, hide_index=True, use_container_width=st.session_state.get("use_container_width", True))
    
servicos = ["Leitura de PDF", "Consulta de placas - GOV"] # Lista de serviços disponíveis
consulta = ["Manual", "Automatizada"] # Lista de tipos de consulta
tipos_pdf = ["DETRAN - ES","DETRAN - MS", "DETRAN - RS","DETRAN - SC","DNIT - RS","PRF - Outros Estados", "PRF - RS","Nomes Faltantes"] # Lista de tipos de PDF

# Obtendo a entrada do usuário para selecionar o serviço
servico_sel = st.sidebar.selectbox("Serviço", servicos)

if servico_sel == "Leitura de PDF":
    # Obtendo o tipo de PDF para leitura
    tipo_pdf_sel = st.sidebar.selectbox("Tipo de PDF", tipos_pdf)

    if tipo_pdf_sel == "DETRAN - ES":
        opcoes_dES= ["Processos"]
        opcao_dES_sel = st.sidebar.selectbox("Selecione uma opção DETRAN - ES", opcoes_dES)
    elif tipo_pdf_sel == "DETRAN - MS":
        opcoes_dMS= ["Placas","Processos","Defesa (sem 218)","Recurso (sem 246)"]
        opcao_dMS_sel = st.sidebar.selectbox("Selecione uma opção DETRAN - MS", opcoes_dMS)
    elif tipo_pdf_sel == "DETRAN - RS":
        opcoes_dRS= ["Placas"]
        opcao_dRS_sel = st.sidebar.selectbox("Selecione uma opção DETRAN - RS", opcoes_dRS)
    elif tipo_pdf_sel == "DETRAN - SC":
        opcoes_dSC= ["Placas"]
        opcao_dSC_sel = st.sidebar.selectbox("Selecione uma opção DETRAN - SC", opcoes_dSC)        
    elif tipo_pdf_sel == "DNIT - RS":
        opcoes_dnit = ["DNIT - RS"]
        opcao_dnit_sel = st.sidebar.selectbox("Selecione uma opção DNIT - RS", opcoes_dnit)
    elif tipo_pdf_sel == "PRF - Outros estados":
        opcoes_prf = ["Autuação - Bafômetro", "Autuação - Completo", "Autuação - Recusa"]
        opcao_prf_sel = st.sidebar.selectbox("Selecione uma opção PRF", opcoes_prf)
    elif tipo_pdf_sel == "PRF - RS":
        opcoes_prf = ["Penalidade", "Autuação"]
        opcao_prf_sel = st.sidebar.selectbox("Selecione uma opção PRF", opcoes_prf)
    elif tipo_pdf_sel == "Nomes Faltantes":
        opcoes_nomes = ["Nomes Faltantes"]
        opcao_nomes_sel = st.sidebar.selectbox("Selecione uma opção Nomes Faltantes", opcoes_nomes)

    # Lógica para selecionar o arquivo para leitura de PDF
    st.sidebar.title("Upload de arquivo 🗂️")
    uploaded_file = st.sidebar.file_uploader(f"Escolha o seu PDF - {tipo_pdf_sel}", accept_multiple_files=False, type=('pdf'), help=("Coloque um arquivo .pdf"))
    if tipo_pdf_sel == "DNIT - RS":
        opcoes_dnit = ["DNIT - RS"]
        if st.sidebar.button('Processar PDF',type="primary"):
            pdf_dnit(uploaded_file)
        else:
            ""

elif servico_sel == "Consulta de placas - GOV":
    # Obtendo a entrada do usuário para selecionar o tipo de consulta
    consulta_sel = st.sidebar.selectbox("Consulta", consulta)
    
    # Lógica para criar os inputs de acordo com a escolha do usuário
    if consulta_sel == "Manual":
        st.title("Digite os detalhes para Consulta de placas - GOV:")
        input1 = st.text_input("Input 1 para Consulta de placas - GOV:")
        input2 = st.text_input("Input 2 para Consulta de placas - GOV:")
        input3 = st.text_input("Input 3 para Consulta de placas - GOV:")
        input4 = st.text_input("Input 4 para Consulta de placas - GOV:")
    elif consulta_sel == "Automatizada":
        st.sidebar.title("""Upload de arquivo 🗂️""")
        uploaded_files = st.sidebar.file_uploader("Escolha o seu arquivo Excel", accept_multiple_files=True, type=('xlsx', 'xls'), help=("Coloque um arquivo .xlsx ou .xls"))
else:
    uploaded_files = None