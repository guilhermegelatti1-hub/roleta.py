import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re

# ==========================================
# 1. MOTOR MEGA ROULETTE
# ==========================================
class MegaRouletteEngine:
    def __init__(self):
        self.RODA = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 
                     5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        
        self.SETORES_PLENOS = {
            "Jeu Zéro": [12, 35, 3, 26, 0, 32, 15],
            "Voisins": [22, 18, 29, 7, 28, 19, 4, 21, 2, 25],
            "Orphelins": [1, 20, 14, 31, 9, 6, 34, 17],
            "Tiers": [27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33]
        }
        self.JEU_ZERO = set(self.SETORES_PLENOS["Jeu Zéro"])
        self.VOISINS = set(self.SETORES_PLENOS["Voisins"])
        self.ORPHELINS = set(self.SETORES_PLENOS["Orphelins"])
        self.TIERS = set(self.SETORES_PLENOS["Tiers"])

    def obter_cor(self, n):
        n = int(n)
        if n == 0: return "Verde"
        vermelhos = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        return "Vermelho" if n in vermelhos else "Preto"

    def classificar_setor_pista(self, n):
        n = int(n)
        if n in self.JEU_ZERO: return "Jeu Zéro"
        if n in self.VOISINS: return "Voisins"
        if n in self.ORPHELINS: return "Orphelins"
        if n in self.TIERS: return "Tiers"
        return "Erro"

    def calcular_saltos(self, historico):
        if len(historico) < 2: return []
        saltos = []
        for i in range(len(historico)-1):
            idx_atual = self.RODA.index(int(historico[i]))
            idx_seguinte = self.RODA.index(int(historico[i+1]))
            saltos.append((idx_seguinte - idx_atual) % 37)
        return saltos

    def projetar_alvo(self, ultimo_numero, salto_predito):
        idx_alvo = (self.RODA.index(int(ultimo_numero)) + salto_predito) % 37
        zona = [self.RODA[(idx_alvo + i) % 37] for i in range(-2, 3)]
        return self.RODA[idx_alvo], zona

# ==========================================
# 2. INICIALIZAÇÃO DA APP E CSS
# ==========================================
st.set_page_config(page_title="Tracker Mega Roulette", layout="wide", initial_sidebar_state="expanded")

engine = MegaRouletteEngine()

if 'historico_quant' not in st.session_state:
    st.session_state.historico_quant = []

st.markdown("""
    <style>
    .mega-box-global { padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%); color: black; text-align: center; font-weight: bold; border: 2px solid white;}
    .mega-box-recente { padding: 25px; border-radius: 15px; background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%); color: white; text-align: center; font-weight: bold; border: 3px solid #FFD700; box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.5);}
    .historico-scroll { max-height: 250px; overflow-y: auto; padding: 15px; background-color: #111111; border-radius: 8px; border: 1px solid #333; font-size: 16px; line-height: 1.8;}
    div[data-testid="stSidebar"] button { font-weight: bold; height: 50px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BARRA LATERAL (ENTRADA DE DADOS)
# ==========================================
def submeter_texto_rapido():
    entrada = st.session_state.input_texto_rapido
    if entrada:
        numeros = re.findall(r'\b([0-9]|[1-2][0-9]|3[0-6])\b', entrada)
        if numeros:
            st.session_state.historico_quant.extend([int(n) for n in numeros])
        st.session_state.input_texto_rapido = "" 

with st.sidebar:
    st.title("⚡ Mega Roulette")
    janela_recente = st.slider("Janela de Tendência Recente", min_value=5, max_value=20, value=10, help="Quantas jogadas atrás queremos analisar para apanhar a tendência atual?")
    st.divider()

    aba_teclado, aba_texto = st.tabs(["🎛️ Teclado Casino", "⌨️ Texto"])
    
    with aba_teclado:
        def add_num(n):
            st.session_state.historico_quant.append(n)
        if st.button("0 🟢", use_container_width=True): add_num(0)
        for row in range(12):
            c1, c2, c3 = st.columns(3)
            n1, n2, n3 = row * 3 + 1, row * 3 + 2, row * 3 + 3
            def btn_label(num): return f"{num} 🔴" if engine.obter_cor(num) == "Vermelho" else f"{num} ⚫"
            with c1: 
                if st.button(btn_label(n1), use_container_width=True, key=f"btn_{n1}"): add_num(n1)
            with c2: 
                if st.button(btn_label(n2), use_container_width=True, key=f"btn_{n2}"): add_num(n2)
            with c3: 
                if st.button(btn_label(n3), use_container_width=True, key=f"btn_{n3}"): add_num(n3)

    with aba_texto:
        st.text_input("Cola os números:", key="input_texto_rapido", on_change=submeter_texto_rapido)

    st.divider()
    
    st.markdown("### 📜 Histórico")
    if len(st.session_state.historico_quant) > 0:
        hist = [f"**{n}**" for n in st.session_state.historico_quant]
        st.markdown(f"<div class='historico-scroll'>{' ➔ '.join(hist)}</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("↩️ Desfazer", use_container_width=True):
                st.session_state.historico_quant.pop()
                st.rerun()
        with col2:
            if st.button("🚨 Limpar Tudo", type="primary", use_container_width=True):
                st.session_state.historico_quant = []
                st.rerun()
    else:
        st.info("Aguardando sorteios...")

# ==========================================
# 4. DASHBOARD (DUPLO MOTOR DE ANÁLISE)
# ==========================================
historico = st.session_state.historico_quant
n_jogadas = len(historico)

st.title("🎯 Radares de Zona")

if n_jogadas < 5:
    st.warning("Insere pelo menos 5 números para iniciar a análise espacial.")
else:
    # Preparação de Dados
    setores_totais = [engine.classificar_setor_pista(n) for n in historico if engine.classificar_setor_pista(n) != "Erro"]
    setores_recentes = setores_totais[-janela_recente:] # SLICING: Pega apenas os últimos X números
    
    col_recente, col_global = st.columns(2)
    
    with col_recente:
        st.markdown("### 🔥 TENDÊNCIA IMEDIATA")
        st.caption(f"Análise das últimas {len(setores_recentes)} jogadas. Ideal para mudanças súbitas do croupier.")
        
        contagem_recente = Counter(setores_recentes)
        if contagem_recente:
            setor_hot_recente = contagem_recente.most_common(1)[0][0]
            prob_recente = (contagem_recente[setor_hot_recente] / len(setores_recentes)) * 100
            nums_recente = engine.SETORES_PLENOS[setor_hot_recente]
            
            st.markdown(f"""
            <div class='mega-box-recente'>
                ALERTA DE ZONA QUENTE: {setor_hot_recente.upper()}<br>
                <i>Caiu aqui {prob_recente:.0f}% das vezes nas últimas jogadas.</i><br><br>
                <h3 style='color: white;'>{nums_recente}</h3>
            </div>
            """, unsafe_allow_html=True)
            
    with col_global:
        st.markdown("### 📊 PANORAMA GLOBAL")
        st.caption(f"Análise das {n_jogadas} jogadas. Mostra a tendência longa da sessão.")
        
        contagem_global = Counter(setores_totais)
        if contagem_global:
            setor_hot_global = contagem_global.most_common(1)[0][0]
            prob_global = (contagem_global[setor_hot_global] / n_jogadas) * 100
            nums_global = engine.SETORES_PLENOS[setor_hot_global]
            
            st.markdown(f"""
            <div class='mega-box-global'>
                ZONA DOMINANTE: {setor_hot_global.upper()}<br>
                <i>Média geral de {prob_global:.0f}%.</i><br><br>
                <h4>{nums_global}</h4>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Gráfico Comparativo
    aba1, aba2 = st.tabs(["Frequência (Últimas Jogadas)", "Frequência (Sessão Inteira)"])
    with aba1:
        fig_rec = px.bar(x=list(contagem_recente.keys()), y=list(contagem_recente.values()), 
                         labels={"x": "Setor", "y": "Ocorrências"}, color_discrete_sequence=["#FFD700"])
        fig_rec.update_layout(template="plotly_dark", title=f"Setores nas últimas {len(setores_recentes)} jogadas")
        st.plotly_chart(fig_rec, use_container_width=True)
        
    with aba2:
        fig_glob = px.pie(names=list(contagem_global.keys()), values=list(contagem_global.values()), hole=0.5)
        fig_glob.update_layout(template="plotly_dark", title="Distribuição Geral da Sessão")
        st.plotly_chart(fig_glob, use_container_width=True)
