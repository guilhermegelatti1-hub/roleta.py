import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter
import re

# ==========================================
# 1. MOTOR MEGA ROULETTE (Com Previsão Algorítmica)
# ==========================================
class MegaRouletteEngine:
    def __init__(self):
        # A ordem física exata da roleta
        self.RODA = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 
                     5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        
        # Mapeamento da roleta nos 4 lados principais
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
        """Identifica em qual dos 4 lados da roleta o número se encontra"""
        n = int(n)
        if n in self.JEU_ZERO: return "Jeu Zéro"
        if n in self.VOISINS: return "Voisins"
        if n in self.ORPHELINS: return "Orphelins"
        if n in self.TIERS: return "Tiers"
        return "Erro"

    def obter_zona_vizinhos(self, n):
        """Retorna o número e os seus 2 vizinhos de cada lado (zona de 5 números)"""
        n = int(n)
        if n not in self.RODA: return []
        idx = self.RODA.index(n)
        return [self.RODA[(idx + i) % 37] for i in range(-2, 3)]

    def prever_proxima_jogada(self, historico):
        """
        Identifica os números e setores para definir uma jogada preditiva com 2 vizinhos.
        Lógica extraída da análise de padrões da roda.
        """
        if len(historico) < 5:
            return None, None, []
            
        # 1. Identificar os setores do histórico recente
        setores = [self.classificar_setor_pista(n) for n in historico if self.classificar_setor_pista(n) != "Erro"]
        if not setores:
            return None, None, []
            
        # 2. Descobrir qual é o Setor/Tier que está a favorecer
        setor_alvo = Counter(setores).most_common(1)[0][0]
        
        # 3. Filtrar apenas os números que saíram DENTRO desse setor alvo
        numeros_no_setor = [n for n in historico if self.classificar_setor_pista(n) == setor_alvo]
        
        # 4. Encontrar o número mais repetido desse setor (o nosso "epicentro")
        if numeros_no_setor:
            numero_epicentro = Counter(numeros_no_setor).most_common(1)[0][0]
        else:
            numero_epicentro = historico[-1] # Fallback de segurança
            
        # 5. Definir a jogada com o número alvo + 2 vizinhos físicos
        jogada_preditiva = self.obter_zona_vizinhos(numero_epicentro)
        
        return setor_alvo, numero_epicentro, jogada_preditiva

# ==========================================
# 2. INICIALIZAÇÃO DA APP E CSS
# ==========================================
st.set_page_config(page_title="Tracker Mega Roulette", layout="wide", initial_sidebar_state="expanded")

engine = MegaRouletteEngine()

# Inicializa o histórico na memória da sessão
if 'historico_quant' not in st.session_state:
    st.session_state.historico_quant = []

# Estilos Visuais para as Caixas
st.markdown("""
    <style>
    .mega-box-global { padding: 20px; border-radius: 10px; background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%); color: black; text-align: center; font-weight: bold; border: 2px solid white;}
    .mega-box-recente { padding: 25px; border-radius: 15px; background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%); color: white; text-align: center; font-weight: bold; border: 3px solid #FFD700; box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.5);}
    .historico-scroll { max-height: 250px; overflow-y: auto; padding: 15px; background-color: #111111; border-radius: 8px; border: 1px solid #333; font-size: 16px; line-height: 1.8;}
    div[data-testid="stSidebar"] button { font-weight: bold; height: 50px; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BARRA LATERAL (ENTRADA DE DADOS E CONTROLOS)
# ==========================================
def submeter_texto_rapido():
    entrada = st.session_state.input_texto_rapido
    if entrada:
        numeros = re.findall(r'\b([0-9]|[1-2][0-9]|3[0-6])\b', entrada)
        if numeros:
            st.session_state.historico_quant.extend([int(n) for n in numeros])
            # Mantemos o limite de segurança de 500
            if len(st.session_state.historico_quant) > 500:
                st.session_state.historico_quant = st.session_state.historico_quant[-500:]
        st.session_state.input_texto_rapido = "" 

with st.sidebar:
    st.title("⚡ Mega Roulette")
    st.write("📈 **Parâmetros de Análise:**")
    
    # Sliders dinâmicos para controlo de janelas de histórico
    janela_global = st.slider("Tamanho do Histórico Global", min_value=10, max_value=100, value=20, help="Quantas jogadas analisar para ver os 4 lados (recomendado: 20).")
    janela_recente = st.slider("Tamanho do Ciclo Curto", min_value=3, max_value=15, value=5, help="Quantos números usar para procurar o ciclo e fazer a previsão.")
    
    st.divider()

    aba_teclado, aba_texto = st.tabs(["🎛️ Teclado", "⌨️ Texto"])
    
    with aba_teclado:
        def add_num(n):
            st.session_state.historico_quant.append(n)
            if len(st.session_state.historico_quant) > 500:
                st.session_state.historico_quant = st.session_state.historico_quant[-500:]

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
        st.caption(f"Registados: {len(st.session_state.historico_quant)} jogadas")
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
# 4. DASHBOARD (ANÁLISE E PREVISÃO)
# ==========================================
historico_completo = st.session_state.historico_quant
n_jogadas = len(historico_completo)

st.title("🎯 Radares de Zona e Previsão")

if n_jogadas < 5:
    st.warning("Insere pelo menos 5 números para iniciar a análise de previsão.")
else:
    # Preparação das listas fatiadas baseadas nos sliders
    historico_global_atual = historico_completo[-janela_global:]
    setores_global = [engine.classificar_setor_pista(n) for n in historico_global_atual if engine.classificar_setor_pista(n) != "Erro"]
    
    historico_recente = historico_completo[-janela_recente:]
    
    col_recente, col_global = st.columns(2)
    
    with col_recente:
        st.markdown("### 🔮 PREVISÃO ALGORÍTMICA")
        st.caption(f"Baseado na tendência das últimas {len(historico_recente)} jogadas.")
        
        # O Motor corre a lógica de previsão com base na janela recente
        setor_alvo, epicentro, jogada_preditiva = engine.prever_proxima_jogada(historico_recente)
        
        if setor_alvo and jogada_preditiva:
            st.markdown(f"""
            <div class='mega-box-recente'>
                ALVO DO SISTEMA: {setor_alvo.upper()}<br>
                <i>O padrão favorece o número {epicentro}. Cobre o epicentro + 2 vizinhos.</i><br><br>
                <h3 style='color: white;'>{jogada_preditiva}</h3>
                <p style='color: #FFD700; font-size: 14px;'>Custo da ronda: 5 fichas</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("A aguardar dados suficientes no ciclo curto para previsão.")
            
    with col_global:
        st.markdown("### 📊 ZONA DOMINANTE (4 LADOS)")
        st.caption(f"Análise focada nos últimos {len(historico_global_atual)} números registados.")
        
        contagem_global = Counter(setores_global)
        if contagem_global:
            setor_hot_global = contagem_global.most_common(1)[0][0]
            prob_global = (contagem_global[setor_hot_global] / len(setores_global)) * 100
            nums_global = engine.SETORES_PLENOS[setor_hot_global]
            
            st.markdown(f"""
            <div class='mega-box-global'>
                O LADO MAIS QUENTE DA MESA: {setor_hot_global.upper()}<br>
                <i>Caiu neste quadrante {prob_global:.0f}% das vezes (amostra de {len(historico_global_atual)}).</i><br><br>
                <h4>{nums_global}</h4>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Gráficos e Auditoria Visual
    aba1, aba2 = st.tabs([f"Estatística dos 4 Lados (Últimos {len(historico_global_atual)})", "Histórico de Repetição de Lados"])
    
    with aba1:
        if contagem_global:
            fig_glob = px.pie(names=list(contagem_global.keys()), values=list(contagem_global.values()), hole=0.5,
                              color_discrete_sequence=["#FF851B", "#0074D9", "#2ECC40", "#B10DC9"])
            fig_glob.update_layout(template="plotly_dark", title=f"Distribuição da Roda (Janela de {len(historico_global_atual)})")
            st.plotly_chart(fig_glob, use_container_width=True)
        else:
            st.write("Sem dados suficientes para o gráfico.")
            
    with aba2:
        if setores_global:
            st.write("Mapa em tempo real das quedas de bola, classificado pelos 4 grandes setores da roda.")
            df_setores = pd.DataFrame({"Jogada": range(1, len(setores_global) + 1), "Lado da Roleta": setores_global})
            fig_linha = px.scatter(df_setores, x="Jogada", y="Lado da Roleta", color="Lado da Roleta")
            fig_linha.update_layout(template="plotly_dark", title="Mapa de Calor de Repetição")
            st.plotly_chart(fig_linha, use_container_width=True)
        else:
            st.write("Sem dados suficientes para o gráfico.")
