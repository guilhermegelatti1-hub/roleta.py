qq é pra mudar ?

O problema continua porque o st.markdown() ainda está tratando o HTML como Markdown. Como seu Streamlit é recente, a correção mais segura é usar st.html().

No arquivo roleta_pro.py, faça estas três substituições.

1. Cabeçalho

Substitua todo o bloco do cabeçalho por:

hero_html = """
<section class="hero">
    <div class="eyebrow">
        EUROPEAN ROULETTE ANALYTICS
    </div>

    <h1>Roulette Lens</h1>

    <p>
        Painel auditável para visualizar frequência,
        setores físicos, recência e desempenho histórico
        da regra estatística.
    </p>
</section>
"""

st.html(hero_html)
2. Função render_signal_card

No final da função, substitua:

st.markdown(
    card_html,
    unsafe_allow_html=True,
)

por:

st.html(card_html)

A função deve terminar assim:

    card_html = f"""
<section class="signal-card">
    <div class="eyebrow">
        LEITURA ESTATÍSTICA
    </div>

    <div class="signal-header">
        <div>
            <h2>{escape(signal.target_sector)}</h2>

            <p>
                Epicentro físico:
                <strong>{signal.epicenter}</strong>
            </p>
        </div>

        <span class="score-pill {score_class}">
            Score interno {escape(signal.confidence_label.lower())}
        </span>
    </div>

    <div class="ball-row">
        {covered_numbers}
    </div>

    <div class="signal-grid">
        <div>
            <span>Concentração</span>
            <strong>{signal.score:.1f}%</strong>
        </div>

        <div>
            <span>Backtest</span>
            <strong>{signal.backtest_accuracy:.1f}%</strong>
            <small>{signal.backtest_trials} testes</small>
        </div>

        <div>
            <span>Amostra</span>
            <strong>{signal.sample_size}</strong>
        </div>
    </div>

    <p class="signal-note">
        {escape(signal.explanation)}
    </p>
</section>
"""

    st.html(card_html)
3. Aviso final

Substitua o bloco final por:

disclaimer_html = """
<div class="disclaimer">
    <strong>Importante:</strong>
    resultados de roleta são independentes e aleatórios.
    Este painel descreve o histórico e não garante vantagem,
    lucro ou previsão do próximo giro.
</div>
"""

st.html(disclaimer_html)
4. CSS

O CSS também pode usar st.html().

Substitua:

st.markdown(
    """
    <style>

por:

st.html(
    """
    <style>

E remova esta parte do fechamento:

unsafe_allow_html=True,

Ficando:

st.html(
    """
    <style>
    /* todo o seu CSS */
    </style>
    """
)

Depois salve e reinicie:

python -m py_compile roleta_pro.py roulette_engine.py
streamlit run roleta_pro.py

O st.html() envia o conteúdo diretamente como HTML e evita que as tags apareçam dentro de uma caixa de código.

me de o código completo 

Substitua todo o conteúdo de roleta_pro.py por este código:

from __future__ import annotations

from collections import Counter
from html import escape
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from roulette_engine import EuropeanRouletteEngine, SignalResult


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

st.set_page_config(
    page_title="Roulette Lens",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

engine = EuropeanRouletteEngine()

if "history" not in st.session_state:
    st.session_state.history = []


# ==========================================================
# FUNÇÕES
# ==========================================================

def add_number(number: int) -> None:
    """Adiciona um número validado ao histórico."""

    validated_number = engine.validate_number(number)

    st.session_state.history.append(validated_number)

    # Limita o histórico da sessão a 500 resultados.
    st.session_state.history = st.session_state.history[-500:]


def submit_text_input() -> None:
    """Extrai números válidos de uma sequência de texto."""

    raw_text = st.session_state.get(
        "quick_input",
        "",
    )

    numbers = re.findall(
        r"(?<!\d)(?:[0-9]|[12][0-9]|3[0-6])(?!\d)",
        raw_text,
    )

    for number in numbers:
        add_number(int(number))

    st.session_state.quick_input = ""


def number_badge(number: int) -> str:
    """Cria a bolinha visual correspondente ao número."""

    color_class = {
        "Vermelho": "ball-red",
        "Preto": "ball-black",
        "Verde": "ball-green",
    }[engine.get_color(number)]

    return (
        f"<span class='number-ball {color_class}'>"
        f"{number}"
        "</span>"
    )


def render_signal_card(signal: SignalResult) -> None:
    """Renderiza o cartão principal da análise."""

    score_class = {
        "Alta": "score-high",
        "Média": "score-medium",
        "Baixa": "score-low",
    }.get(
        signal.confidence_label,
        "score-low",
    )

    covered_numbers = "".join(
        number_badge(number)
        for number in signal.covered_numbers
    )

    backtest_trials = getattr(
        signal,
        "backtest_trials",
        max(signal.sample_size - 8, 0),
    )

    card_html = f"""
<section class="signal-card">
    <div class="eyebrow">
        LEITURA ESTATÍSTICA
    </div>

    <div class="signal-header">
        <div>
            <h2>{escape(signal.target_sector)}</h2>

            <p>
                Epicentro físico:
                <strong>{signal.epicenter}</strong>
            </p>
        </div>

        <span class="score-pill {score_class}">
            Score interno
            {escape(signal.confidence_label.lower())}
        </span>
    </div>

    <div class="ball-row">
        {covered_numbers}
    </div>

    <div class="signal-grid">
        <div>
            <span>Concentração</span>
            <strong>{signal.score:.1f}%</strong>
        </div>

        <div>
            <span>Backtest</span>
            <strong>{signal.backtest_accuracy:.1f}%</strong>
            <small>{backtest_trials} testes</small>
        </div>

        <div>
            <span>Amostra</span>
            <strong>{signal.sample_size}</strong>
        </div>
    </div>

    <p class="signal-note">
        {escape(signal.explanation)}
    </p>
</section>
"""

    st.html(card_html)


# ==========================================================
# CSS
# ==========================================================

css = """
<style>
:root {
    --background: #07111f;
    --surface: rgba(15, 28, 46, 0.90);
    --surface-secondary: rgba(20, 39, 63, 0.96);
    --border: rgba(148, 163, 184, 0.18);
    --text: #edf6ff;
    --muted: #9eb0c4;
    --accent: #41d9b5;
    --accent-secondary: #77a7ff;
    --gold: #f5c76b;
}

.stApp {
    background:
        radial-gradient(
            circle at 15% 10%,
            rgba(65, 217, 181, 0.12),
            transparent 32rem
        ),
        radial-gradient(
            circle at 88% 18%,
            rgba(119, 167, 255, 0.11),
            transparent 28rem
        ),
        linear-gradient(
            145deg,
            #050b14 0%,
            var(--background) 55%,
            #081425 100%
        );

    color: var(--text);
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #081321 0%,
            #0c1b2d 100%
        );

    border-right: 1px solid var(--border);
}

[data-testid="stMetric"] {
    padding: 16px 18px;
    border: 1px solid var(--border);
    border-radius: 18px;
    background: var(--surface);

    box-shadow:
        0 14px 34px
        rgba(0, 0, 0, 0.18);
}

.hero {
    margin-bottom: 22px;
    padding: 28px 30px;
    border: 1px solid var(--border);
    border-radius: 24px;

    background:
        linear-gradient(
            120deg,
            rgba(65, 217, 181, 0.13),
            rgba(119, 167, 255, 0.08)
        ),
        var(--surface);

    box-shadow:
        0 22px 55px
        rgba(0, 0, 0, 0.22);
}

.hero h1 {
    margin: 0;
    font-size: clamp(2.1rem, 4vw, 3.7rem);
    letter-spacing: -0.05em;
}

.hero p {
    max-width: 780px;
    margin: 12px 0 0;
    color: var(--muted);
    font-size: 1.05rem;
}

.eyebrow {
    margin-bottom: 8px;
    color: var(--accent);
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.16em;
}

.signal-card {
    min-height: 360px;
    padding: 26px;
    border: 1px solid rgba(65, 217, 181, 0.28);
    border-radius: 24px;

    background:
        linear-gradient(
            145deg,
            rgba(65, 217, 181, 0.14),
            rgba(119, 167, 255, 0.06)
        ),
        var(--surface-secondary);

    box-shadow:
        0 22px 55px
        rgba(0, 0, 0, 0.25);
}

.signal-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 18px;
}

.signal-header h2 {
    margin: 0;
    font-size: 2rem;
}

.signal-header p,
.signal-note {
    color: var(--muted);
}

.score-pill {
    display: inline-flex;
    padding: 8px 12px;
    border-radius: 999px;
    white-space: nowrap;
    font-size: 0.78rem;
    font-weight: 800;
}

.score-high {
    background: rgba(65, 217, 181, 0.16);
    color: #7ff4d8;
}

.score-medium {
    background: rgba(245, 199, 107, 0.16);
    color: #ffe09d;
}

.score-low {
    background: rgba(255, 101, 119, 0.14);
    color: #ff9baa;
}

.ball-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 24px 0;
}

.number-ball {
    display: inline-flex;
    width: 48px;
    height: 48px;
    align-items: center;
    justify-content: center;

    border:
        2px solid
        rgba(255, 255, 255, 0.28);

    border-radius: 50%;
    font-weight: 900;

    box-shadow:
        inset 0 0 0 2px
        rgba(0, 0, 0, 0.16),
        0 8px 20px
        rgba(0, 0, 0, 0.25);
}

.ball-red {
    background:
        linear-gradient(
            145deg,
            #ed334e,
            #9f142a
        );

    color: white;
}

.ball-black {
    background:
        linear-gradient(
            145deg,
            #293648,
            #080c12
        );

    color: white;
}

.ball-green {
    background:
        linear-gradient(
            145deg,
            #31c68c,
            #087451
        );

    color: white;
}

.signal-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 12px 0 20px;
}

.signal-grid div {
    padding: 14px;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: rgba(7, 17, 31, 0.64);
}

.signal-grid span,
.signal-grid small {
    display: block;
    color: var(--muted);
    font-size: 0.76rem;
}

.signal-grid strong {
    font-size: 1.2rem;
}

.history-box {
    max-height: 230px;
    overflow-y: auto;
    padding: 14px;
    border: 1px solid var(--border);
    border-radius: 16px;
    background: rgba(3, 9, 17, 0.66);
    line-height: 2.5;
}

.disclaimer {
    margin-top: 18px;
    padding: 13px 16px;
    border-left: 3px solid var(--gold);
    border-radius: 8px;
    background: rgba(245, 199, 107, 0.08);
    color: #d8c79f;
    font-size: 0.9rem;
}

div.stButton > button {
    border: 1px solid var(--border);
    border-radius: 12px;

    transition:
        transform 0.15s ease,
        border-color 0.15s ease;
}

div.stButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(65, 217, 181, 0.55);
}

@media (max-width: 760px) {
    .signal-grid {
        grid-template-columns: 1fr;
    }

    .signal-header {
        flex-direction: column;
    }
}
</style>
"""

st.html(css)


# ==========================================================
# BARRA LATERAL
# ==========================================================

with st.sidebar:
    st.markdown("## 🎯 Roulette Lens")

    st.caption(
        "Leitura estatística da roleta europeia"
    )

    analysis_window = st.slider(
        "Janela de análise",
        min_value=12,
        max_value=120,
        value=36,
        help=(
            "Quantidade de resultados recentes "
            "utilizada na leitura."
        ),
    )

    decay = st.slider(
        "Peso da recência",
        min_value=0.75,
        max_value=0.98,
        value=0.90,
        step=0.01,
        help=(
            "Valores menores dão mais peso "
            "aos resultados recentes."
        ),
    )

    neighbor_radius = st.select_slider(
        "Cobertura de vizinhos",
        options=[1, 2, 3],
        value=2,
        help=(
            "Quantidade de vizinhos físicos "
            "de cada lado do epicentro."
        ),
    )

    st.divider()

    keyboard_tab, text_tab = st.tabs(
        [
            "Mesa",
            "Texto",
        ]
    )

    with keyboard_tab:
        if st.button(
            "0 🟢",
            use_container_width=True,
            key="number_0",
        ):
            add_number(0)
            st.rerun()

        for row in range(12):
            columns = st.columns(3)

            for offset, column in enumerate(
                columns,
                start=1,
            ):
                number = row * 3 + offset

                if engine.get_color(number) == "Vermelho":
                    icon = "🔴"
                else:
                    icon = "⚫"

                with column:
                    if st.button(
                        f"{number} {icon}",
                        use_container_width=True,
                        key=f"number_{number}",
                    ):
                        add_number(number)
                        st.rerun()

    with text_tab:
        st.text_input(
            "Cole uma sequência",
            key="quick_input",
            placeholder="Ex.: 17, 0, 32, 21, 8",
            on_change=submit_text_input,
        )

        st.caption(
            "Aceita números de 0 a 36 separados "
            "por espaço, vírgula ou quebra de linha."
        )

    st.divider()
    st.markdown("### Histórico")

    if st.session_state.history:
        recent_badges = " ".join(
            number_badge(number)
            for number in st.session_state.history[-60:]
        )

        history_html = (
            "<div class='history-box'>"
            f"{recent_badges}"
            "</div>"
        )

        st.html(history_html)

        st.caption(
            f"{len(st.session_state.history)} "
            "resultados registrados"
        )

        undo_column, clear_column = st.columns(2)

        with undo_column:
            if st.button(
                "↩ Desfazer",
                use_container_width=True,
            ):
                st.session_state.history.pop()
                st.rerun()

        with clear_column:
            if st.button(
                "Limpar",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.history = []
                st.rerun()

    else:
        st.info(
            "Adicione resultados para iniciar."
        )


# ==========================================================
# CABEÇALHO
# ==========================================================

hero_html = """
<section class="hero">
    <div class="eyebrow">
        EUROPEAN ROULETTE ANALYTICS
    </div>

    <h1>Roulette Lens</h1>

    <p>
        Painel auditável para visualizar frequência,
        setores físicos, recência e desempenho histórico
        da regra estatística.
    </p>
</section>
"""

st.html(hero_html)


# ==========================================================
# PROCESSAMENTO
# ==========================================================

history = st.session_state.history
total_spins = len(history)

if total_spins == 0:
    st.info(
        "Comece adicionando os resultados "
        "no painel lateral."
    )

    st.stop()

current_window = history[-analysis_window:]

signal = engine.build_signal(
    current_window,
    decay=decay,
    neighbor_radius=neighbor_radius,
)

red_count = sum(
    engine.get_color(number) == "Vermelho"
    for number in current_window
)

black_count = sum(
    engine.get_color(number) == "Preto"
    for number in current_window
)

zero_count = current_window.count(0)


# ==========================================================
# MÉTRICAS
# ==========================================================

metric_columns = st.columns(4)

metric_columns[0].metric(
    "Resultados",
    total_spins,
)

metric_columns[1].metric(
    "Janela ativa",
    len(current_window),
)

metric_columns[2].metric(
    "Vermelho / Preto",
    f"{red_count} / {black_count}",
)

metric_columns[3].metric(
    "Zeros",
    zero_count,
)

st.write("")


# ==========================================================
# CARTÃO PRINCIPAL E GRÁFICO DE SETORES
# ==========================================================

left_column, right_column = st.columns(
    [1.16, 0.84],
    gap="large",
)

with left_column:
    if signal:
        render_signal_card(signal)
    else:
        st.warning(
            "São necessários pelo menos "
            "8 resultados válidos para gerar "
            "uma leitura."
        )

with right_column:
    sector_counts = Counter(
        engine.get_sector(number)
        for number in current_window
    )

    sector_names = list(engine.SECTORS)

    sector_values = [
        sector_counts.get(name, 0)
        for name in sector_names
    ]

    sector_chart = go.Figure(
        go.Bar(
            x=sector_values,
            y=sector_names,
            orientation="h",
            text=sector_values,
            textposition="auto",
            marker={
                "color": [
                    "#41d9b5",
                    "#77a7ff",
                    "#f5c76b",
                    "#d17cff",
                ],
                "line": {
                    "width": 0,
                },
            },
        )
    )

    sector_chart.update_layout(
        title="Distribuição por setor",
        template="plotly_dark",
        height=360,
        margin={
            "l": 10,
            "r": 10,
            "t": 55,
            "b": 10,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Ocorrências",
        yaxis_title="",
        showlegend=False,
    )

    st.plotly_chart(
        sector_chart,
        use_container_width=True,
    )


# ==========================================================
# ABAS
# ==========================================================

overview_tab, numbers_tab, audit_tab = st.tabs(
    [
        "Visão geral",
        "Números",
        "Auditoria da leitura",
    ]
)


# ==========================================================
# ABA: VISÃO GERAL
# ==========================================================

with overview_tab:
    first_spin_number = max(
        1,
        total_spins - len(current_window) + 1,
    )

    timeline = pd.DataFrame(
        {
            "Jogada": range(
                first_spin_number,
                total_spins + 1,
            ),
            "Número": current_window,
            "Setor": [
                engine.get_sector(number)
                for number in current_window
            ],
            "Cor": [
                engine.get_color(number)
                for number in current_window
            ],
        }
    )

    timeline_chart = px.scatter(
        timeline,
        x="Jogada",
        y="Setor",
        color="Cor",
        hover_data=["Número"],
        color_discrete_map={
            "Vermelho": "#ed334e",
            "Preto": "#9aa8b7",
            "Verde": "#41d9b5",
        },
    )

    timeline_chart.update_traces(
        marker={
            "size": 11,
            "line": {
                "width": 1,
                "color": "white",
            },
        }
    )

    timeline_chart.update_layout(
        template="plotly_dark",
        height=390,
        title="Sequência recente por setor",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Cor",
    )

    st.plotly_chart(
        timeline_chart,
        use_container_width=True,
    )


# ==========================================================
# ABA: NÚMEROS
# ==========================================================

with numbers_tab:
    frequency = Counter(current_window)

    number_table = pd.DataFrame(
        {
            "Número": list(range(37)),
            "Ocorrências": [
                frequency.get(number, 0)
                for number in range(37)
            ],
            "Cor": [
                engine.get_color(number)
                for number in range(37)
            ],
            "Setor": [
                engine.get_sector(number)
                for number in range(37)
            ],
        }
    ).sort_values(
        [
            "Ocorrências",
            "Número",
        ],
        ascending=[
            False,
            True,
        ],
    )

    maximum_occurrences = max(
        1,
        int(
            number_table["Ocorrências"].max()
        ),
    )

    st.dataframe(
        number_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Número": st.column_config.NumberColumn(
                format="%d",
            ),
            "Ocorrências": (
                st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=maximum_occurrences,
                )
            ),
        },
    )


# ==========================================================
# ABA: AUDITORIA
# ==========================================================

with audit_tab:
    if signal:
        theoretical_coverage = (
            len(signal.covered_numbers)
            / 37
            * 100
        )

        observed_difference = (
            signal.backtest_accuracy
            - theoretical_coverage
        )

        backtest_trials = getattr(
            signal,
            "backtest_trials",
            max(signal.sample_size - 8, 0),
        )

        audit_columns = st.columns(3)

        audit_columns[0].metric(
            "Taxa do backtest",
            f"{signal.backtest_accuracy:.1f}%",
            help=(
                f"Calculada sobre {backtest_trials} "
                "previsões walk-forward."
            ),
        )

        audit_columns[1].metric(
            "Cobertura teórica",
            f"{theoretical_coverage:.1f}%",
        )

        audit_columns[2].metric(
            "Diferença observada",
            f"{observed_difference:+.1f} p.p.",
        )

        st.write(
            "O backtest percorre o histórico sem olhar "
            "o próximo resultado. A leitura é gerada "
            "somente com os dados disponíveis naquele "
            "momento e, então, compara-se o resultado "
            "seguinte com a cobertura calculada."
        )

        st.progress(
            min(
                signal.confidence_score / 100,
                1.0,
            )
        )

        st.caption(
            "Score interno: "
            f"{signal.confidence_score:.1f}/100. "
            "É uma métrica interna de robustez, "
            "não uma probabilidade de acerto futuro."
        )

    else:
        st.info(
            "Adicione mais resultados para "
            "liberar a auditoria."
        )


# ==========================================================
# AVISO FINAL
# ==========================================================

disclaimer_html = """
<div class="disclaimer">
    <strong>Importante:</strong>
    resultados de roleta são independentes e aleatórios.
    Este painel descreve o histórico e não garante vantagem,
    lucro ou previsão do próximo giro.
</div>
"""

st.html(disclaimer_html)

Depois de substituir:

python -m py_compile roleta_pro.py roulette_engine.py

Se não aparecer erro:

streamlit run roleta_pro.py

Caso a aplicação já esteja executando, salve o arquivo com Ctrl + S; o Streamlit normalmente recarrega automaticamente.

analise e melhore o código criado 
Pensou por 2m 56s

Analisei a versão atual e preparei uma versão 2 completa.

Problemas encontrados

O roleta_pro.py publicado ainda usa st.markdown(..., unsafe_allow_html=True) para renderizar o cartão, cabeçalho e aviso. Como o HTML possui indentação, o Streamlit pode interpretá-lo como bloco de código e exibir as tags na tela.

Também existe um problema estatístico: os setores possuem tamanhos diferentes — 7, 10, 8 e 12 números — mas o motor escolhe o setor pelo maior total ponderado bruto. Isso naturalmente favorece setores maiores, mesmo sem existir concentração anormal.

Melhorias aplicadas

A versão 2 inclui:

HTML renderizado com st.html();
código da interface reorganizado em funções;
comparação dos setores corrigida pelo tamanho teórico;
cálculo de Z-score com tamanho efetivo da amostra;
epicentro escolhido pela concentração da vizinhança física;
backtest walk-forward;
intervalo de Wilson de 95%;
validação mais rígida das entradas;
aviso para números inválidos;
exportação do histórico em CSV;
GitHub Actions para testar automaticamente;
14 testes unitários aprovados;
verificação de sintaxe aprovada.
Arquivos completos

Baixar projeto completo em ZIP

Também estão separados:

roleta_pro.py
roulette_engine.py
test_engine.py
README.md
requirements.txt
tests.yml
.gitignore
Como aplicar no GitHub

Substitua:

roleta_pro.py
roulette_engine.py
README.md
requirements.txt
tests/test_engine.py

Adicione:

.gitignore
.github/workflows/tests.yml

No Codespaces, execute:

python -m py_compile roleta_pro.py roulette_engine.py
python -m unittest discover -s tests -v
streamlit run roleta_pro.py

A validação local confirmou a sintaxe e os 14 testes. Não consegui iniciar a interface Streamlit neste ambiente porque o pacote Streamlit não está instalado nele; a execução visual deve ser verificada no seu Codespaces. 

Biblioteca
/
test_engine.py
import unittest

from roulette_engine import EuropeanRouletteEngine


class EuropeanRouletteEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = EuropeanRouletteEngine()

    def test_wheel_contains_all_numbers_once(self) -> None:
        self.assertEqual(len(self.engine.WHEEL), 37)
        self.assertEqual(set(self.engine.WHEEL), set(range(37)))

    def test_sectors_form_exclusive_partition(self) -> None:
        numbers = [
            number
            for sector_numbers in self.engine.SECTORS.values()
            for number in sector_numbers
        ]
        self.assertEqual(len(numbers), 37)
        self.assertEqual(set(numbers), set(range(37)))

    def test_colors(self) -> None:
        self.assertEqual(self.engine.get_color(0), "Verde")
        self.assertEqual(self.engine.get_color(1), "Vermelho")
        self.assertEqual(self.engine.get_color(2), "Preto")

    def test_invalid_number(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.validate_number(37)

        with self.assertRaises(ValueError):
            self.engine.validate_number(True)

        with self.assertRaises(ValueError):
            self.engine.validate_number(1.5)

    def test_sanitize_history(self) -> None:
        clean = self.engine.sanitize_history([0, "1", 37, None, 2])
        self.assertEqual(clean, [0, 1, 2])

    def test_neighbors_wrap_around(self) -> None:
        self.assertEqual(
            self.engine.get_neighbors(0, 2),
            (3, 26, 0, 32, 15),
        )

    def test_radius_is_bounded(self) -> None:
        self.assertEqual(len(self.engine.get_neighbors(0, 100)), 37)

    def test_effective_sample_size(self) -> None:
        self.assertAlmostEqual(
            self.engine.effective_sample_size([1, 1, 1, 1]),
            4.0,
        )

    def test_uniform_wheel_has_no_sector_size_bias(self) -> None:
        statistics = self.engine.sector_statistics(list(self.engine.WHEEL), decay=0.999)

        for values in statistics.values():
            self.assertAlmostEqual(
                values["observed_share_pct"],
                values["expected_share_pct"],
                delta=0.2,
            )

    def test_signal_requires_minimum_sample(self) -> None:
        self.assertIsNone(
            self.engine.build_signal(
                list(range(self.engine.MINIMUM_SAMPLE - 1))
            )
        )

    def test_signal_is_deterministic(self) -> None:
        history = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27,
            13, 36, 11, 30, 8, 23, 10, 5,
        ]
        self.assertEqual(
            self.engine.build_signal(history),
            self.engine.build_signal(history),
        )

    def test_backtest_trials(self) -> None:
        history = list(range(20))
        result = self.engine.backtest(history)
        self.assertEqual(result.trials, 8)

    def test_backtest_baseline_matches_coverage(self) -> None:
        result = self.engine.backtest(list(range(20)), neighbor_radius=2)
        self.assertAlmostEqual(result.baseline_pct, 5 / 37 * 100)

    def test_wilson_interval_contains_observed_rate(self) -> None:
        low, high = self.engine.wilson_interval(5, 10)
        self.assertLessEqual(low, 50)
        self.assertGreaterEqual(high, 50)


if __name__ == "__main__":
    unittest.main()

Biblioteca
/
test_engine.py
import unittest

from roulette_engine import EuropeanRouletteEngine


class EuropeanRouletteEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = EuropeanRouletteEngine()

    def test_wheel_contains_all_numbers_once(self) -> None:
        self.assertEqual(len(self.engine.WHEEL), 37)
        self.assertEqual(set(self.engine.WHEEL), set(range(37)))

    def test_sectors_form_exclusive_partition(self) -> None:
        numbers = [
            number
            for sector_numbers in self.engine.SECTORS.values()
            for number in sector_numbers
        ]
        self.assertEqual(len(numbers), 37)
        self.assertEqual(set(numbers), set(range(37)))

    def test_colors(self) -> None:
        self.assertEqual(self.engine.get_color(0), "Verde")
        self.assertEqual(self.engine.get_color(1), "Vermelho")
        self.assertEqual(self.engine.get_color(2), "Preto")

    def test_invalid_number(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.validate_number(37)

        with self.assertRaises(ValueError):
            self.engine.validate_number(True)

        with self.assertRaises(ValueError):
            self.engine.validate_number(1.5)

    def test_sanitize_history(self) -> None:
        clean = self.engine.sanitize_history([0, "1", 37, None, 2])
        self.assertEqual(clean, [0, 1, 2])

    def test_neighbors_wrap_around(self) -> None:
        self.assertEqual(
            self.engine.get_neighbors(0, 2),
            (3, 26, 0, 32, 15),
        )

    def test_radius_is_bounded(self) -> None:
        self.assertEqual(len(self.engine.get_neighbors(0, 100)), 37)

    def test_effective_sample_size(self) -> None:
        self.assertAlmostEqual(
            self.engine.effective_sample_size([1, 1, 1, 1]),
            4.0,
        )

    def test_uniform_wheel_has_no_sector_size_bias(self) -> None:
        statistics = self.engine.sector_statistics(list(self.engine.WHEEL), decay=0.999)

        for values in statistics.values():
            self.assertAlmostEqual(
                values["observed_share_pct"],
                values["expected_share_pct"],
                delta=0.2,
            )

    def test_signal_requires_minimum_sample(self) -> None:
        self.assertIsNone(
            self.engine.build_signal(
                list(range(self.engine.MINIMUM_SAMPLE - 1))
            )
        )

    def test_signal_is_deterministic(self) -> None:
        history = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27,
            13, 36, 11, 30, 8, 23, 10, 5,
        ]
        self.assertEqual(
            self.engine.build_signal(history),
            self.engine.build_signal(history),
        )

    def test_backtest_trials(self) -> None:
        history = list(range(20))
        result = self.engine.backtest(history)
        self.assertEqual(result.trials, 8)

    def test_backtest_baseline_matches_coverage(self) -> None:
        result = self.engine.backtest(list(range(20)), neighbor_radius=2)
        self.assertAlmostEqual(result.baseline_pct, 5 / 37 * 100)

    def test_wilson_interval_contains_observed_rate(self) -> None:
        low, high = self.engine.wilson_interval(5, 10)
        self.assertLessEqual(low, 50)
        self.assertGreaterEqual(high, 50)


if __name__ == "__main__":
    unittest.main()
