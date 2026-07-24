Roulette Lens
Dashboard em Streamlit para analisar resultados de roleta europeia (0–36) com foco em transparência estatística e qualidade visual.
O que mudou
Interface responsiva com identidade visual mais limpa.
Motor estatístico separado da interface.
Pontuação ponderada por recência.
Seleção determinística de setor e epicentro.
Backtest walk-forward sem usar dados futuros.
Índice de confiança baseado em amostra, concentração e desempenho histórico.
Tabela completa de frequência dos números.
Testes unitários para roda, cores, setores, vizinhos e geração do sinal.
Aviso explícito sobre aleatoriedade e ausência de garantia.
> Resultados de roleta são independentes. O painel descreve padrões históricos e não garante previsão, vantagem ou lucro.
Executar localmente
```bash
python -m venv .venv
```
Ative o ambiente virtual e instale as dependências:
```bash
pip install -r requirements.txt
```
Inicie a aplicação:
```bash
streamlit run roleta_pro.py
```
Executar os testes
```bash
python -m unittest discover -s tests -v
```
Estrutura
```text
.
├── roleta_pro.py
├── roulette_engine.py
├── requirements.txt
└── tests/
    └── test_engine.py
```
Como o sinal funciona
Os resultados são classificados nos setores físicos da roda.
Resultados mais recentes recebem peso maior.
O setor com maior pontuação ponderada é selecionado.
Dentro dele, o número com maior frequência ponderada vira o epicentro.
O painel cobre o epicentro e os vizinhos físicos configurados.
Um backtest walk-forward mede como essa regra teria se comportado no próprio histórico.
A métrica de backtest deve ser interpretada com cautela: amostras pequenas variam muito e desempenho passado não implica desempenho futuro.
