import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import math

# ==========================================
# 1. MOTOR QUANTITATIVO (OOP)
# ==========================================
class RoletaQuantEngine:
    def __init__(self):
        self.RODA = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 
                     5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        self.VERMELHOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        self.PROB_COR = 18 / 37
        self.PROB_DUZIA = 12 / 37

    def classificar(self, n):
        if n == 0: return {"Cor": "Verde", "Paridade": "Zero", "Duzia": "Zero", "Metade": "Zero"}
        return {
            "Cor": "Vermelho" if n in self.VERMELHOS else "Preto",
            "Paridade": "Par" if n % 2 == 0 else "Ímpar",
            "Duzia": "1ª Dúzia" if n <= 12 else "2ª Dúzia" if n <= 24 else "3ª Dúzia",
            "Metade": "Baixo (1-18)" if n <= 18 else "Alto (19-36)"
        }

    def calcular_z_score(self, observacoes, total_jogadas, probabilidade_teorica):
        """
        Calcula o Z-Score para detetar anomalias estatísticas na roda física.
        Z = (X - μ) / σ
        """
        if total_jogadas == 0: return 0
        esperado = total_jogadas * probabilidade_teorica
        desvio_padrao = math.sqrt(total_jogadas * probabilidade_teorica * (1 - probabilidade_teorica))
        if desvio_padrao == 0: return 0
        return (observacoes - esperado) / desvio_padrao

    def cadeias_de_markov(self, historico):
        """
        Analisa a probabilidade de transição empírica (Ex: Qual a % de sair Preto DEPOIS de um Vermelho?)
        """
        if len(historico) < 2: return pd.DataFrame()
        
        transicoes = {"Vermelho": {"Vermelho": 0, "Preto": 0, "Verde": 0},
                      "Preto": {"Vermelho": 0, "Preto": 0, "Verde": 0},
                      "Verde": {"Vermelho": 0, "Preto": 0, "Verde": 0}}
        
        cores = [self.classificar(n)["Cor"] for n in historico]
        for i in range(len(cores)-1):
            atual = cores[i]
            proximo = cores[i+1]
            transicoes[atual][proximo] += 1
            
        df_trans = pd.DataFrame(transicoes).T
        df_trans = df_trans.div(df_trans.sum(axis=1), axis=0).fillna(0) * 100
        return df_trans.round(2)

    def monte_carlo_banca(self, banca_inicial, aposta, historico, iteracoes=1000):
        """
        Simula 1000 cenários de 50 jogadas futuras usando o viés empírico atual da mesa.
        """
        if not historico: return []
        cores = [self.classificar(n)["Cor"] for n in historico]
        prob_empirica_red = cores.count("Vermelho") / len(cores)
        
        resultados_finais = []
        for _ in range(iteracoes):
            banca = banca_inicial
            for _ in range(50): # simula próximas 50 rodadas
                if banca < aposta: break
                # Aposta simulada no Vermelho baseada no viés da mesa vs algoritmo de RNG
                sorteio = np.random.choice(["Win", "Loss"], p=[prob_empirica_red, 1-prob_empirica_red])
                if sorteio == "Win": banca += aposta
                else: banca -= aposta
            resultados_finais.append(banca)
        return resultados_finais

# ==========================================
# 2. INICIALIZAÇÃO DA APP
# ==========================================
st.set_page_config(page_title="Roulette Quant Pro", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# Tema Escuro Avançado via CSS injection
st.markdown("""
    <style>
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 8px; border-left: 5px solid #00E676;}
    </style>
    """, unsafe_allow_html=True)

if 'historico_quant' not in st.session_state:
    st.session_state.historico_quant = []

engine = RoletaQuantEngine()

# ==========================================
# 3. BARRA LATERAL - CONTROLO E ENTRADA
# ==========================================
with st.sidebar:
    st.title("⚙️ Painel de Controlo")
    st.write("Insira os números da sessão real.")
    
    with st.form("input_form", clear_on_submit=True):
        novo_num = st.number_input("Número Sorteado (0-36):", min_value=0, max_value=36, step=1)
        submitted = st.form_submit_button("Submeter Jogada", use_container_width=True)
        if submitted:
            st.session_state.historico_quant.append(novo_num)
            st.rerun()
            
    if st.button("🚨 Reset Total (Nova Sessão)", type="primary", use_container_width=True):
        st.session_state.historico_quant = []
        st.rerun()

    st.divider()
    st.markdown("### Config. Simulação")
    banca = st.number_input("Banca Inicial ($):", value=1000, step=100)
    unidade = st.number_input("Unidade de Aposta ($):", value=25, step=5)

# ==========================================
# 4. DASHBOARD QUANTITATIVO PRINCIPAL
# ==========================================
historico = st.session_state.historico_quant
n_jogadas = len(historico)

st.title("📈 Análise Quantitativa de Roleta Europeia")

if n_jogadas < 10:
    st.warning("⚠️ O motor quantitativo requer pelo menos 10 jogadas para gerar matrizes de transição estatisticamente relevantes.")
    st.info(f"Jogadas inseridas: {n_jogadas}/10. Continue a inserir dados na barra lateral.")
else:
    # 4.1. Dados Processados
    dados = [engine.classificar(n) for n in historico]
    df_dados = pd.DataFrame(dados)
    
    # 4.2. Top Metrics (Visão Geral)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Volume de Amostra", n_jogadas)
    col2.metric("Último Número", historico[-1])
    
    # Z-Score do Vermelho
    qtd_vermelho = len(df_dados[df_dados["Cor"] == "Vermelho"])
    z_score_red = engine.calcular_z_score(qtd_vermelho, n_jogadas, engine.PROB_COR)
    col3.metric("Z-Score (Vermelho)", f"{z_score_red:.2f}", 
                delta="Anomalia!" if abs(z_score_red) > 2 else "Padrão Normal", 
                delta_color="inverse" if abs(z_score_red) > 2 else "off")
    
    # Detetor de Viés da Roda
    frequencias = Counter(historico)
    num_mais_quente = frequencias.most_common(1)[0]
    z_score_num = engine.calcular_z_score(num_mais_quente[1], n_jogadas, 1/37)
    col4.metric(f"Nº {num_mais_quente[0]} (Quente)", f"Saiu {num_mais_quente[1]}x", 
                delta=f"Z-Score: {z_score_num:.2f}", delta_color="normal")

    st.divider()

    # 4.3. ABAS DE ANÁLISE PROFUNDA
    aba1, aba2, aba3 = st.tabs(["🧬 Análise de Variância (Z-Scores)", "🔗 Matriz de Cadeias de Markov", "🎲 Simulação de Monte Carlo"])
    
    with aba1:
        st.markdown("### 🧬 Distribuição e Detetor de Viés Físico")
        st.write("Um Z-Score acima de +2.0 ou abaixo de -2.0 indica que a cor está a sair muito fora da probabilidade matemática esperada (possível tilt físico na mesa).")
        
        cores_counts = df_dados["Cor"].value_counts()
        fig_bar = go.Figure()
        
        for cor in ["Vermelho", "Preto", "Verde"]:
            qtd = cores_counts.get(cor, 0)
            esperado = n_jogadas * (engine.PROB_COR if cor != "Verde" else 1/37)
            
            fig_bar.add_trace(go.Bar(
                x=[cor], y=[qtd], name=f"{cor} (Real)",
                marker_color="#FF4136" if cor == "Vermelho" else "#111111" if cor == "Preto" else "#2ECC40"
            ))
            fig_bar.add_trace(go.Scatter(
                x=[cor], y=[esperado], mode="markers", name=f"Esperado",
                marker=dict(symbol="line-ew-open", size=40, color="white", line=dict(width=3))
            ))
            
        fig_bar.update_layout(title="Ocorrências Reais vs Esperança Matemática", barmode='overlay', template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    with aba2:
        st.markdown("### 🔗 Matriz de Transição (Preditiva Empírica)")
        st.write("Lê-se da Esquerda para o Topo. Exemplo: Quando o último foi Vermelho, qual a probabilidade empírica do próximo ser Preto nesta mesa?")
        
        df_markov = engine.cadeias_de_markov(historico)
        if not df_markov.empty:
            fig_heat = px.imshow(df_markov, text_auto=True, color_continuous_scale="Viridis",
                                 labels=dict(x="Próxima Cor", y="Cor Atual", color="Probabilidade (%)"),
                                 title="Mapa de Calor de Transição de Cores (%)")
            st.plotly_chart(fig_heat, use_container_width=True)
            
            # Alerta de Padrão
            max_trans = df_markov.max().max()
            if max_trans > 60:
                st.success(f"🔥 **Padrão Encontrado:** Existe uma transição a acontecer com {max_trans}% de frequência!")

    with aba3:
        st.markdown("### 🎲 Simulação de Bancarrota de Monte Carlo")
        st.write(f"Projeção baseada na tua banca de **${banca}** apostando **${unidade}** no Vermelho (usando o viés atual da mesa). Simulação de 1000 cenários para as próximas 50 jogadas.")
        
        projecoes = engine.monte_carlo_banca(banca, unidade, historico)
        if projecoes:
            fig_hist = px.histogram(projecoes, nbins=50, 
                                    title="Distribuição Probabilística da Banca após 50 Jogadas",
                                    labels={"value": "Banca Final ($)", "count": "Cenários Simulados"},
                                    color_discrete_sequence=["#00E676"])
            fig_hist.add_vline(x=banca, line_dash="dash", line_color="white", annotation_text="Banca Inicial (Break-Even)")
            
            st.plotly_chart(fig_hist, use_container_width=True)
            
            risco_ruina = len([p for p in projecoes if p < banca]) / len(projecoes) * 100
            st.markdown(f"**Risco Estatístico de Perda (Ruína):** `{risco_ruina:.2f}%`")
