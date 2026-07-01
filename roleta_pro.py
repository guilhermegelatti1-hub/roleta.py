import streamlit as st
import pandas as pd
from collections import Counter

# ==========================================
# 1. CONFIGURAÇÕES E DADOS DA ROLETA
# ==========================================

RODA_EUROPEIA = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 
                 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

VERMELHOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

def classificar_numero(n):
    if n == 0:
        return "Verde", "Zero", "Zero", "Zero", "Zero", "🟢"
    
    cor = "Vermelho" if n in VERMELHOS else "Preto"
    emoji = "🔴" if cor == "Vermelho" else "⚫"
    paridade = "Par" if n % 2 == 0 else "Ímpar"
    metade = "Baixo (1-18)" if n <= 18 else "Alto (19-36)"
    
    if n <= 12: duzia = "1ª Dúzia"
    elif n <= 24: duzia = "2ª Dúzia"
    else: duzia = "3ª Dúzia"
        
    if n % 3 == 1: coluna = "1ª Coluna"
    elif n % 3 == 2: coluna = "2ª Coluna"
    else: coluna = "3ª Coluna"
        
    return cor, paridade, metade, duzia, coluna, emoji

def obter_vizinhos(n, qtd_vizinhos=2):
    idx = RODA_EUROPEIA.index(n)
    tamanho = len(RODA_EUROPEIA)
    vizinhos = []
    for i in range(-qtd_vizinhos, qtd_vizinhos + 1):
        if i != 0:
            vizinho_idx = (idx + i) % tamanho
            vizinhos.append(RODA_EUROPEIA[vizinho_idx])
    return vizinhos

def calcular_atrasos(historico):
    if not historico:
        return {}
    
    atrasos = {
        "Vermelho": 0, "Preto": 0,
        "Par": 0, "Ímpar": 0,
        "1ª Dúzia": 0, "2ª Dúzia": 0, "3ª Dúzia": 0,
        "1ª Coluna": 0, "2ª Coluna": 0, "3ª Coluna": 0
    }
    
    historico_invertido = historico[::-1]
    
    categorias = {
        "Vermelho": lambda n: classificar_numero(n)[0] == "Vermelho",
        "Preto": lambda n: classificar_numero(n)[0] == "Preto",
        "Par": lambda n: classificar_numero(n)[1] == "Par",
        "Ímpar": lambda n: classificar_numero(n)[1] == "Ímpar",
        "1ª Dúzia": lambda n: classificar_numero(n)[3] == "1ª Dúzia",
        "2ª Dúzia": lambda n: classificar_numero(n)[3] == "2ª Dúzia",
        "3ª Dúzia": lambda n: classificar_numero(n)[3] == "3ª Dúzia",
        "1ª Coluna": lambda n: classificar_numero(n)[4] == "1ª Coluna",
        "2ª Coluna": lambda n: classificar_numero(n)[4] == "2ª Coluna",
        "3ª Coluna": lambda n: classificar_numero(n)[4] == "3ª Coluna",
    }
    
    for cat, condicao in categorias.items():
        contador = 0
        for n in historico_invertido:
            if condicao(n):
                break
            contador += 1
        atrasos[cat] = contador
        
    return atrasos

# ==========================================
# 3. INTERFACE WEB E MEMÓRIA
# ==========================================
if 'historico_pro' not in st.session_state:
    st.session_state.historico_pro = []

st.set_page_config(page_title="Roleta Premium", page_icon="🎰", layout="wide")
st.title("🎰 Dashboard Premium: Estatísticas da Roleta")

with st.container():
    st.markdown("### 📥 Registar Nova Jogada")
    col_input, col_btn, col_clear = st.columns([2, 1, 1])
    
    with col_input:
        novo_numero = st.number_input("Introduza o número sorteado (0-36):", min_value=0, max_value=36, step=1)
    with col_btn:
        st.write(" ")
        st.write(" ")
        if st.button("➕ Registar", use_container_width=True, type="primary"):
            st.session_state.historico_pro.append(novo_numero)
            st.rerun()
    with col_clear:
        st.write(" ")
        st.write(" ")
        if st.button("🗑️ Reiniciar", use_container_width=True):
            st.session_state.historico_pro = []
            st.rerun()

# ==========================================
# 4. PROCESSAMENTO, MÉTRICAS E GRÁFICOS
# ==========================================
historico = st.session_state.historico_pro
total = len(historico)

st.divider()

if total > 0:
    # Preparar Dados
    dados_processados = [classificar_numero(n) for n in historico]
    cores = [d[0] for d in dados_processados]
    emojis = [d[5] for d in dados_processados]
    duzias = [d[3] for d in dados_processados if d[3] != "Zero"]
    
    dict_atrasos = calcular_atrasos(historico)
    max_atraso = max(dict_atrasos.values())
    campo_max = [k for k, v in dict_atrasos.items() if v == max_atraso][0]
    
    # 4.1. MÉTRICAS DE TOPO (DASHBOARD)
    met1, met2, met3 = st.columns(3)
    met1.metric("Total de Rodadas", total)
    met2.metric("Último Sorteado", f"{historico[-1]} {emojis[-1]}")
    met3.metric("Maior Atraso Atual", f"{campo_max}", f"-{max_atraso} rodadas")
    
    # Histórico Visual
    historico_visual = " ".join([f"{n}{e}" for n, e in zip(historico[-15:], emojis[-15:])])
    st.markdown(f"**Últimos 15 números:** {historico_visual}")
    
    # 4.2. ABAS DE ANÁLISE
    aba1, aba2, aba3, aba4 = st.tabs(["🔥 Quentes & Frios", "📈 Gráficos", "🎯 Atrasómetros", "🎡 Cilindro"])
    
    with aba1:
        st.markdown("#### Análise de Frequência de Números")
        col_q, col_f = st.columns(2)
        
        contagem_numeros = Counter(historico)
        
        with col_q:
            st.success("🔥 **Números Quentes (Top 3)**")
            quentes = contagem_numeros.most_common(3)
            for n, qtd in quentes:
                st.write(f"Número **{n}** ({classificar_numero(n)[0]}) — Saiu **{qtd}** vezes")
                
        with col_f:
            st.error("❄️ **Números Frios (Menos Sorteados)**")
            # Procura números que saíram menos ou ainda não saíram (0 vezes)
            todos_numeros = set(range(37))
            numeros_saidos = set(contagem_numeros.keys())
            nao_saidos = list(todos_numeros - numeros_saidos)
            
            if nao_saidos:
                st.write(f"Existem **{len(nao_saidos)}** números que ainda não saíram nesta sessão.")
                st.write(f"Exemplos: {nao_saidos[:5]}")
            else:
                frios = contagem_numeros.most_common()[-3:]
                for n, qtd in frios:
                    st.write(f"Número **{n}** — Saiu apenas **{qtd}** vez(es)")

    with aba2:
        col_graf1, col_graf2 = st.columns(2)
        with col_graf1:
            st.markdown("**Distribuição de Cores**")
            contagem_cores = Counter(cores)
            df_chart_cores = pd.DataFrame({
                "Vezes Sorteado": [contagem_cores.get("Vermelho", 0), contagem_cores.get("Preto", 0), contagem_cores.get("Verde", 0)]
            }, index=["Vermelho", "Preto", "Verde"])
            st.bar_chart(df_chart_cores, color=["#FF4B4B", "#262730", "#00C853"]) # Cores personalizadas
            
        with col_graf2:
            st.markdown("**Distribuição de Dúzias**")
            contagem_duzias = Counter(duzias)
            df_chart_duzias = pd.DataFrame({
                "Vezes Sorteado": [contagem_duzias.get("1ª Dúzia", 0), contagem_duzias.get("2ª Dúzia", 0), contagem_duzias.get("3ª Dúzia", 0)]
            }, index=["1ª Dúzia", "2ª Dúzia", "3ª Dúzia"])
            st.bar_chart(df_chart_duzias)

    with aba3:
        st.markdown("#### Tabela Completa de Atrasos")
        df_atrasos = pd.DataFrame([
            {"Indicador": k, "Rodadas de Atraso": v} for k, v in dict_atrasos.items()
        ])
        st.dataframe(df_atrasos.sort_values(by="Rodadas de Atraso", ascending=False), use_container_width=True, hide_index=True)

    with aba4:
        st.markdown("#### Zonas da Roda Europeia")
        ultimo_num = historico[-1]
        vizinhos = obter_vizinhos(ultimo_num, 2)
        st.info(f"Último sorteado: **{ultimo_num}** {classificar_numero(ultimo_num)[5]}")
        st.write(f"Os 4 vizinhos imediatos na roda física são: **{vizinhos[0]}, {vizinhos[1]}, {vizinhos[2]}, {vizinhos[3]}**.")
        
else:
    st.info("O painel está pronto! Comece a inserir os números da sua sessão de roleta para gerar as estatísticas em tempo real.")
