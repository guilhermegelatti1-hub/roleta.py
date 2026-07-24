# 🎯 Roulette Lens

Dashboard em Streamlit para analisar resultados de roleta europeia entre **0 e 36**, com foco em visualização, recência e auditoria estatística.

> Resultados de roleta são eventos independentes. Este projeto descreve padrões históricos e não garante previsão, vantagem ou lucro.

## Funcionalidades

- Interface responsiva em Streamlit.
- Entrada por mesa numérica ou texto.
- Histórico visual com as cores da roleta.
- Pontuação ponderada por recência.
- Seleção determinística de setor e epicentro.
- Cobertura configurável de vizinhos físicos.
- Backtest walk-forward sem uso de dados futuros.
- Score interno baseado em amostra, concentração e desempenho histórico.
- Tabela de frequência dos números.
- Testes unitários do motor.

## Estrutura

```text
.
├── roleta_pro.py
├── roulette_engine.py
├── requirements.txt
├── README.md
└── tests/
    └── test_engine.py
