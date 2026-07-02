import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from collections import Counter
import re
from PIL import Image
import easyocr

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
# 2. INICIALIZAÇÃO DA APP
# ==========================================
st.set_page_config(page_title="Roulette Quant Pro", layout="wide", initial_sidebar_state="expanded")

@st.cache_resource
def load_ocr_model():
    return easyocr.Reader(['en'], gpu=False) 

reader = load_ocr_model()
engine = RoletaQuantEngine()

if 'historico_quant' not in st.session_state:
    st.session_state.historico_quant = []
    
if 'ocr_texto_bruto' not in st.session_state:
    st.session_state.ocr_texto_bruto = ""

st.markdown("""
    <style>
    .stMetric { background-color: #1E1E1E; padding: 15px; border-radius: 8px; border-left: 5px solid #00E676;}
    .radar-box { padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white; text-align: center; font-weight: bold;}
    .pista-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #1f4037 0%, #99f2c8 100%); color: black; text-align: center; font-weight: bold;}
    .alvo-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #FF4136 0%, #FF851B 100%); color: white; text-align: center; font-weight: bold;}
    .mega-box { padding: 20px; border-radius: 15px; background: linear-gradient(135deg, #8A2BE2 0%, #FF00FF 100%); color: white; text-align: center; font-weight: bold;}
    .erratico-box { padding: 20px; border-radius: 15px; background-color: #333333; color: #aaaaaa; text-align: center; border: 1px dashed #777;}
    .vicio-box { padding: 25px; border-radius: 15px; background: linear-gradient(135deg, #FF0000 0%, #8B0000 100%); color: white; text-align: center; font-weight: bold; border: 3px dashed yellow; animation: blinker 2s linear infinite;}
    .historico-scroll { max-height: 300px; overflow-y: auto; padding: 15px; background-color: #111111; border-radius: 8px; border: 1px solid #333; font-size: 16px; line-height: 1.8;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. BARRA LATERAL 
# ==========================================
def submeter_texto_rapido():
    entrada = st.session_state.input_texto_rapido
    if entrada:
        numeros = re.findall(r'\b([0-9]|[1-2][0-9]|3[0-6])\b', entrada)
        if numeros:
            st.session_state.historico_quant.extend([int(n) for n in numeros])
        st.session_state.input_texto_rapido = "" 

with st.sidebar:
    st.markdown("### 🎮 Modo de Análise")
    modo_jogo = st.radio("Mesa:", ["Clássica (Europeia/Francesa)", "Mega Roulette"], index=0, label_visibility="collapsed")
    st.divider()

    st.title("⚙️ Inserir Dados")
    aba_ocr, aba_teclado, aba_texto = st.tabs(["📸 OCR Editável", "🎛️ Teclado", "⌨️ Digitar"])
    
    # ---------------------------------------------------------
    # A SOLUÇÃO: OCR COM INTERCEÇÃO HUMANA
    # ---------------------------------------------------------
    with aba_ocr:
        st.info("Faz `Ctrl + V` da grelha.")
        imagem_upload = st.file_uploader("Upload", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        
        if imagem_upload is not None:
            if st.button("🔍 Extrair Números com IA", use_container_width=True):
                with st.spinner('A decifrar o ecrã do casino...'):
                    try:
                        img_array = np.array(Image.open(imagem_upload).convert('RGB'))
                        resultados = reader.readtext(img_array)
                        
                        itens_validos = []
                        for (bbox, text, conf) in resultados:
                            texto_limpo = re.sub(r'[^0-9]', '', text)
                            if texto_limpo.isdigit() and conf > 0.3:
                                num = int(texto_limpo)
                                if 0 <= num <= 36:
                                    centro_x = (bbox[0][0] + bbox[1][0]) / 2
                                    centro_y = (bbox[0][1] + bbox[2][1]) / 2
                                    itens_validos.append({'num': num, 'x': centro_x, 'y': centro_y})
                        
                        numeros_limpos = []
                        if itens_validos:
                            itens_validos.sort(key=lambda item: item['y'])
                            linhas, linha_atual, y_referencia = [], [], None
                            for item in itens_validos:
                                if y_referencia is None:
                                    linha_atual.append(item)
                                    y_referencia = item['y']
                                elif abs(item['y'] - y_referencia) < 30: 
                                    linha_atual.append(item)
                                else:
                                    linhas.append(linha_atual)
                                    linha_atual = [item]
                                    y_referencia = item['y']
                            if linha_atual: linhas.append(linha_atual)
                                
                            for linha in linhas:
                                linha.sort(key=lambda item: item['x'])
                                for item in linha:
                                    numeros_limpos.append(item['num'])
                        
                        # Guardar resultado imperfeito numa variável para ser editada
                        st.session_state.ocr_texto_bruto = " ".join(map(str, numeros_limpos))
                    except Exception as e:
                        st.error("Erro no processamento da imagem.")

        # A CAIXA MÁGICA DE REVISÃO (Aparece se houver texto guardado)
        if st.session_state.ocr_texto_bruto:
            st.warning("⚠️ Os multiplicadores baralham a IA. Corrige os números que faltam abaixo antes de confirmar:")
            texto_editado = st.text_input("Lista Lida (Edita aqui!):", value=st.session_state.ocr_texto_bruto)
            
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("✅ Confirmar Dados", type="primary", use_container_width=True):
                    nums_finais = re.findall(r'\b([0-9]|[1-2][0-9]|3[0-6])\b', texto_editado)
                    if nums_finais:
                        st.session_state.historico_quant.extend([int(n) for n in nums_finais])
                        st.session_state.ocr_texto_bruto = "" # Limpa a caixa após injetar
                        st.rerun()
            with col_b2:
                if st.button("🔄 Inverter Ordem", use_container_width=True):
                    nums_finais = re.findall(r'\b([0-9]|[1-2][0-9]|3[0-6])\b', texto_editado)
                    if nums_finais:
                        st.session_state.historico_quant.extend(reversed([int(n) for n in nums_finais]))
                        st.session_state.ocr_texto_bruto = ""
                        st.rerun()

    with aba_teclado:
        st.write("Inserção rápida sem erros:")
        def add_num(n): st.session_state.historico_quant.append(n)
        if st.button("0 🟢", use_container_width=True): add_num(0)
        for row in range(12):
            c1, c2, c3 = st.columns(3)
            n1, n2, n3 = row * 3 + 1, row * 3 + 2, row * 3 + 3
            def btn_label(num): return f"{num} 🔴" if engine.classificar(num)["Cor"] == "Vermelho" else f"{num} ⚫"
            with c1: 
                if st.button(btn_label(n1), use_container_width=True): add_num(n1)
            with c2: 
                if st.button(btn_label(n2), use_container_width=True): add_num(n2)
            with c3: 
                if st.button(btn_label(n3), use_container_width=True): add_num(n3)

    with aba_texto:
        st.write("Cola do chat (ex: `12 5 36 0`):")
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
        
        col_limpar1, col_limpar2 = st.columns(2)
        with col_limpar1:
            if st.button("↩️ Apagar Último", use_container_width=True):
                st.session_state.historico_quant.pop()
                st.rerun()
        with col_limpar2:
            if st.button("🚨 Limpar Sessão", type="primary", use_container_width=True):
                st.session_state.historico_quant = []
                st.session_state.ocr_texto_bruto = ""
                st.rerun()
    else:
        st.info("Nenhum número registado.")

# ==========================================
# 4. DASHBOARD VISUAL COMPLETO 
# ==========================================
historico = st.session_state.historico_quant
n_jogadas = len(historico)
LIMITE_CALIBRACAO = 25 

st.title("🎯 Radar de IA")

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

    if modo_jogo == "Mega Roulette (Multiplicadores)":
        st.markdown("### ⚡ Estratégia de Cobertura Mega Roulette")
        st.write("Atenção: Para ganhares os multiplicadores, tens de fazer **Apostas Plenas (Straight Up)** nestes números.")
        
        setores = [engine.classificar_setor_pista(n) for n in historico]
        contagem_setores = Counter(setores)
        if "Erro" in contagem_setores: del contagem_setores["Erro"]
            
        if contagem_setores:
            setor_quente = contagem_setores.most_common(1)[0][0]
            numeros_para_apostar = engine.SETORES_PLENOS[setor_quente]
            prob_real = (contagem_setores[setor_quente] / n_jogadas) * 100
            
            st.markdown(f"""
            <div class='mega-box'>
                🔥 ZONA DE CAPTURA DO MULTIPLICADOR: {setor_quente.upper()} 🔥<br>
                A bola está a cair aqui {prob_real:.1f}% das vezes.<br><br>
                <b>Coloca 1 ficha Plena em cada um destes números:</b><br>
                <h2>{numeros_para_apostar}</h2>
                <i>Custo total da ronda: {len(numeros_para_apostar)} fichas</i>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Dados insuficientes para calcular o setor Mega.")
    else:
        st.markdown("### 🕵️‍♂️ Assinatura do Croupier (Memória Muscular)")
        saltos = engine.calcular_saltos(historico)
        if saltos:
            contagem_saltos = Counter(saltos)
            distancia_padrao = contagem_saltos.most_common(1)[0][0]
            saltos_na_zona = sum(1 for s in saltos if min(abs(s - distancia_padrao), 37 - abs(s - distancia_padrao)) <= 2)
            confianca_zona = (saltos_na_zona / len(saltos)) * 100
            
            col_f1, col_f2 = st.columns([1, 2])
            if confianca_zona < 25.0:
                with col_f1: st.metric("Distância Padrão", "Falhou", "Dispersão Elevada")
                with col_f2: st.markdown("<div class='erratico-box'>❌ CRUPIÊ ERRÁTICO ❌<br>A força de lançamento varia demasiado.</div>", unsafe_allow_html=True)
            else:
                alvo, zona = engine.projetar_alvo(historico[-1], distancia_padrao)
                with col_f1: st.metric("Distância Padrão de Lançamento", f"+{distancia_padrao} casas", f"Zona atinge {confianca_zona:.1f}% de precisão")
                with col_f2: st.markdown(f"<div class='alvo-box'>🎯 ALVO FÍSICO PROJETADO: NÚMERO {alvo}<br>Cobrir a zona de queda: {zona}</div>", unsafe_allow_html=True)

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
                st.markdown(f"<div class='radar-box' style='background-color: #FFC107; color: black;'>2. ESTATÍSTICA DE ATRASO<br>Apostar no {cor_atrasada}</div>", unsafe_allow_html=True)
                st.warning(f"Atenção: O {cor_atrasada} não sai há {rodadas_atraso} rodadas consecutivas.")
            else:
                st.markdown(f"<div class='radar-box' style='background-color: #555555;'>2. ESTATÍSTICA DE ATRASO<br>Mesa Equilibrada</div>", unsafe_allow_html=True)

        with col_v3:
            duzias = [engine.classificar(n)["Duzia"] for n in historico if engine.classificar(n)["Duzia"] != "Zero"]
            if duzias:
                duzia_quente = Counter(duzias).most_common(1)[0][0]
                st.markdown(f"<div class='radar-box' style='background-color: #00E676; color: black;'>3. ZONA CONTÍNUA<br>Apostar na {duzia_quente}</div>", unsafe_allow_html=True)

    st.divider()
    
    st.markdown("### 📊 Auditoria Quantitativa (Raio-X da Mesa)")
    aba1, aba2, aba3 = st.tabs(["Física (Histograma de Saltos)", "Cilindro (Racetrack)", "Transição de Probabilidade (Markov)"])
    
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
        fig_pista.update_layout(template="plotly_dark", title="Frequência Real de Queda por Setor da Roda")
        st.plotly_chart(fig_pista, use_container_width=True)

    with aba3:
        df_markov = engine.cadeias_de_markov(historico)
        if not df_markov.empty:
            fig_heat = px.imshow(df_markov, text_auto=True, color_continuous_scale="Viridis", title="Mapa Térmico de Mudança de Cor")
            st.plotly_chart(fig_heat, use_container_width=True)
