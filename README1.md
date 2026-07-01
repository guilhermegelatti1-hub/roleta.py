# 🎯 Roleta Pro Analyzer

Bem-vindo ao **Roleta Pro Analyzer**, um painel de diagnóstico estatístico e rastreador de jogadas de roleta desenvolvido em Python.

## 📖 Sobre o Projeto
Este projeto foi criado com o objetivo de unir **Programação (Python)** e **Estatística**. O sistema permite ao utilizador inserir os números sorteados numa Roleta Europeia física e gera um diagnóstico completo e em tempo real sobre o histórico da mesa.

> **Nota Matemática:** O sistema calcula probabilidades empíricas (o que já aconteceu) e compara com as probabilidades teóricas. A roleta é um jogo de eventos independentes, logo, este software tem fins puramente analíticos e educativos sobre a Lei dos Grandes Números.

## ✨ Funcionalidades
- **Rastreador de Histórico:** Memoriza as jogadas da sessão atual.
- **Análise Básica:** Distribuição de Cores (Vermelho/Preto/Verde), Paridade (Par/Ímpar) e Metades (Altos/Baixos).
- **Zonas da Mesa:** Monitorização de Dúzias e Colunas.
- **Detetor de Sequências:** Identifica a quantidade de vezes consecutivas que uma cor saiu.
- **Análise de Vizinhos (Cilindro Físico):** Mapeia a roda da Roleta Europeia real e identifica os 4 vizinhos imediatos do último número sorteado, ajudando a visualizar setores da roda.

## 🛠️ Tecnologias Utilizadas
- **Python 3**
- **Streamlit:** Para a criação da interface web interativa.
- **Pandas:** Para estruturação dos dados em tabelas.

## 🚀 Como Executar o Projeto

1. Certifica-te de que tens o Python instalado no teu computador.
2. Instala as dependências necessárias executando o comando no terminal:
   ```bash
   pip install streamlit pandas
   pip install streamlit pandas numpy plotly
