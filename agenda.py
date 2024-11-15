import streamlit as st
import pandas as pd
from datetime import date, datetime

# Dicionário para traduzir os meses para português
meses_portugues = {
    1: "Janeiro",
    2: "Fevereiro",
    3: "Março",
    4: "Abril",
    5: "Maio",
    6: "Junho",
    7: "Julho",
    8: "Agosto",
    9: "Setembro",
    10: "Outubro",
    11: "Novembro",
    12: "Dezembro"
}

# Inicializa a planilha de gastos
def initialize_data():
    try:
        # Carregar o CSV
        df = pd.read_csv("gastos.csv")
        
        # Remover espaços extras das colunas
        df.columns = df.columns.str.strip()
        
        # Atualizar a coluna 'Mês' com base na coluna 'Data Atual'
        if 'Data Atual' in df.columns:
            df['Mês'] = pd.to_datetime(df['Data Atual'], format='%d-%m-%Y', errors='coerce').dt.month.map(meses_portugues)
        else:
            df['Mês'] = ''

        # Verificar se a coluna 'Data Atual' existe, se não, cria
        if 'Data Atual' not in df.columns:
            df['Data Atual'] = ''

        return df
    except FileNotFoundError:
        # Se o arquivo não existir, cria um DataFrame vazio com as colunas corretas
        return pd.DataFrame(columns=["Categoria", "Item", "Valor", "Mês", "Data Atual"])
    except Exception as e:
        # Captura outros erros
        st.error(f"Ocorreu um erro inesperado: {e}")
        return pd.DataFrame(columns=["Categoria", "Item", "Valor", "Mês", "Data Atual"])

# Função para salvar um novo gasto, anexando ao CSV existente
def save_data(new_entry):
    try:
        # Tenta carregar o CSV existente
        df = pd.read_csv("gastos.csv")
        df = pd.concat([df, new_entry], ignore_index=True)
    except FileNotFoundError:
        # Se o arquivo não existir, utiliza apenas o novo dado
        df = new_entry

    # Salva os dados atualizados no CSV
    df.to_csv("gastos.csv", index=False)

# Carrega os dados iniciais
data = initialize_data()

# Configurações de estilo
st.markdown(
    """
    <style>
    .main-title {
        color: #2E8B57;
        font-size: 2.5em;
        font-weight: bold;
    }
    .sub-title {
        color: #4682B4;
        font-size: 1.5em;
        margin-top: 1em;
    }
    .sidebar-title {
        color: #DAA520;
        font-size: 1.5em;
    }
    .button-primary {
        background-color: #4CAF50;
        color: white;
    }
    .button-secondary {
        background-color: #f44336;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Título e descrição
st.markdown('<div class="main-title">Agenda Digital de Gastos</div>', unsafe_allow_html=True)

# Exibe a tabela de gastos
st.markdown('<div class="sub-title">Tabela de Gastos</div>', unsafe_allow_html=True)
st.dataframe(data)

# Opção para download da tabela de gastos abaixo da tabela
csv = data.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Baixar tabela de gastos em CSV",
    data=csv,
    file_name="gastos.csv",
    mime="text/csv",
    key='download-button'
)

# Sidebar para inserir um novo gasto
with st.sidebar:
    st.markdown('<div class="sidebar-title">Inserir novo gasto</div>', unsafe_allow_html=True)
    categorias_itens = {
        "Gastos Diários": ["Açúcar", "Óleo", "Leite", "Pão de Queijo"],
        "A cada dois dias": ["Carne Moída", "Frango", "Abacaxi"],
        "Mercado Semanal": ["Coco", "Chocolate", "Pó Granulado", "Refrigerante", "Cenoura", "Temperos"],
        "Quinzenal": ["Trigo", "Mantimentos", "Chapa", "Margarina", "Gás", "Embalagens"],
        "Mensal": ["Funcionários", "Aluguel", "Água", "Energia", "Internet", "Maquineta", "Gastos Extras"]
    }
    categoria = st.selectbox(
        "Selecione a categoria",
        list(categorias_itens.keys())
    )
    item = st.selectbox("Selecione o item", categorias_itens[categoria])
    valor = st.number_input("Valor do Gasto", min_value=0.0, format="%.2f")
    
    # Exibe o mês da data do gasto em português usando o dicionário de meses
    data_gasto = st.date_input("Data do Gasto", value=date.today())
    mes_gasto = meses_portugues[data_gasto.month]  # Nome do mês em português

    # Data atual do registro em formato dia-mês-ano
    data_atual = datetime.now().strftime('%d-%m-%Y')

    if st.button("Salvar Gasto", key='save-button'):
        if item and valor > 0:
            # Cria um DataFrame com o novo gasto
            new_entry = pd.DataFrame([{
                "Categoria": categoria, 
                "Item": item, 
                "Valor": valor,
                "Mês": mes_gasto,  # Adiciona o mês em português
                "Data Atual": data_atual  # Adiciona a data atual do registro
            }])
            
            # Salva apenas o novo gasto, anexando ao CSV existente
            save_data(new_entry)
            
            st.success("Gasto salvo com sucesso!")
        else:
            st.error("Por favor, preencha todos os campos antes de salvar.")
