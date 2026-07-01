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
        return "Verde", "Zero", "Zero", "Zero", "Zero"
    
    cor = "Vermelho" if n in VERMELHOS else "Preto"
    paridade = "Par" if n % 2 == 0 else "Ímpar"
    metade = "Baixo (1-18)" if n <= 18 else "Alto (19-36)"
    
    if n <= 12: duzia = "1ª Dúzia"
    elif n <= 24: duzia = "2ª Dúzia"
    else: duzia = "3ª Dúzia"
        
    if n % 3 == 1: coluna = "1ª Coluna"
    elif n % 3 == 2: coluna = "2ª Coluna"
    else: coluna = "3ª Coluna"
        
    return cor, paridade, metade, duzia, coluna

def obter_vizinhos(n, qtd_vizinhos=2):
    idx = RODA_EUROPEIA.index(n)
    tamanho = len(RODA_EUROPEIA)
    vizinhos = []
    for i in range(-qtd_vizinhos, qtd_vizinhos + 1):
        if i != 0:
            vizinho_idx = (idx + i) % tamanho
            vizinhos.append(RODA_EUROPEIA[vizinho_idx])
    return vizinhos

# ==========================================
# 2. FUNÇÃO AVANÇADA: CÁLCULO DE ATRASOS
# ==========================================
def calcular_atrasos(historico):
    """Calcula há quantas rodadas uma determinada característica não aparece"""
    if not historico:
        return {}
    
    atrasos = {
        "Vermelho": 0, "Preto": 0,
        "Par": 0, "Ímpar": 0,
        "1ª Dúzia": 0, "2ª Dúzia": 0, "3ª Dúzia": 0
    }
    
    # Inverter o histórico para analisar do mais recente para o mais antigo
    historico_invertido = historico[::-1]
    
    # Encontrar atrasos para Cores
    for i, n in enumerate(historico_invertido):
        cor, paridade, _, duzia, _ = classificar_numero(n)
        
        if i == 0: # O último número que saiu zera o atraso da sua categoria
            continue
            
    # Lógica de varredura ativa de atraso
    categorias = {
        "Vermelho": lambda n: classificar_numero(n)[0] == "Vermelho",
        "Preto": lambda n: classificar_numero(n)[0] == "Preto",
        "Par": lambda n: classificar_numero(n)[1] == "Par",
        "Ímpar": lambda n: classificar_numero(n)[1] == "Ímpar",
        "1ª Dúzia": lambda n: classificar_numero(n)[3] == "1ª Dúzia",
        "2ª Dúzia": lambda n: classificar_numero(n)[3] == "2ª Dúzia",
        "3ª Dúzia": lambda n: classificar_numero(n)[3] == "3ª Dúzia",
    }
    
    for cat, condicao in categories.items():
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

st.set_page_config(page_title="Roleta Pro Dashboard", page_icon="📊", layout="wide")
st.title("📊 Dashboard Analítico & Gráfico de Roleta")

with st.container():
    st.markdown("### 📥 Painel de Entrada de Dados")
    col_input, col_btn, col_clear = st.columns([2, 1, 1])
    
    with col_input:
        novo_numero = st.number_input("Introduza o número sorteado (0-36):", min_value=0, max_value=36, step=1)
    with col_btn:
        st.write(" ")
        st.write(" ")
        if st.button("➕ Registar Número", use_container_width=True):
            st.session_state.historico_pro.append(novo_numero)
            st.rerun()
    with col_clear:
        st.write(" ")
        st.write(" ")
        if st.button("🗑️ Reiniciar Sessão", use_container_width=True):
            st.session_state.historico_pro = []
            st.rerun()

# ==========================================
# 4. PROCESSAMENTO E EXIBIÇÃO GRÁFICA
# ==========================================
historico = st.session_state.historico_pro
total = len(historico)

st.divider()

if total > 0:
    st.markdown(f"**Análise Baseada em:** {total} jogadas | **Última sequência inserida:** {historico[-12:]}")
    
    dados_processados = [classificar_numero(n) for n in historico]
    cores = [d[0] for d in dados_processados]
    duzias = [d[3] for d in dados_processados if d[3] != "Zero"]
    
    aba1, aba2, aba3 = st.tabs(["📈 Gráficos & Tendências", "🎯 Monitor de Atrasos", "🎡 Setores do Cilindro"])
    
    with aba1:
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown("#### 🔴 Frequência de Cores (Gráfico)")
            contagem_cores = Counter(cores)
            # Criar um DataFrame estruturado para alimentar o gráfico do Streamlit
            df_chart_cores = pd.DataFrame({
                "Vezes Sorteado": [contagem_cores.get("Vermelho", 0), contagem_cores.get("Preto", 0), contagem_cores.get("Verde", 0)]
            }, index=["Vermelho", "Preto", "Verde"])
            st.bar_chart(df_chart_cores)
            
        with col_graf2:
            st.markdown("#### 📊 Frequência de Dúzias (Gráfico)")
            contagem_duzias = Counter(duzias)
            df_chart_duzias = pd.DataFrame({
                "Vezes Sorteado": [contagem_duzias.get("1ª Dúzia", 0), contagem_duzias.get("2ª Dúzia", 0), contagem_duzias.get("3ª Dúzia", 0)]
            }, index=["1ª Dúzia", "2ª Dúzia", "3ª Dúzia"])
            st.bar_chart(df_chart_duzias)

    with aba2:
        st.markdown("#### ⏱️ Detetor de Atrasos Atuais (Atrasómetros)")
        st.write("Indica há quantas rodadas consecutivas uma opção *não* sai na roleta.")
        
        dict_atrasos = calcular_atrasos(historico)
        df_atrasos = pd.DataFrame([
            {"Indicador/Campo": k, "Rodadas de Atraso": v} for k, v in dict_atrasos.items()
        ])
        st.dataframe(df_atrasos, use_container_width=True, hide_index=True)
        
        # Alerta de alta tendência (puramente estatístico)
        max_atraso = max(dict_atrasos.values())
        campo_max = [k for k, v in dict_atrasos.items() if v == max_atraso][0]
        if max_atraso > 4:
            st.warning(f"⚠️ **Alerta Estatístico:** O campo **{campo_max}** está sem sair há **{max_atraso}** rodadas seguidas!")

    with aba3:
        st.markdown("#### 🔮 Diagnóstico de Vizinhos Físicos")
        ultimo_num = historico[-1]
        vizinhos = obter_vizinhos(ultimo_num, 2)
        
        st.success(f"O último número sorteado foi o **{ultimo_num}** ({classificar_numero(ultimo_num)[0]}).")
        st.write(f"Os vizinhos de setor no cilindro real são: **{vizinhos[0]} e {vizinhos[1]}** (à esquerda) e **{vizinhos[2]} e {vizinhos[3]}** (à direita).")
        
else:
    st.info("Aguardando inserção de dados. Digite o número sorteado acima para gerar os gráficos e análises.")
