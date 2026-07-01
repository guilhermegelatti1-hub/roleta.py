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
        # A roda física real da Roleta Europeia
        self.RODA = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 
                     5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        self.VERMELHOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        self.PROB_COR = 18 / 37
        
        self.JEU_ZERO = {12, 35, 3, 26, 0, 32, 15}
        self.VOISINS = {22, 18, 29, 7, 28, 19, 4, 21, 2, 25}
        self.ORPHELINS = {1, 20, 14, 31, 9, 6, 34, 17}
        self.TIERS = {27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33}

    def classificar(self, n):
        n = int(n)
        if n == 0: return {"Cor": "Verde", "Paridade": "Zero", "Duzia": "Zero", "Metade": "Zero"}
        return {
            "Cor": "Vermelho" if n in self.VERMELHOS else "Preto",
            "Paridade": "Par" if n % 2 == 0 else "Ímpar",
            "Duzia": "1ª Dúzia" if n <= 12 else "2ª Dúzia" if n <= 24 else "3ª Dúzia",
            "Metade": "Baixo (1-18)" if n <= 18 else "Alto (19-36)"
        }

    def classificar_setor_pista(self, n):
        n = int(n)
        if n in self.JEU_ZERO: return "Jeu Zéro"
        if n in self.VOISINS: return "Voisins"
        if n in self.ORPHELINS: return "Orphelins"
        if n in self.TIERS: return "Tiers"
        return "Erro"

    def cadeias_de_markov(self, historico):
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

    def calcular_maior_atraso(self, historico):
        if not historico: return "Nenhum", 0
        hist_inv = historico[::-1]
        cores = [self.classificar(n)["Cor"] for n in hist_inv]
        atraso_verm = next((i for i, cor in enumerate(cores) if cor == "Vermelho"), len(cores))
        atraso_preto = next((i for i, cor in enumerate(cores) if cor == "Preto"), len(cores))
        if atraso_verm > atraso_preto: return "Vermelho", atraso_verm
        elif atraso_preto > atraso_verm: return "Preto", atraso_preto
        return "Nenhum", 0

    # NOVO MÓDULO: CÁLCULO DE FÍSICA E SALTOS NA RODA
    def calcular_saltos(self, historico):
        """Calcula a distância (sentido horário) entre jogadas consecutivas no cilindro físico"""
        if len(historico) < 2: return []
        saltos = []
        for i in range(len(historico)-1):
            n_atual = int(historico[i])
            n_seguinte = int(historico[i+1])
            idx_atual = self.RODA.index(n_atual)
            idx_seguinte = self.RODA.index(n_seguinte)
            
            # Cálculo da distância circular
            distancia = (idx_seguinte - idx_atual) % 37
            saltos.append(distancia)
        return saltos

    def projetar_alvo(self, ultimo_numero, salto_predito):
        """Calcula onde a bola vai cair com base no salto previsto"""
        idx_atual = self.RODA.index(int(ultimo_numero))
        idx_alvo = (idx_atual + salto_predito) % 37
        alvo_principal = self.RODA[idx_alvo]
        
        # Pega os 2 vizinhos de cada lado para criar uma "Zona de Aterrizagem"
        zona = []
        for i in range(-2, 3):
            idx_vizinho = (idx_alvo + i) % 37
            zona.append(self.RODA[idx_vizinho])
            
        return alvo_principal, zona

# ==========================================
# 2. INICIALIZAÇÃO DA APP
# ==========================================
st.set_page_config(page_title="Roulette Quant Pro", layout="wide", page_icon="📈", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 8px; border-left: 5px solid #00E676;}
    .radar-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white; text-align: center; font-weight: bold;}
    .pista-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%); color: black; text-align: center; font-weight: bold; border: 2px solid white;}
    .alvo-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #FF4136 0%, #FF851B 100%); color: white; text-align: center; font-weight: bold; border: 2px solid white;}
    </style>
    """, unsafe_allow_html=True)

if 'historico_quant' not in st.session_state:
    st.session_state.historico_quant = []

engine = RoletaQuantEngine()

# ==========================================
# 3. BARRA LATERAL (Inserção Ultra-Rápida)
# ==========================================
def registar_jogada():
    num = st.session_state.input_roleta
    if num is not None:
        st.session_state.historico_quant.append(int(num))
        st.session_state.input_roleta = None

with st.sidebar:
    st.title("⚙️ Inserir Dados")
    st.write("Digita o número e prime **ENTER**.")
    
    st.number_input("Número Sorteado (0-36):", min_value=0, max_value=36, step=1, value=None, key="input_roleta", on_change=registar_jogada)
            
    st.write("---")
    if st.button("🚨 Nova Sessão", type="primary", use_container_width=True):
        st.session_state.historico_quant = []
        st.rerun()

# ==========================================
# 4. DASHBOARD VISUAL
# ==========================================
historico = st.session_state.historico_quant
n_jogadas = len(historico)
LIMITE_CALIBRACAO = 25 

st.title("🎯 Radar Estatístico & Físico")

if n_jogadas < LIMITE_CALIBRACAO:
    st.warning("⚠️ A recolher dados da física da mesa e memória muscular do croupier.")
    st.markdown(f"### Calibrando: {n_jogadas} / {LIMITE_CALIBRACAO} jogadas")
    progresso = int((n_jogadas / LIMITE_CALIBRACAO) * 100)
    st.progress(progresso, text=f"{progresso}% concluído")
    
    if n_jogadas > 0: st.write(f"**Histórico:** {historico}")
else:
    st.success(f"✅ Mesa Calibrada. {n_jogadas} jogadas em análise.")
    
    # ---------------------------------------------------------
    # NOVO: MÓDULO DE FÍSICA E ASSINATURA DO CROUPIER
    # ---------------------------------------------------------
    st.markdown("### 🕵️‍♂️ Detetor de Assinatura do Croupier (Predição Física)")
    
    saltos = engine.calcular_saltos(historico)
    contagem_saltos = Counter(saltos)
    
    if contagem_saltos:
        salto_mais_comum = contagem_saltos.most_common(1)[0]
        distancia_padrao = salto_mais_comum[0]
        freq_salto = salto_mais_comum[1]
        percentagem_salto = (freq_salto / len(saltos)) * 100
        
        ultimo_numero = historico[-1]
        alvo, zona_aterrizagem = engine.projetar_alvo(ultimo_numero, distancia_padrao)
        
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            st.metric("Distância Padrão (Casas)", f"+{distancia_padrao} casas", f"Ocorre em {percentagem_salto:.1f}% dos giros")
            st.write(f"O croupier tem a tendência física de lançar a bola para aterrar **{distancia_padrao} posições** à frente do último número sorteado.")
        
        with col_f2:
            st.markdown(f"<div class='alvo-box'>🎯 ALVO PROJETADO PARA O PRÓXIMO GIRO: NÚMERO {alvo}<br>Zona de Aterrizagem sugerida (Vizinhos): {zona_aterrizagem}</div>", unsafe_allow_html=True)

    st.divider()

    # ---------------------------------------------------------
    # ANÁLISE DA PISTA (RACETRACK)
    # ---------------------------------------------------------
    st.markdown("### 🏎️ Análise da Pista (Racetrack)")
    
    setores = [engine.classificar_setor_pista(n) for n in historico]
    contagem_setores = Counter(setores)
    max_ocorrencias = max(contagem_setores.values())
    setores_quentes = [setor for setor, qtd in contagem_setores.items() if qtd == max_ocorrencias]
    
    nome_setor_display = "EMPATE: " + " / ".join(setores_quentes) if len(setores_quentes) > 1 else setores_quentes[0]
    prob_real = (max_ocorrencias / n_jogadas) * 100
    
    st.markdown(f"<div class='pista-box'>🔥 ZONA FÍSICA MAIS QUENTE: {nome_setor_display.upper()} 🔥<br>Lidera com {max_ocorrencias} bolas ({prob_real:.1f}% das rodadas)</div>", unsafe_allow_html=True)

    st.divider()

    # ---------------------------------------------------------
    # SUGESTÕES ESTATÍSTICAS
    # ---------------------------------------------------------
    st.markdown("### 🧭 Probabilidades Clássicas")
    
    ultima_cor = engine.classificar(ultimo_numero)["Cor"]
    df_markov = engine.cadeias_de_markov(historico)
    cor_atrasada, rodadas_atraso = engine.calcular_maior_atraso(historico)
    
    col_v1, col_v2, col_v3 = st.columns(3)
    
    with col_v1:
        if ultima_cor in df_markov.index:
            prob_prox_verm = df_markov.loc[ultima_cor, "Vermelho"]
            prob_prox_preto = df_markov.loc[ultima_cor, "Preto"]
            cor_sugerida = "Vermelho" if prob_prox_verm > prob_prox_preto else "Preto" if prob_prox_preto > prob_prox_verm else "Indefinido"
            cor_fundo = "#FF4B4B" if cor_sugerida == "Vermelho" else "#262730" if cor_sugerida == "Preto" else "#555555"
            
            st.markdown(f"<div class='radar-box' style='background-color: {cor_fundo};'>1. TENDÊNCIA DE COR<br>Apostar no {cor_sugerida}</div>", unsafe_allow_html=True)
            st.write(f"Sempre que saiu {ultima_cor}, o próximo foi:")
            st.progress(int(prob_prox_verm), text=f"🔴 Vermelho: {prob_prox_verm}%")
            st.progress(int(prob_prox_preto), text=f"⚫ Preto: {prob_prox_preto}%")
    
    with col_v2:
        if rodadas_atraso >= 3:
            st.markdown(f"<div class='radar-box' style='background-color: #FFC107; color: black;'>2. ESTATÍSTICA DE ATRASO<br>Apostar no {cor_atrasada}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='radar-box' style='background-color: #555555;'>2. ESTATÍSTICA DE ATRASO<br>Sem anomalias</div>", unsafe_allow_html=True)

    with col_v3:
        duzias = [engine.classificar(n)["Duzia"] for n in historico if engine.classificar(n)["Duzia"] != "Zero"]
        if duzias:
            duzia_quente = Counter(duzias).most_common(1)[0][0]
            st.markdown(f"<div class='radar-box' style='background-color: #00E676; color: black;'>3. DÚZIA QUENTE<br>Apostar na {duzia_quente}</div>", unsafe_allow_html=True)

    st.divider()

    # ---------------------------------------------------------
    # ABAS DE ESTATÍSTICA PROFUNDA & AUDITORIA
    # ---------------------------------------------------------
    st.markdown("### 📊 Detalhes Técnicos & Auditoria")
    aba1, aba2, aba3 = st.tabs(["Histograma de Saltos (Física)", "Gráfico da Pista", "Mapa de Transição"])
    
    with aba1:
        st.write("Frequência de distâncias que a bola viaja no cilindro entre jogadas consecutivas:")
        if saltos:
            fig_saltos = px.histogram(x=saltos, nbins=37, labels={"x": "Distância (Nº de Casas)", "y": "Vezes que Aconteceu"})
            fig_saltos.update_layout(template="plotly_dark")
            st.plotly_chart(fig_saltos, use_container_width=True)

    with aba2:
        fig_pista = px.pie(names=list(contagem_setores.keys()), values=list(contagem_setores.values()), hole=0.4,
                           color=list(contagem_setores.keys()),
                           color_discrete_map={"Jeu Zéro": "#2ECC40", "Voisins": "#0074D9", "Orphelins": "#FF851B", "Tiers": "#B10DC9"})
        fig_pista.update_layout(template="plotly_dark", title="Dominância de Setores")
        st.plotly_chart(fig_pista, use_container_width=True)

    with aba3:
        if not df_markov.empty:
            fig_heat = px.imshow(df_markov, text_auto=True, color_continuous_scale="Viridis")
            st.plotly_chart(fig_heat, use_container_width=True)
