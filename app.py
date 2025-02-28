import streamlit as st
import re
import pandas as pd
import pdfplumber
import requests
import time
import requests

servicos = ["Leitura de PDF", "Consulta de placas - GOV"] # Lista de serviços disponíveis

st.set_page_config(
    page_title="PA - Consultas",
    page_icon="https://raw.githubusercontent.com/PAlab0/Consultas/main/Documentos/logo_v.png",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.sidebar.markdown(
    "<div align='center'><img src='https://github.com/PAlab0/PAlab0/blob/main/logoPA.png?raw=true' width='85'></div>",
    unsafe_allow_html=True,
) 
st.sidebar.markdown(""" """)
st.sidebar.title("""Consultas DETRAN 📝""")

# Defs Gerais
def loop (uploaded_file,padrao):
    st.title(f"""Resultados - {tipo_pdf_sel} 📝""")
    # Abre o PDF e obtém o número total de páginas
    with pdfplumber.open(uploaded_file) as pdf:
        total_paginas = len(pdf.pages)

        # Inicializa  listas vazias para armazenar os dados extraídos
        todas_tabelas = []
        todas_tabelas1 = []
        todas_tabelas2 = []
        todas_tabelas3 = []
        
        # Inicializa o texto para exibir o número da página processada
        texto_progresso = st.empty()

        # Inicializa a barra de progresso
        progress_bar = st.progress(0)

        # Loop para percorrer todas as páginas do relatório
        for idx, pagina in enumerate(pdf.pages, start=1):
            porc = (idx/total_paginas)*100
            # Atualiza o texto e a barra de progresso para exibir o número e porcentagem das páginas processadas
            texto_progresso.text(f"Processando página {idx} de {total_paginas} - {porc:.1f}%")
            progress_bar.progress(idx / total_paginas)

            # Procura pelas linhas da tabela usando a expressão regular
            tabelas_pagina = re.findall(padrao, pagina.extract_text())

            # Acrescenta as tabelas encontradas na página atual à lista de todas as tabelas
            todas_tabelas.extend(tabelas_pagina)
    # Remove a barra de progresso ao final do processamento
    progress_bar.empty()

    return todas_tabelas
def download(df):
    # Salva o DataFrame como um arquivo Excel
    df.to_excel('{tipo_pdf_sel}.xlsx', index=False)
    # Lê o conteúdo do arquivo Excel como bytes
    with open('{tipo_pdf_sel}.xlsx', 'rb') as f:
        excel_bytes = f.read()
    # Exibe uma mensagem de sucesso
    st.success('Processamento concluído!', icon="✅")
    # Resetar index
    df = df.reset_index()
    # Exibe o DataFrame
    st.dataframe(df, use_container_width=st.session_state.get("use_container_width", True))
    # Exibe um botão para baixar o arquivo Excel
    if st.download_button(
        label="Clique aqui para baixar o arquivo em Excel",
        data=excel_bytes,
        file_name= (f'{tipo_pdf_sel}.xlsx'),
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ):
        st.success(f'Dataframe salvo como {tipo_pdf_sel}.xlsx', icon="✅")
    else: ""
def dow_pdf(file):
    btn = st.download_button(
                    label="Download Modelo",
                    data=file,
                    file_name="Modelo.pdf",
                    mime="image/pdf"
                )
    
# DNIT
def dnit_rs(uploaded_file):
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2}\s/\s[A-Z]{2})\s([A-Z]\d{9})\s(\d{2}/\d{2}/\d{4})\s(\d{3}-\d)\s/\s(\d)"  
    # Chamando a função loop para processar o PDF e criar o DataFrame
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)
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
    download(df)
def dnit_todos(uploaded_file):
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2}\s/\s[A-Z]{2})\s([A-Z]\d{9})\s(\d{2}/\d{2}/\d{4})\s(\d{3}-\d)\s/\s(\d)"  
    # Chamando a função loop para processar o PDF e criar o DataFrame
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)
    # Cria o DataFrame final com todas as informações extraídas de todas as páginas
    df = pd.DataFrame(todas_tabelas, columns=["Placa/UF", "Nº do Auto de Infração", "Data da Infração", "Código da Infração", "Desdobramento"])
    # Filtra as linhas que contêm "/RS" na coluna "Placa/UF"
    df = df[df["Código da Infração"] == "747-1"]
    df = df[df["Desdobramento"] == "0"]
    # Remove as colunas indesejadas do DataFrame
    df.drop(columns=["Nº do Auto de Infração", "Data da Infração", "Código da Infração", "Desdobramento"], inplace=True)
    # Remove o UF da coluna "Placa/UF"
    df["Placa/UF"] = df["Placa/UF"].str.split("/", n=1).str[0]
    download(df)   
# DETRAN - MS
def detran_MS_processos(uploaded_file):
    padrao_linha_tabela = r"Condutor:\s+(.*?)\n"
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)
    df = pd.DataFrame(todas_tabelas, columns=["Condutor"])
    download(df)
def detran_MS_defesa(uploaded_file):
    padrao_linha_tabela = r"Condutor:\s+(.*?)\n"
    padrao1_linha_tabela = r"Condutor:\s+(.*?)\n"
    padrao2_linha_tabela = r"Previsão Legal \(CTB\): (.+?)\n"
    todas_tabelas1 = loop(uploaded_file, padrao1_linha_tabela)
    todas_tabelas2 = loop(uploaded_file, padrao2_linha_tabela)
    df1 = pd.DataFrame(todas_tabelas1, columns=["Condutor"])
    df2 = pd.DataFrame(todas_tabelas2, columns=["Previsão Legal"])
    df = pd.concat([df1, df2], axis=1)
    df = df[df["Previsão Legal"] != "218 III"]
    df.drop(columns=["Previsão Legal"], inplace=True)
    download(df)
def detran_MS_recurso(uploaded_file):
    padrao_linha_tabela = r"Condutor:\s+(.*?)\n"
    padrao1_linha_tabela = r"Condutor:\s+(.*?)\n"
    padrao2_linha_tabela = r"Fundamento legal (.+?) Processo"
    padrao3_linha_tabela = r"Prazo:\s+(.*?)\n"
    todas_tabelas1 = loop(uploaded_file, padrao1_linha_tabela)
    todas_tabelas2 = loop(uploaded_file, padrao2_linha_tabela)
    todas_tabelas3 = loop(uploaded_file, padrao3_linha_tabela)    
    df1 = pd.DataFrame(todas_tabelas1, columns=["Condutor"])
    df2 = pd.DataFrame(todas_tabelas2, columns=["Previsão Legal"])
    df3 = pd.DataFrame(todas_tabelas3, columns=["Prazo"])
    df4 = pd.concat([df1, df2], axis=1)
    df = pd.concat([df4, df3], axis=1)
    df = df[df["Previsão Legal"] != "218 III"]
    df = df[df["Previsão Legal"] != "02 MESES"]
    df = df[df["Previsão Legal"] != "04 MESES"]
    df = df[df["Previsão Legal"] != "06 MESES"]
    df.drop(columns=["Previsão Legal"], inplace=True)
    df.drop(columns=["Prazo"], inplace=True)
    download(df)
def detran_MS_placas(uploaded_file):
    padrao1_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2})\s([A-Z0-9]+)\s(\d+)"
    padrao2_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2})\s([A-Z0-9]+)\s(\d+)\s(\d{2}/\d{2}/\d{4})\s(\d{2}/\d{2}/\d{4})\s([\d,]+(?:\.\d{3})*,\d+)"
    todas_tabelas1 = loop(uploaded_file, padrao1_linha_tabela)
    todas_tabelas2 = loop(uploaded_file, padrao2_linha_tabela)
    df = pd.DataFrame(todas_tabelas1, columns=["Placa", "Número Auto", "Código da Infração"])
    df2 = pd.DataFrame(todas_tabelas2, columns=["Placa", "Número Auto", "Código da Infração","Data de Infração", "Data Limite", "Valor"])
    df2 = df2["Placa"]
    df3 = df[~df['Placa'].isin(df2)]
    codigos_infracoes_filtrados = ['51691', '51692', '75790', '52151', '52152', '52400', '52581', '52582', '52583', '52661', '52662' , '52663', '52741', '52742', '52820', '52900', '53040', '53120', '53200', '57970', '60760', '76171', '76172', '76173', '76090']
    df3 = df3[df3['Código da Infração'].isin(codigos_infracoes_filtrados)]
    df3.drop(columns=["Número Auto", "Código da Infração"], inplace=True)
    df3 = df3.drop_duplicates(subset=['Placa'])
    download(df)
# DETRAN - RS
def detran_RS_placas(uploaded_file):
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2})\s(\d{2}/\d{2}/\d{4})\s(\d+)\s([A-Z]{1,2}\d+)\s(\d+)"
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)
    df = pd.DataFrame(todas_tabelas, columns=["Placa", "Data da Infração", "Órgão Autuador","Série", "Cód. Infração"])
    codigos_infracoes_filtrados = ['51691', '51692', '75790', '52151', '52152', '52400', '52581', '52582', '52583', '52661', '52662' , '52663', '52741', '52742', '52820', '52900', '53040', '53120', '53200', '57970', '60760', '74710', '70301', '70303','70481', '70483', '70561', '70562', '70721', '70722', '76171', '76172', '76173', '76090']
    df = df[df['Cód. Infração'].isin(codigos_infracoes_filtrados)]
    df.drop(columns=["Data da Infração", "Órgão Autuador","Série", "Cód. Infração"], inplace=True)
    df = df.drop_duplicates(subset='Placa').dropna(subset=['Placa'])
    download(df)
# DETRAN - SC
def detran_SC_placas(uploaded_file):
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2})\s([A-Z0-9]+)\s(\d{2}/\d{2}/\d{4})\s(\d{4}-\d)\s(\d{2}/\d{2}/\d{4})"                    
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)
    df = pd.DataFrame(todas_tabelas, columns=["Placa", "Número Auto", "Data Infração", "Código da Infração", "Data Limite"])
    codigos_infracoes_filtrados = ['5169-1', '5169-2', '7579-0', '5215-1', '5215-2', '5240-0', '5258-1', '5258-2', '5258-3', '5266-1', '5266-2' , '5266-3', '5274-1', '5274-2', '5282-0', '5290-0', '5304-0', '5312-0', '5320-0', '5797-0', '6076-0', '7617-1', '7617-2', '7617-3', '7609-0']
    df = df[df['Código da Infração'].isin(codigos_infracoes_filtrados)]
    df.drop(columns=["Número Auto", "Data Infração","Código da Infração", "Data Limite"], inplace=True)
    download(df)
# PRF - RS
def PRF_RS_autuacao(uploaded_file):
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2})\s([A-Z]\d{9})\s(\d{2}/\d{2}/\d{4})\s(\d{4}/\d)\s(\d{2}/\d{2}/\d{4})"
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)
    df = pd.DataFrame(todas_tabelas, columns=["Placa", "Nº do Auto de Infração", "Data da Infração", "Código da Infração/Desdobramento", "Data de Vencimento da Notificação"])
    codigos_infracoes_filtrados = ['5169/1', '5169/2', '7579/0', '5215/1', '5215/2', '5240/0', '5258/1', '5258/2', '5258/3', '5266/1', '5266/2' , '5266/3', '5274/1', '5274/2', '5282/0', '5290/0', '5304/0', '5312/0', '5320/0', '5797/0', '6076/0', '7471/0', '7030/1', '7030/3','7048/1', '7048/3', '7056/1', '7056/2', '7072/1', '7072/2', '7617/1', '7617/2', '7617/3', '7609/0']
    df = df[df['Código da Infração/Desdobramento'].isin(codigos_infracoes_filtrados)]
    df = df[df['Placa'].str.startswith('I')]
    df.drop(columns=["Nº do Auto de Infração", "Data da Infração", "Data de Vencimento da Notificação"], inplace=True)
    download(df)
def PRF_RS_penalidade(uploaded_file):
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2}),\s([A-Z]\d{9}),\s(\d{2}/\d{2}/\d{4}),\s(\d{4}/\d{1,2}),\s(R\$[\d.,]+),\s(\d{2}/\d{2}/\d{4})"
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)
    df = pd.DataFrame(todas_tabelas, columns=["Placa", "Nº do Auto de Infração", "Data da Infração", "Código da Infração/Desdobramento","Valor multa", "Data de Vencimento da Notificação"])
    codigos_infracoes_filtrados =  ['5169/1', '5169/2', '7579/0', '5215/1', '5215/2', '5240/0', '5258/1', '5258/2', '5258/3', '5266/1', '5266/2' , '5266/3', '5274/1', '5274/2', '5282/0', '5290/0', '5304/0', '5312/0', '5320/0', '5797/0', '6076/0', '7471/0', '7030/1', '7030/3','7048/1', '7048/3', '7056/1', '7056/2', '7072/1', '7072/2', '7617/1', '7617/2', '7617/3', '7609/0']
    df = df[df['Código da Infração/Desdobramento'].isin(codigos_infracoes_filtrados)]
    df = df[df['Placa'].str.startswith('I')]
    df.drop(columns=["Nº do Auto de Infração", "Data da Infração","Valor multa","Data de Vencimento da Notificação"], inplace=True)
    download(df)
# PRF - Outros estados        
def PRF_outros_recusa(uploaded_file):
    
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2})\s([A-Z]\d{9})\s(\d{2}/\d{2}/\d{4})\s(\d{4}/\d)\s(\d{2}/\d{2}/\d{4})"

    # Inicialize uma lista vazia para armazenar todas as tabelas encontradas
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)

    # Cria o DataFrame final com todas as informações extraídas de todas as páginas
    df = pd.DataFrame(todas_tabelas, columns=["Placa", "Nº do Auto de Infração", "Data da Infração", "Código da Infração/Desdobramento", "Data de Vencimento da Notificação"])

    # Filtrar os dados com base nos códigos de infração específicos
    codigos_infracoes_filtrados = ['7579/0']
    df = df[df['Código da Infração/Desdobramento'].isin(codigos_infracoes_filtrados)]
    df = df

    # Remover as colunas indesejadas do DataFrame
    df.drop(columns=["Nº do Auto de Infração", "Data da Infração", "Data de Vencimento da Notificação"], inplace=True)

    download(df)
def PRF_outros_bafometro(uploaded_file):
    
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2})\s([A-Z]\d{9})\s(\d{2}/\d{2}/\d{4})\s(\d{4}/\d)\s(\d{2}/\d{2}/\d{4})"

    # Inicialize uma lista vazia para armazenar todas as tabelas encontradas
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)

    # Cria o DataFrame final com todas as informações extraídas de todas as páginas
    df = pd.DataFrame(todas_tabelas, columns=["Placa", "Nº do Auto de Infração", "Data da Infração", "Código da Infração/Desdobramento", "Data de Vencimento da Notificação"])

    # Filtrar os dados com base nos códigos de infração específicos
    codigos_infracoes_filtrados = ['5169/1', '5169/2',]
    df = df[df['Código da Infração/Desdobramento'].isin(codigos_infracoes_filtrados)]
    df = df

    # Remover as colunas indesejadas do DataFrame
    df.drop(columns=["Nº do Auto de Infração", "Data da Infração", "Data de Vencimento da Notificação"], inplace=True)

    download(df)
def PRF_outros_completo(uploaded_file):
    
    padrao_linha_tabela = r"([A-Z]{3}\d{1}\w{1}\d{2})\s([A-Z]\d{9})\s(\d{2}/\d{2}/\d{4})\s(\d{4}/\d)\s(\d{2}/\d{2}/\d{4})"

    # Inicialize uma lista vazia para armazenar todas as tabelas encontradas
    todas_tabelas = loop(uploaded_file, padrao_linha_tabela)

    # Cria o DataFrame final com todas as informações extraídas de todas as páginas
    df = pd.DataFrame(todas_tabelas, columns=["Placa", "Nº do Auto de Infração", "Data da Infração", "Código da Infração/Desdobramento", "Data de Vencimento da Notificação"])

    # Filtrar os dados com base nos códigos de infração específicos
    codigos_infracoes_filtrados = ['5169/1', '5169/2', '7579/0', '5215/1', '5215/2', '5240/0', '5258/1', '5258/2', '5258/3', '5266/1', '5266/2' , '5266/3', '5274/1', '5274/2', '5282/0', '5290/0', '5304/0', '5312/0', '5320/0', '5797/0', '6076/0', '7471/0', '7030/1', '7030/3','7048/1', '7048/3', '7056/1', '7056/2', '7072/1', '7072/2', '7617/1', '7617/2', '7617/3', '7609/0']
    df = df[df['Código da Infração/Desdobramento'].isin(codigos_infracoes_filtrados)]
    df = df

    # Remover as colunas indesejadas do DataFrame
    df.drop(columns=["Nº do Auto de Infração", "Data da Infração", "Data de Vencimento da Notificação"], inplace=True)

    download(df)
# Nomes Faltantes
def nomes_faltantes(uploaded_file_comp,uploaded_file_red):
    # Carregar os arquivos CSV
    COMPLETO = pd.read_csv(uploaded_file_comp, header=None)
    REDUZIDO = pd.read_csv(uploaded_file_red, header=None)
    COMPLETO.columns = ["COMPLETO"]
    REDUZIDO.columns = ["REDUZIDO"]
    # Encontrar nomes que estão em COMPLETO mas não em REDUZIDO
    nomes_faltantes = COMPLETO[~COMPLETO["COMPLETO"].isin(REDUZIDO["REDUZIDO"])]
    # Renomear a coluna
    nomes_faltantes.columns = ["FINAL"]
    download(nomes_faltantes)

# Obtendo a entrada do usuário para selecionar o serviço
servico_sel = st.sidebar.selectbox("Serviço", servicos)

if servico_sel == "Leitura de PDF":
    # Dicionário mapeando os tipos de PDF para as opções de processamento correspondentes
    opcoes_processamento = {
        "DETRAN - ES": {},
        "DETRAN - MS": {
            "Placas": detran_MS_placas,
            "Processos": detran_MS_processos,
            "Defesa (sem 218)": detran_MS_defesa,
            "Recurso (sem 246)": detran_MS_recurso
        },
        "DETRAN - RS": {
            "Placas": detran_RS_placas
        },
        "DETRAN - SC": {
         "Placas": detran_SC_placas
        },
        "DNIT": {
            "Modelo de PDF DNIT - RS": dnit_rs,
            "Modelo de PDF DNIT - Todos": dnit_todos
        },
        "PRF - Outros estados": {
            "Autuação - Bafômetro": PRF_outros_bafometro,
            "Autuação - Completo": PRF_outros_completo,
            "Autuação - Recusa": PRF_outros_recusa
        },
        "PRF - RS": {
            "Penalidade": PRF_RS_penalidade,
            "Autuação": PRF_RS_autuacao
        },
        "Nomes Faltantes": {
            "Nomes Faltantes": nomes_faltantes
        }
    }

    # Selecionar tipo de PDF e opção de processamento
    opcoes_tipo_pdf = list(opcoes_processamento.keys())
    tipo_pdf_sel = st.sidebar.selectbox("Tipo de PDF", opcoes_tipo_pdf)
    
    opcoes_processamento_selecionado = opcoes_processamento[tipo_pdf_sel]
    opcoes_processamento_selecionado_nomes = list(opcoes_processamento_selecionado.keys())
    opcao_processamento_sel = st.sidebar.selectbox(f"Selecione uma opção {tipo_pdf_sel}", opcoes_processamento_selecionado_nomes)
    
    uploaded_file_comp = None
    uploaded_file_red = None
    uploaded_file = None

    if tipo_pdf_sel == "Nomes Faltantes":
        st.sidebar.title("Upload de arquivo 🗂️")
        uploaded_file_comp = st.sidebar.file_uploader(f"Escolha o seu csv - Completo", accept_multiple_files=False, type=('csv'), help=("Coloque um arquivo .csv"))
        uploaded_file_red = st.sidebar.file_uploader(f"Escolha o seu csv - Reduzido", accept_multiple_files=False, type=('csv'), help=("Coloque um arquivo .csv"))
    elif tipo_pdf_sel == "DETRAN - ES":
            link = "https://colab.research.google.com/drive/1dW1ITnB7DZyTyxbNFs_Kt-tVDhPZHho6#scrollTo=_h1SCm_NmTA0"
            st.markdown(f'''
                <a href="{link}" target="_blank">
                    <button style="
                        color: white; 
                        background-color: #3540E6; 
                        border: none; 
                        padding: 10px 20px; 
                        text-align: center; 
                        display: inline-block; 
                        font-size: 16px; 
                        margin: 4px 2px; 
                        cursor: pointer;
                        border-radius: 20px;  /* Arredondamento dos cantos */
                    ">
                        Abrir Colab
                    </button>
                </a>
                ''', unsafe_allow_html=True)
    else:
        st.sidebar.title("Upload de arquivo 🗂️")
        uploaded_file = st.sidebar.file_uploader(f"Escolha o seu PDF - {tipo_pdf_sel}", accept_multiple_files=False, type=('pdf'), help=("Coloque um arquivo .pdf"))

    # Botão unificado de processamento
    if uploaded_file_red != None or uploaded_file != None:
        if st.sidebar.button('Processar Arquivo', type="primary"):
            if tipo_pdf_sel == "Nomes Faltantes":
                # Passando ambos os arquivos CSV para a função de processamento
                opcoes_processamento[tipo_pdf_sel][opcao_processamento_sel](uploaded_file_comp, uploaded_file_red)
            else:
                # Passando o arquivo PDF para a função de processamento
                opcoes_processamento[tipo_pdf_sel][opcao_processamento_sel](uploaded_file)

elif servico_sel == "Consulta de placas - GOV":
    link = "https://colab.research.google.com/drive/1H8wCSJmwAf485EaE5xeJwuYWy4EqSQTW#scrollTo=4jfs5_C-0YA4"
    st.markdown(f'''
                <a href="{link}" target="_blank">
                    <button style="
                        color: white; 
                        background-color: #3540E6; 
                        border: none; 
                        padding: 10px 20px; 
                        text-align: center; 
                        display: inline-block; 
                        font-size: 16px; 
                        margin: 4px 2px; 
                        cursor: pointer;
                        border-radius: 20px;  /* Arredondamento dos cantos */
                    ">
                        Abrir Colab
                    </button>
                </a>
                ''', unsafe_allow_html=True)
else:
    uploaded_files = None
