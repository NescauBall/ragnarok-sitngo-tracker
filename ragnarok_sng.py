import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def load_data(file_path):
    """Carrega os dados do CSV e retorna um DataFrame."""
    df = pd.read_csv(file_path)
    return df

def calculate_metrics(df):
    """Calcula XP acumulado e outras métricas essenciais."""
    df['XP Acumulado'] = df['Pontos Totais'].cumsum()
    df['Sessão Positiva'] = df['Lucro Total'] > 0
    df['ROI (%)'] = (df['Lucro Total'] / df['Buy-ins Investidos']) * 100
    df['Ganhou +5 Buy-ins'] = df['Lucro Total'] >= (df['Buy-ins Investidos'] * 5)
    return df

def plot_graphs(df):
    """Gera gráficos de evolução do XP e ROI."""
    st.subheader("📈 Evolução do XP Total")
    fig, ax = plt.subplots()
    ax.plot(df['Sessão'], df['XP Acumulado'], marker='o', linestyle='-', color='blue')
    ax.set_xlabel("Sessão")
    ax.set_ylabel("XP Total Acumulado")
    ax.set_title("Evolução do XP por Sessão")
    ax.grid(True)
    st.pyplot(fig)
    
    st.subheader("📊 Evolução do ROI (%)")
    fig, ax = plt.subplots()
    ax.plot(df['Sessão'], df['ROI (%)'], marker='s', linestyle='-', color='green')
    ax.axhline(y=0, color='red', linestyle='--', label='Break-even (0%)')
    ax.set_xlabel("Sessão")
    ax.set_ylabel("ROI (%)")
    ax.set_title("Evolução do ROI por Sessão")
    ax.grid(True)
    st.pyplot(fig)

def display_table(df):
    """Exibe tabelas com layout melhorado."""
    st.subheader("📋 Tabela de Acompanhamento")
    st.dataframe(df.style.format({
        "Lucro Total": "${:,.2f}",
        "Buy-ins Investidos": "${:,.2f}",
        "ROI (%)": "{:.2f}%",
        "XP Acumulado": "{:,.0f}",
    }).applymap(lambda x: 'background-color: lightgreen' if x > 0 else 'background-color: lightcoral' if isinstance(x, (int, float)) and x < 0 else ''))

def main():
    st.set_page_config(page_title="Ragnarok Sit & Go Tracker", layout="wide")
    st.title("🃏 Ragnarok Sit & Go Tracker 🎮")
    st.write("Acompanhe suas sessões de Sit & Go e veja a evolução das classes do Ragnarok.")
    
    uploaded_file = st.file_uploader("📂 Faça o upload do CSV das sessões", type=["csv"])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        df = calculate_metrics(df)
        
        display_table(df)
        plot_graphs(df)
    
if __name__ == "__main__":
    main()
