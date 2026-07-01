import streamlit as st
import pandas as pd
from collections import Counter

# ==========================================
# 1. CONFIGURAÇÕES E DADOS DA ROLETA
# ==========================================

# Ordem exata dos números na roda da Roleta Europeia
RODA_EUROPEIA = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 
                 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

VERMELHOS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

# Funções de Classificação
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
    # Encontra o índice do número na roda física e retorna os vizinhos
    idx = RODA_EUROPEIA.index(n)
    tamanho = len(RODA_EUROPEIA)
    vizinhos = []
    # Pega os números à esquerda e à direita
    for i in range(-qtd_vizinhos, qtd_vizinhos + 1):
        if i != 0:
            vizinho_idx = (idx + i) % tamanho
            vizinhos.append(RODA_EUROPEIA[vizinho_idx])
    return vizinhos

# ==========================================
# 2. INICIALIZAÇÃO DA MEMÓRIA (STATE)
# ==========================================

if 'historico_pro' not in st.session_state:
    st.session_state.historico_pro = []

st.set_page_config(page_title="Roleta Pro Analyzer", page_icon="🎯", layout="wide")
st.title("🎯 Roleta Pro Analyzer - Diagnóstico Completo")

# ==========================================
# 3. INTERFACE DE ENTRADA
# ==========================================

with st.container():
    st.markdown("### 📥 Inserir Nova Jogada")
    col_input, col_btn, col_clear = st.columns([2, 1, 1])
    
    with col_input:
        novo_numero = st.number_input("Digite o número sorteado (0-36):", min_value=0, max_value=36, step=1)
    with col_btn:
        st.write(" ")
        st.write(" ")
        if st.button("➕ Adicionar Número", use_container_width=True):
            st.session_state.historico_pro.append(novo_numero)
            st.rerun()
    with col_clear:
        st.write(" ")
        st.write(" ")
        if st.button("🗑️ Limpar Tudo", use_container_width=True):
            st.session_state.historico_pro = []
            st.rerun()

# ==========================================
# 4. PAINEL DE DIAGNÓSTICO ESTATÍSTICO
# ==========================================

historico = st.session_state.historico_pro
total = len(historico)

st.divider()

if total > 0:
    st.markdown(f"**Total de Jogadas Analisadas:** {total} | **Últimos 10 números:** {historico[-10:]}")
    
    # Processar todos os dados do histórico
    dados_processados = [classificar_numero(n) for n in historico]
    cores = [d[0] for d in dados_processados]
    paridades = [d[1] for d in dados_processados if d[1] != "Zero"]
    duzias = [d[3] for d in dados_processados if d[3] != "Zero"]
    
    # Criar abas para organizar a informação
    aba1, aba2, aba3 = st.tabs(["🔴 Cores & Básicos", "📊 Dúzias & Colunas", "🎡 Análise de Vizinhos"])
    
    with aba1:
        colA, colB = st.columns(2)
        with colA:
            st.markdown("#### Distribuição de Cores")
            contagem_cores = Counter(cores)
            df_cores = pd.DataFrame([
                {"Cor": k, "Ocorrências": v, "Frequência Real": f"{(v/total)*100:.1f}%"} 
                for k, v in contagem_cores.items()
            ])
            st.table(df_cores)
            
        with colB:
            st.markdown("#### Detetor de Sequências")
            # Lógica para calcular a sequência atual da mesma cor
            seq_atual = 1
            for i in range(len(cores)-2, -1, -1):
                if cores[i] == cores[-1]:
                    seq_atual += 1
                else:
                    break
            st.info(f"A cor **{cores[-1]}** saiu nas últimas **{seq_atual}** jogada(s) consecutiva(s).")
            
            st.markdown("#### Frequência Par/Ímpar (Ignorando Zeros)")
            if paridades:
                contagem_paridade = Counter(paridades)
                df_par = pd.DataFrame([
                    {"Tipo": k, "Ocorrências": v, "Frequência Real": f"{(v/len(paridades))*100:.1f}%"} 
                    for k, v in contagem_paridade.items()
                ])
                st.table(df_par)

    with aba2:
        st.markdown("#### Análise de Dúzias")
        if duzias:
            cont_duzias = Counter(duzias)
            # Probabilidade teórica de uma dúzia é 12/37
            prob_teorica_duzia = (12/37) * 100
            
            df_duzias = pd.DataFrame([
                {"Dúzia": k, "Ocorrências": v, "Freq. Real": f"{(v/len(duzias))*100:.1f}%", "Prob. Teórica": f"{prob_teorica_duzia:.1f}%"} 
                for k, v in cont_duzias.items()
            ])
            st.table(df_duzias)
        else:
            st.write("Ainda não caíram números nas dúzias (apenas zeros).")

    with aba3:
        st.markdown("#### Diagnóstico de Zonas da Roda (Cilindro Físico)")
        ultimo_num = historico[-1]
        vizinhos = obter_vizinhos(ultimo_num, 2)
        
        st.success(f"O último número sorteado foi o **{ultimo_num}**.")
        st.write(f"Os 4 vizinhos imediatos deste número no cilindro físico são: **{vizinhos}**")
        st.write("Muitos jogadores profissionais analisam se a bola está a cair repetidamente num setor específico da roda física, o que pode indicar uma ligeira inclinação (tilt) na mesa física real.")

else:
    st.warning("O painel está vazio. Insere o primeiro número para iniciar a recolha de dados.")
