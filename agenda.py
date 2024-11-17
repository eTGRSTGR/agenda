import streamlit as st
import pandas as pd
from datetime import date, datetime
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

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
        df = pd.read_csv("gastos.csv")
        df.columns = df.columns.str.strip()
        if 'Data Atual' in df.columns:
            df['Mês'] = pd.to_datetime(df['Data Atual'], format='%d-%m-%Y', errors='coerce').dt.month.map(meses_portugues)
        else:
            df['Mês'] = ''
        if 'Data Atual' not in df.columns:
            df['Data Atual'] = ''
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Categoria", "Item", "Valor", "Mês", "Data Atual"])
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado: {e}")
        return pd.DataFrame(columns=["Categoria", "Item", "Valor", "Mês", "Data Atual"])

# Função para salvar um novo gasto, anexando ao CSV existente
def save_data(new_entry):
    try:
        df = pd.read_csv("gastos.csv")
        df = pd.concat([df, new_entry], ignore_index=True)
    except FileNotFoundError:
        df = new_entry
    df.to_csv("gastos.csv", index=False)

data = initialize_data()

# Configurações de estilo
st.markdown(
    """
    <style>
    .main-title { color: #2E8B57; font-size: 2.5em; font-weight: bold; }
    .sub-title { color: #4682B4; font-size: 1.5em; margin-top: 1em; }
    .sidebar-title { color: #DAA520; font-size: 1.5em; }
    .sidebar-img { border-radius: 50%; width: 100px; height: 100px; margin: 5px 0 20px; }
    </style>
    """,
    unsafe_allow_html=True
)

# Título e descrição
st.markdown('<div class="main-title">Novo Sabor - Agenda </div>', unsafe_allow_html=True)

# Sidebar para inserção de imagem e dados
with st.sidebar:
    st.image("https://i.ibb.co/GpwXH1v/Design-sem-nome-2.png", use_container_width=True, caption="", output_format="JPEG")
    st.markdown('<div class="sidebar-title">Inserir novo gasto</div>', unsafe_allow_html=True)

# Exibe a tabela de gastos
st.markdown('<div class="sub-title">Tabela de Gastos</div>', unsafe_allow_html=True)
st.dataframe(data)

# Calcula o total dos gastos
if not data.empty and "Valor" in data.columns:
    total_gastos = data["Valor"].sum()
    st.markdown(f"<div class='sub-title'>Total dos Gastos: R$ {total_gastos:,.2f}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='sub-title'>Nenhum gasto registrado.</div>", unsafe_allow_html=True)

# Gráfico de Pizza - Proporção dos Gastos por Categoria
if not data.empty and "Valor" in data.columns:
    gastos_por_categoria = data.groupby("Categoria")["Valor"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(
        gastos_por_categoria["Valor"], 
        labels=gastos_por_categoria["Categoria"], 
        autopct='%1.1f%%', 
        startangle=90
    )
    ax.set_title("Proporção dos Gastos por Categoria", fontsize=16)
    st.pyplot(fig)

# Gráfico de Itens - Gastos por Item
if not data.empty and "Item" in data.columns:
    gastos_por_item = data.groupby("Item")["Valor"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(gastos_por_item["Item"], gastos_por_item["Valor"])
    ax.set_title("Gastos por Item", fontsize=16)
    ax.set_xlabel("Item", fontsize=14)
    ax.set_ylabel("Valor Gasto (R$)", fontsize=14)
    ax.tick_params(axis="x", rotation=45)  # Rotaciona os rótulos dos itens
    st.pyplot(fig)

# Gráfico de Barras Empilhadas - Gastos por Categoria ao Longo dos Meses
if not data.empty and "Mês" in data.columns:
    gastos_por_mes_categoria = data.groupby(["Mês", "Categoria"])["Valor"].sum().unstack()
    gastos_por_mes_categoria.plot(kind="bar", stacked=True, figsize=(12, 6))
    plt.title("Gastos por Categoria ao Longo dos Meses", fontsize=16)
    plt.xlabel("Mês", fontsize=14)
    plt.ylabel("Total Gasto (R$)", fontsize=14)
    st.pyplot(plt.gcf())  # Garante que o gráfico atual seja exibido no Streamlit

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
    categorias_itens = {
        "Gastos Diários": ["Açúcar", "Óleo", "Leite", "Pão de Queijo"],
        "A cada dois dias": ["Carne Moída", "Frango", "Abacaxi"],
        "Mercado Semanal": ["Coco", "Chocolate", "Pó Granulado", "Refrigerante", "Cenoura", "Temperos"],
        "Quinzenal": ["Trigo", "Mantimentos", "Chapa", "Margarina", "Gás", "Embalagens"],
        "Mensal": ["Funcionários", "Aluguel", "Água", "Energia", "Internet", "Maquineta", "Gastos Extras"]
    }
    categoria = st.selectbox("Selecione a categoria", list(categorias_itens.keys()))
    item = st.selectbox("Selecione o item", categorias_itens[categoria])
    valor = st.number_input("Valor do Gasto", min_value=0.0, format="%.2f")
    data_gasto = st.date_input("Data do Gasto", value=date.today())
    mes_gasto = meses_portugues[data_gasto.month]
    data_atual = datetime.now().strftime('%d-%m-%Y')

    if st.button("Salvar Gasto", key='save-button'):
        if item and valor > 0:
            new_entry = pd.DataFrame([{
                "Categoria": categoria, 
                "Item": item, 
                "Valor": valor,
                "Mês": mes_gasto,
                "Data Atual": data_atual
            }])
            save_data(new_entry)
            st.success("Gasto salvo com sucesso!")
        else:
            st.error("Por favor, preencha todos os campos antes de salvar.")
