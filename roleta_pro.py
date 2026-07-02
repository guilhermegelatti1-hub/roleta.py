import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import math
import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import re

# ==========================================
# 1. MOTOR QUANTITATIVO & FÍSICO (OOP)
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

    def calcular_saltos(self, historico):
        if len(historico) < 2: return []
        saltos = []
        for i in range(len(historico)-1):
            idx_atual = self.RODA.index(int(historico[i]))
            idx_seguinte = self.RODA.index(int(historico[i+1]))
            saltos.append((idx_seguinte - idx_atual) % 37)
        return saltos

    def projetar_alvo(self, ultimo_numero, salto_predito):
        idx_atual = self.RODA.index(int(ultimo_numero))
        idx_alvo = (idx_atual + salto_predito) % 37
        alvo_principal = self.RODA[idx_alvo]
        zona = [self.RODA[(idx_alvo + i) % 37] for i in range(-2, 3)]
        return alvo_principal, zona

    def scanner_falha_mecanica(self, historico):
        n = len(historico)
        if n < 37: return 0, False, []
        esperado = n / 37.0
        contagem = Counter(historico)
        qui_quadrado = 0
        for num in range(37):
            observado = contagem.get(num, 0)
            qui_quadrado += ((observado - esperado) ** 2) / esperado
        mesa_viciada = qui_quadrado > 50.99
        anomalias = []
        if mesa_viciada:
            anomalias = [num for num, qtd in contagem.items() if qtd > esperado * 1.5]
        return qui_quadrado, mesa_viciada, anomalias

# ==========================================
# 2. INICIALIZAÇÃO DA APP
# ==========================================
st.set_page_config(page_title="Roulette Quant Pro", layout="wide", page_icon="📉", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 8px; border-left: 5px solid #00E676;}
    .radar-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white; text-align: center; font-weight: bold;}
    .pista-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%); color: black; text-align: center; font-weight: bold; border: 2px solid white;}
    .alvo-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #FF4136 0%, #FF851B 100%); color: white; text-align: center; font-weight: bold; border: 2px solid white;}
    .mega-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #8A2BE2 0%, #FF00FF 100%); color: white; text-align: center; font-weight: bold; border: 2px solid #FFD700;}
    .erratico-box { padding: 20px; border-radius: 15px; background-color: #333333; color: #aaaaaa; text-align: center; border: 1px dashed #777;}
    .vicio-box { padding: 25px; border-radius: 15px; background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%); color: white; text-align: center; font-weight: bold; border: 3px dashed yellow; animation: blinker 2s linear infinite;}
    .historico-scroll { max-height: 300px; overflow-y: auto; padding: 15px; background-color: #111111; border-radius: 8px; border: 1px solid #333; font-size: 16px; line-height: 1.8;}
    </style>
    """, unsafe_allow_html=True)

if 'historico_quant' not in st.session_state:
    st.session_state.historico_quant = []

engine = RoletaQuantEngine()

# ==========================================
# 3. BARRA LATERAL (ENTRADAS OTIMIZADAS)
# ==========================================

# Nova função ultra-rápida para texto limpo (Aceita 1 número ou vários)
def submeter_texto_rapido():
    entrada = st.session_state.input_texto_rapido
    if entrada:
        # Extrai todos os números válidos (0-36) da string digitada
        numeros = re.findall(r'\b([0-9]|[1-2][0-9]|3[0-6])\b', entrada)
        if numeros:
            st.session_state.historico_quant.extend([int(n) for n in numeros])
        st.session_state.input_texto_rapido = "" # Limpa a caixa

with st.sidebar:
    st.markdown("### 🎮 Modo de Análise")
    modo_jogo = st.radio("Escolhe a tua mesa:", ["Clássica (Europeia/Francesa)", "Mega Roulette (Multiplicadores)"], index=0, label_visibility="collapsed")
    st.divider()

    st.title("⚙️ Inserir Dados")
    
    aba_ocr, aba_texto = st.tabs(["📸 Colar Print", "⌨️ Digitação Rápida"])
    
    with aba_ocr:
        st.info("**Instruções:** Usa o `Windows + Shift + S`. Recorta apenas a grelha dos números. Clica na caixa abaixo e dá `Ctrl + V`.")
        imagem_upload = st.file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        
        if imagem_upload is not None:
            try:
                imagem = Image.open(imagem_upload).convert('RGB')
                
                # --- NOVO FILTRO DE RAIO-X PARA NEON/CASSINO ---
                # 1. Upscale brutal
                imagem = imagem.resize((imagem.width * 3, imagem.height * 3), Image.Resampling.LANCZOS)
                # 2. Aumentar contraste das cores antes de remover a cor
                imagem = ImageEnhance.Contrast(imagem).enhance(3.0)
                # 3. Tons de Cinza
                img_gray = imagem.convert('L')
                # 4. Binarização Extrema (Força os números brilhantes a ficarem brancos puros e o fundo preto)
                limite = 100
                img_bin = img_gray.point(lambda p: 255 if p > limite else 0)
                # 5. Inverter (Tesseract adora fundo branco com letras pretas)
                img_final = ImageOps.invert(img_bin)
                
                # MOSTRAR AO UTILIZADOR COMO A IA ESTÁ A VER O ECRÃ
                st.image(img_final, caption="Visão Raio-X da Inteligência Artificial", use_container_width=True)
                
                # Leitura focada em blocos de texto (PSM 6)
                config_tesseract = r'--psm 6 -c tessedit_char_whitelist=0123456789'
                texto_bruto = pytesseract.image_to_string(img_final, config=config_tesseract)
                
                # Ignora Multiplicadores gigantes (ex: 200x) porque só aceita de 0 a 36!
                numeros_detectados = re.findall(r'\b([0-9]|[1-2][0-9]|3[0-6])\b', texto_bruto)
                numeros_limpos = [int(n) for n in numeros_detectados]
                
                if numeros_limpos:
                    st.success(f"**Apanhei {len(numeros_limpos)} números!**")
                    st.info(f"{numeros_limpos}")
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("✅ Injetar Direto", use_container_width=True):
                            st.session_state.historico_quant.extend(numeros_limpos)
                            st.rerun()
                    with col_b2:
                        if st.button("🔄 Inverter Ordem", help="Usa isto se a grelha ler os números de trás para a frente", use_container_width=True):
                            st.session_state.historico_quant.extend(reversed(numeros_limpos))
                            st.rerun()
                else:
                    st.error("Falha na leitura. O print tem texto a mais misturado (chat, caras)?")
            except Exception as e:
                st.error("Erro interno. Tenta fazer o recorte apenas da tabela.")

    with aba_texto:
        st.write("Sem bugs. Digita 1 número e dá Enter, ou vários separados por espaço (ex: `12 5 36 0`).")
        # Substituí o number_input bugado por um text_input fluido
        st.text_input("Números:", key="input_texto_rapido", on_change=submeter_texto_rapido)

    st.divider()
    
    st.markdown("### 📜 Histórico da Sessão")
    historico_atual = st.session_state.historico_quant
    
    if len(historico_atual) > 0:
        hist_formatado = []
        for n in historico_atual:
            cor = engine.classificar(n)["Cor"]
            emoji = "🔴" if cor == "Vermelho" else "⚫" if cor == "Preto" else "🟢"
            hist_formatado.append(f"**{n}** {emoji}")
            
        texto_historico = " ➔ ".join(hist_formatado)
        st.markdown(f"<div class='historico-scroll'>{texto_historico}</div>", unsafe_allow_html=True)
        st.caption(f"Total digitado: {len(historico_atual)} jogadas")
    else:
        st.info("Nenhum número registado.")
        
    st.divider()
    if st.button("🚨 Limpar Sessão", type="primary", use_container_width=True):
        st.session_state.historico_quant = []
        st.rerun()

# ==========================================
# 4. DASHBOARD VISUAL (DINÂMICO)
# ==========================================
historico = st.session_state.historico_quant
n_jogadas = len(historico)
LIMITE_CALIBRACAO = 25 

st.title("🎯 Radar de IA com Adaptação a Falhas")

if n_jogadas < LIMITE_CALIBRACAO:
    st.warning("⚠️ A recolher dados da física e mecânica da mesa.")
    st.markdown(f"### Calibrando: {n_jogadas} / {LIMITE_CALIBRACAO} jogadas")
    progresso = int((n_jogadas / LIMITE_CALIBRACAO) * 100)
    st.progress(progresso, text=f"{progresso}% concluído")
else:
    st.success(f"✅ Mesa Calibrada. {n_jogadas} jogadas em análise contínua.")
    
    qui_quadrado, mesa_viciada, anomalias = engine.scanner_falha_mecanica(historico)
    
    if mesa_viciada:
        st.markdown(f"""
        <div class='vicio-box'>
            🚨 ALERTA MÁXIMO: FALHA FÍSICA DETETADA NA MESA 🚨<br><br>
            O teste Qui-Quadrado (Score: {qui_quadrado:.1f}) indica que esta roleta está viciada.<br>
            APOSTE EXCLUSIVAMENTE NOS NÚMEROS COM DEFEITO: {anomalias}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(f"Integridade da Mesa: Nível Saudável (Qui-Quadrado: {qui_quadrado:.1f}/50.99).")

    # ==========================================
    # RAMIFICAÇÃO: MODO CLÁSSICO vs MODO MEGA
    # ==========================================
    if modo_jogo == "Mega Roulette (Multiplicadores)":
        st.markdown("### ⚡ Estratégia de Cobertura Mega Roulette")
        st.write("Atenção: Para ganhares os multiplicadores, tens de fazer **Apostas Plenas (Straight Up)** nestes números. Evita apostas exteriores (Cores/Dúzias).")
        
        setores = [engine.classificar_setor_pista(n) for n in historico]
        contagem_setores = Counter(setores)
        
        if "Erro" in contagem_setores:
            del contagem_setores["Erro"]
            
        if contagem_setores:
            setor_quente = contagem_setores.most_common(1)[0][0]
            numeros_para_apostar = engine.SETORES_PLENOS[setor_quente]
            custo_fichas = len(numeros_para_apostar)
            prob_real = (contagem_setores[setor_quente] / n_jogadas) * 100
            
            st.markdown(f"""
            <div class='mega-box'>
                🔥 ZONA DE CAPTURA DO MULTIPLICADOR: {setor_quente.upper()} 🔥<br>
                A bola está a cair aqui {prob_real:.1f}% das vezes.<br><br>
                <b>Coloca 1 ficha Plena em cada um destes números:</b><br>
                <h2>{numeros_para_apostar}</h2>
                <i>Custo total da ronda: {custo_fichas} fichas</i>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Dados insuficientes para calcular o setor Mega.")
            
        st.divider()
        st.markdown("*(No Modo Mega, o Radar de Cores e Dúzias é desativado para focar na captura de multiplicadores)*")

    else:
        # MODO CLÁSSICO
        st.markdown("### 🕵️‍♂️ Assinatura do Croupier (Memória Muscular)")
        
        saltos = engine.calcular_saltos(historico)
        if saltos:
            contagem_saltos = Counter(saltos)
            salto_mais_comum = contagem_saltos.most_common(1)[0]
            distancia_padrao = salto_mais_comum[0]
            
            saltos_na_zona = sum(1 for s in saltos if min(abs(s - distancia_padrao), 37 - abs(s - distancia_padrao)) <= 2)
            confianca_zona = (saltos_na_zona / len(saltos)) * 100
            
            col_f1, col_f2 = st.columns([1, 2])
            
            if confianca_zona < 25.0:
                with col_f1:
                    st.metric("Distância Padrão", "Falhou", "Dispersão Elevada")
                with col_f2:
                    st.markdown("<div class='erratico-box'>❌ CRUPIÊ ERRÁTICO ❌<br>A força de lançamento varia demasiado.</div>", unsafe_allow_html=True)
            else:
                alvo, zona = engine.projetar_alvo(historico[-1], distancia_padrao)
                with col_f1:
                    st.metric("Distância Padrão de Lançamento", f"+{distancia_padrao} casas", f"Zona atinge {confianca_zona:.1f}% de precisão")
                with col_f2:
                    st.markdown(f"<div class='alvo-box'>🎯 ALVO FÍSICO PROJETADO: NÚMERO {alvo}<br>Cobrir a zona de queda: {zona}</div>", unsafe_allow_html=True)

        st.divider()

        st.markdown("### 🏎️ Análise da Pista (Racetrack)")
        setores = [engine.classificar_setor_pista(n) for n in historico]
        contagem_setores = Counter(setores)
        max_ocorrencias = max(contagem_setores.values())
        setores_quentes = [setor for setor, qtd in contagem_setores.items() if qtd == max_ocorrencias]
        
        nome_setor_display = "EMPATE: " + " / ".join(setores_quentes) if len(setores_quentes) > 1 else setores_quentes[0]
        prob_real = (max_ocorrencias / n_jogadas) * 100
        st.markdown(f"<div class='pista-box'>🔥 ZONA FÍSICA MAIS QUENTE: {nome_setor_display.upper()} 🔥<br>Absorveu {max_ocorrencias} bolas ({prob_real:.1f}%)</div>", unsafe_allow_html=True)

        st.divider()

        st.markdown("### 🧭 Radar Estatístico Secundário")
        ultima_cor = engine.classificar(historico[-1])["Cor"]
        df_markov = engine.cadeias_de_markov(historico)
        cor_atrasada, rodadas_atraso = engine.calcular_maior_atraso(historico)
        
        col_v1, col_v2, col_v3 = st.columns(3)
        
        with col_v1:
            if ultima_cor in df_markov.index:
                prob_prox_verm = df_markov.loc[ultima_cor, "Vermelho"]
                prob_prox_preto = df_markov.loc[ultima_cor, "Preto"]
                cor_sugerida = "Vermelho" if prob_prox_verm > prob_prox_preto else "Preto" if prob_prox_preto > prob_prox_verm else "Indefinido"
                cor_fundo = "#FF4B4B" if cor_sugerida == "Vermelho" else "#262730" if cor_sugerida == "Preto" else "#555555"
                st.markdown(f"<div class='radar-box' style='background-color: {cor_fundo};'>1. CADEIA DE MARKOV<br>Apostar no {cor_sugerida}</div>", unsafe_allow_html=True)
                st.progress(int(prob_prox_verm), text=f"🔴 Vermelho: {prob_prox_verm}%")
                st.progress(int(prob_prox_preto), text=f"⚫ Preto: {prob_prox_preto}%")
        
        with col_v2:
            if rodadas_atraso >= 3:
                st.markdown(f"<div class='radar-box' style='background-color: #FFC107; color: black;'>2. PRESSÃO MATEMÁTICA<br>Apostar no {cor_atrasada}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='radar-box' style='background-color: #555555;'>2. PRESSÃO MATEMÁTICA<br>Mesa Equilibrada</div>", unsafe_allow_html=True)

        with col_v3:
            duzias = [engine.classificar(n)["Duzia"] for n in historico if engine.classificar(n)["Duzia"] != "Zero"]
            if duzias:
                duzia_quente = Counter(duzias).most_common(1)[0][0]
                st.markdown(f"<div class='radar-box' style='background-color: #00E676; color: black;'>3. ZONA CONTÍNUA<br>Apostar na {duzia_quente}</div>", unsafe_allow_html=True)

    # ==========================================
    # ABAS DE AUDITORIA 
    # ==========================================
    st.divider()
    st.markdown("### 📊 Auditoria Quantitativa")
    aba1, aba2, aba3 = st.tabs(["Física (Histograma de Saltos)", "Cilindro (Racetrack)", "Transição de Probabilidade"])
    
    with aba1:
        saltos = engine.calcular_saltos(historico)
        if saltos:
            fig_saltos = px.histogram(x=saltos, nbins=37, labels={"x": "Distância de Salto (Casas)", "y": "Frequência"})
            fig_saltos.update_layout(template="plotly_dark", title="Perfil Físico de Lançamento do Croupier")
            st.plotly_chart(fig_saltos, use_container_width=True)

    with aba2:
        setores = [engine.classificar_setor_pista(n) for n in historico]
        contagem_setores = Counter(setores)
        fig_pista = px.pie(names=list(contagem_setores.keys()), values=list(contagem_setores.values()), hole=0.4,
                           color=list(contagem_setores.keys()),
                           color_discrete_map={"Jeu Zéro": "#2ECC40", "Voisins": "#0074D9", "Orphelins": "#FF851B", "Tiers": "#B10DC9"})
        fig_pista.update_layout(template="plotly_dark", title="Frequência Real de Queda por Setor")
        st.plotly_chart(fig_pista, use_container_width=True)

    with aba3:
        df_markov = engine.cadeias_de_markov(historico)
        if not df_markov.empty:
            fig_heat = px.imshow(df_markov, text_auto=True, color_continuous_scale="Viridis", title="Mapa Térmico de Mudança de Cor")
            st.plotly_chart(fig_heat, use_container_width=True)
