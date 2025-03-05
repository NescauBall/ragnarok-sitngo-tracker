import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import re

def load_data(file_path):
    """Carrega os dados do CSV e retorna um DataFrame."""
    df = pd.read_csv(file_path)
    return df

def convert_money(value):
    """Converte valores monetários de string para float."""
    value = value.replace("$", "").replace(",", "")  # Remove símbolos e vírgulas
    try:
        return float(value)
    except ValueError:
        return None

def convert_buyin(value):
    """Converte Buy-in (exemplo: "$1.70+$0.30" → 2.00)."""
    parts = re.findall(r"[\d.]+", value)  # Extrai números
    if len(parts) == 2:
        return float(parts[0]) + float(parts[1])  # Soma Buy-in + Rake
    return None

def calculate_metrics(df):
    """Calcula XP acumulado e outras métricas essenciais."""
    df["Buy-In"] = df["Buy-In"].apply(convert_buyin)
    df["My C Net Won"] = df["My C Net Won"].apply(convert_money)
    df["Sessão"] = (df.index // 6) + 1  # Cada 6 torneios formam uma sessão
    
    # Agrupando por sessão para cálculos
    df_sessions = df.groupby("Sessão").agg(
        Buy_In_Medio=("Buy-In", "mean"),
        Lucro_Total=("My C Net Won", "sum"),
        Torneios_Jogados=("My C Net Won", "count")
    ).reset_index()
    
    # Calculando se a sessão foi positiva e se ganhou +5 buy-ins
    df_sessions["Sessão Positiva"] = df_sessions["Lucro_Total"] > 0
    df_sessions["Ganhou +5 Buy-ins"] = (df_sessions["Lucro_Total"] / df_sessions["Buy_In_Medio"]) >= 5
    
    # Cálculo de XP baseado nas regras definidas
    df_sessions["XP Ganho"] = (
        df["Finish"].apply(lambda x: 10 if x == 1 else 7 if x == 2 else 5 if x == 3 else -2 if x == 4 else 0).groupby(df["Sessão"]).sum() +
        df_sessions["Sessão Positiva"] * 3 +
        df_sessions["Ganhou +5 Buy-ins"] * 5
    )
    
    df_sessions["XP Acumulado"] = df_sessions["XP Ganho"].cumsum()
    df_sessions["ROI (%)"] = (df_sessions["Lucro_Total"] / (df_sessions["Buy_In_Medio"] * df_sessions["Torneios_Jogados"])) * 100
    
    return df_sessions

def plot_graphs(df):
    """Gera gráficos de evolução do XP e ROI."""
    st.subheader("📈 Evolução do XP Total")
    fig, ax = plt.subplots()
    ax.plot(df["Sessão"], df["XP Acumulado"], marker='o', linestyle='-', color='blue')
    ax.set_xlabel("Sessão")
    ax.set_ylabel("XP Total Acumulado")
    ax.set_title("Evolução do XP por Sessão")
    ax.grid(True)
    st.pyplot(fig)
    
    st.subheader("📊 Evolução do ROI (%)")
    fig, ax = plt.subplots()
    ax.plot(df["Sessão"], df["ROI (%)"], marker='s', linestyle='-', color='green')
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
        "Buy_In_Medio": "${:,.2f}",
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
        df_sessions = calculate_metrics(df)
        
        display_table(df_sessions)
        plot_graphs(df_sessions)
    
if __name__ == "__main__":
    main()
