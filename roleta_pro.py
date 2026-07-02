import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter
import re
from PIL import Image
import easyocr  # Nova biblioteca de Deep Learning para Visão Computacional

# ==========================================
# 1. MOTOR QUANTITATIVO & FÍSICO
# ==========================================
class RoletaQuantEngine:
    def __init__(self):
        self.RODA = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 
                     5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        self.VERMELHOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
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
            atual, proximo = cores[i], cores[i+1]
            transicoes[atual][proximo] += 1
        df_trans = pd.DataFrame(transicoes).T
        return df_trans.div(df_trans.sum(axis=1), axis=0).fillna(0).round(2) * 100

    def calcular_maior_atraso(self, historico):
        if not historico: return "Nenhum", 0
        cores = [self.classificar(n)["Cor"] for n in historico[::-1]]
        atraso_verm = next((i for i, cor in enumerate(cores) if cor == "Vermelho"), len(cores))
        atraso_preto = next((i for i, cor in enumerate(cores) if cor == "Preto"), len(cores))
        if atraso_verm > atraso_preto: return "Vermelho", atraso_verm
        if atraso_preto > atraso_verm: return "Preto", atraso_preto
        return "Nenhum", 0

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

    def scanner_falha_mecanica(self, historico):
        n = len(historico)
        if n < 37: return 0, False, []
        esperado = n / 37.0
        contagem = Counter(historico)
        qui_quadrado = sum(((contagem.get(num, 0) - esperado) ** 2) / esperado for num in range(37))
        mesa_viciada = qui_quadrado > 50.99
        anomalias = [num for num, qtd in contagem.items() if qtd > esperado * 1.5] if mesa_viciada else []
        return qui_quadrado, mesa_viciada, anomalias

# ==========================================
# 2. INICIALIZAÇÃO E MODELO IA
# ==========================================
st.set_page_config(page_title="Roulette Quant Pro", layout="wide", initial_sidebar_state="expanded")

# Carregar o modelo de Deep Learning em Cache (para não demorar a carregar a cada print)
@st.cache_resource
def load_ocr_model():
    # Carrega o modelo em inglês (suficiente para ler números)
    return easyocr.Reader(['en'], gpu=False) 

reader = load_ocr_model()
engine = RoletaQuantEngine()

if 'historico_quant' not in st.session_state:
    st.session_state.historico_quant = []

st.markdown("""
    <style>
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 8px; border-left: 5px solid #00E676;}
    .radar-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white; text-align: center; font-weight: bold;}
    .pista-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%); color: black; text-align: center; font-weight: bold;}
    .alvo-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #FF4136 0%, #FF851B 100%); color: white; text-align: center; font-weight: bold;}
    .mega-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #8A2BE2 0%, #FF00FF 100%); color: white; text-align: center; font-weight: bold;}
    .historico-scroll { max-height: 300px; overflow-y: auto; padding: 15px; background-color: #111111; border-radius: 8px; border: 1px solid #333; font-size: 16px; line-height: 1.8;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BARRA LATERAL (ENTRADA OCR POR DEEP LEARNING)
# ==========================================
with st.sidebar:
    st.markdown("### 🎮 Modo de Análise")
    modo_jogo = st.radio("Mesa:", ["Clássica (Europeia)", "Mega Roulette"], index=0, label_visibility="collapsed")
    st.divider()

    st.title("📸 Ler Print (EasyOCR)")
    st.info("Faz `Ctrl + V` do recorte da grelha de números.")
    
    imagem_upload = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    if imagem_upload is not None:
        with st.spinner('A analisar imagem com Deep Learning...'):
            try:
                # Converter imagem para formato legível pelo OpenCV/EasyOCR
                imagem = Image.open(imagem_upload).convert('RGB')
                img_array = np.array(imagem)
                
                # O EasyOCR processa a imagem original diretamente, sem precisarmos de inverter cores
                resultados = reader.readtext(img_array)
                
                itens_validos = []
                
                # Passo A: Extração de Dados
                for (bbox, text, conf) in resultados:
                    texto_limpo = re.sub(r'[^0-9]', '', text) # Limpa tudo o que não for número
                    
                    if texto_limpo.isdigit() and conf > 0.4: # Confiança mínima de 40%
                        num = int(texto_limpo)
                        if 0 <= num <= 36: # Ignora multiplicadores como 50 ou 200
                            # Calcula o centro da caixa delimitadora do número (Centro Y e Centro X)
                            centro_x = (bbox[0][0] + bbox[1][0]) / 2
                            centro_y = (bbox[0][1] + bbox[2][1]) / 2
                            
                            itens_validos.append({'num': num, 'x': centro_x, 'y': centro_y})

                numeros_limpos = []
                
                # Passo B: Algoritmo de Agrupamento Geométrico
                if itens_validos:
                    # 1. Ordena todos os números de cima para baixo
                    itens_validos.sort(key=lambda item: item['y'])
                    
                    linhas = []
                    linha_atual = []
                    y_referencia = None
                    
                    # 2. Agrupa os números que partilham a mesma linha física
                    for item in itens_validos:
                        if y_referencia is None:
                            linha_atual.append(item)
                            y_referencia = item['y']
                        # Se o centro do número estiver num raio de 25 píxeis de altura, é da mesma linha
                        elif abs(item['y'] - y_referencia) < 25: 
                            linha_atual.append(item)
                        else:
                            linhas.append(linha_atual)
                            linha_atual = [item]
                            y_referencia = item['y']
                    if linha_atual:
                        linhas.append(linha_atual)
                        
                    # 3. Ordena os números de cada linha da Esquerda para a Direita
                    for linha in linhas:
                        linha.sort(key=lambda item: item['x'])
                        for item in linha:
                            numeros_limpos.append(item['num'])
                
                if numeros_limpos:
                    st.success(f"Lidos {len(numeros_limpos)} números.")
                    st.info(str(numeros_limpos))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Injetar", use_container_width=True):
                            st.session_state.historico_quant.extend(numeros_limpos)
                            st.rerun()
                    with col2:
                        if st.button("🔄 Inverter", use_container_width=True):
                            st.session_state.historico_quant.extend(reversed(numeros_limpos))
                            st.rerun()
                else:
                    st.error("A IA não detetou números de 0 a 36.")
            except Exception as e:
                st.error(f"Erro no processamento: {e}")

    st.divider()
    
    st.markdown("### 📜 Histórico")
    historico = st.session_state.historico_quant
    if len(historico) > 0:
        texto_hist = " ➔ ".join([f"**{n}** {'🔴' if engine.classificar(n)['Cor']=='Vermelho' else '⚫' if engine.classificar(n)['Cor']=='Preto' else '🟢'}" for n in historico])
        st.markdown(f"<div class='historico-scroll'>{texto_hist}</div>", unsafe_allow_html=True)
        st.caption(f"Total: {len(historico)} jogadas")
        
        col_limpar1, col_limpar2 = st.columns(2)
        with col_limpar1:
            if st.button("↩️ Apagar Último"):
                st.session_state.historico_quant.pop()
                st.rerun()
        with col_limpar2:
            if st.button("🚨 Limpar Tudo"):
                st.session_state.historico_quant = []
                st.rerun()
    else:
        st.info("Nenhum número registado.")

# ==========================================
# 4. DASHBOARD VISUAL
# ==========================================
n_jogadas = len(historico)
LIMITE_CALIBRACAO = 25 

st.title("🎯 Radar de IA")

if n_jogadas < LIMITE_CALIBRACAO:
    st.warning("⚠️ Calibrando...")
    st.progress(int((n_jogadas / LIMITE_CALIBRACAO) * 100), text=f"{n_jogadas}/{LIMITE_CALIBRACAO} jogadas")
else:
    st.success(f"✅ Mesa Calibrada. Análise de {n_jogadas} jogadas contínuas.")
    
    qui_quadrado, mesa_viciada, anomalias = engine.scanner_falha_mecanica(historico)
    if mesa_viciada:
        st.error(f"🚨 FALHA FÍSICA DETETADA. APOSTE EM: {anomalias}")
    else:
        st.info(f"Integridade da Mesa: Saudável (Qui-Quadrado: {qui_quadrado:.1f}/50.99)")

    if modo_jogo == "Mega Roulette":
        st.markdown("### ⚡ Cobertura Mega Roulette")
        setores = [engine.classificar_setor_pista(n) for n in historico]
        contagem = Counter([s for s in setores if s != "Erro"])
        if contagem:
            setor_quente = contagem.most_common(1)[0][0]
            numeros_aposta = engine.SETORES_PLENOS[setor_quente]
            st.markdown(f"<div class='mega-box'>🔥 ZONA MULTIPLICADOR: {setor_quente.upper()}<br><b>Fichas Plenas em: {numeros_aposta}</b></div>", unsafe_allow_html=True)
            
    else:
        st.markdown("### 🕵️‍♂️ Assinatura do Croupier")
        saltos = engine.calcular_saltos(historico)
        if saltos:
            distancia_padrao = Counter(saltos).most_common(1)[0][0]
            confianca_zona = (sum(1 for s in saltos if min(abs(s - distancia_padrao), 37 - abs(s - distancia_padrao)) <= 2) / len(saltos)) * 100
            
            c1, c2 = st.columns([1, 2])
            if confianca_zona < 25.0:
                c1.metric("Distância Padrão", "Falhou")
                c2.error("❌ CRUPIÊ ERRÁTICO")
            else:
                alvo, zona = engine.projetar_alvo(historico[-1], distancia_padrao)
                c1.metric("Lançamento", f"+{distancia_padrao}", f"{confianca_zona:.1f}% precisão")
                c2.markdown(f"<div class='alvo-box'>🎯 ALVO: {alvo}<br>Cobrir: {zona}</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("### 🧭 Radar Estatístico")
        df_markov = engine.cadeias_de_markov(historico)
        ultima_cor = engine.classificar(historico[-1])["Cor"]
        
        if ultima_cor in df_markov.index:
            pv, pp = df_markov.loc[ultima_cor, "Vermelho"], df_markov.loc[ultima_cor, "Preto"]
            sugerida = "Vermelho" if pv > pp else "Preto" if pp > pv else "Nenhuma"
            st.markdown(f"<div class='radar-box' style='background-color: {'#FF4B4B' if sugerida=='Vermelho' else '#262730'};'>1. MARKOV: Apostar no {sugerida}</div>", unsafe_allow_html=True)
            
    st.divider()
    st.markdown("### 📊 Auditoria Quantitativa")
    aba1, aba2, aba3 = st.tabs(["Física (Saltos)", "Pista", "Transições"])
    with aba1:
        if 'saltos' in locals() and saltos:
            st.plotly_chart(px.histogram(x=saltos, nbins=37, title="Perfil Físico"), use_container_width=True)
    with aba2:
        if 'contagem' in locals() and contagem:
            st.plotly_chart(px.pie(names=list(contagem.keys()), values=list(contagem.values()), hole=0.4), use_container_width=True)
    with aba3:
        if 'df_markov' in locals() and not df_markov.empty:
            st.plotly_chart(px.imshow(df_markov, text_auto=True), use_container_width=True)
