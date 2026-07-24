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
roleta_pro.py
from __future__ import annotations

from collections import Counter
from html import escape
import re
from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from roulette_engine import EuropeanRouletteEngine, SignalResult


APP_TITLE = "Roulette Lens"
MAX_HISTORY = 500

COLOR_MAP = {
    "Vermelho": "#ed334e",
    "Preto": "#9aa8b7",
    "Verde": "#41d9b5",
}

SECTOR_COLORS = {
    "Jeu Zéro": "#41d9b5",
    "Voisins lateral": "#77a7ff",
    "Orphelins": "#f5c76b",
    "Tiers": "#d17cff",
}


@st.cache_resource
def get_engine() -> EuropeanRouletteEngine:
    return EuropeanRouletteEngine()


engine = get_engine()


def initialize_session() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("input_feedback", "")


def parse_numbers(text: str) -> tuple[list[int], list[str]]:
    tokens = re.findall(r"[-+]?\d+", text)
    valid: list[int] = []
    invalid: list[str] = []

    for token in tokens:
        try:
            valid.append(engine.validate_number(int(token)))
        except ValueError:
            invalid.append(token)

    return valid, invalid


def add_numbers(numbers: Iterable[int]) -> None:
    validated = [engine.validate_number(number) for number in numbers]
    st.session_state.history.extend(validated)
    st.session_state.history = st.session_state.history[-MAX_HISTORY:]


def number_badge(number: int) -> str:
    css_class = {
        "Vermelho": "ball-red",
        "Preto": "ball-black",
        "Verde": "ball-green",
    }[engine.get_color(number)]

    return f"<span class='number-ball {css_class}'>{number}</span>"


def render_styles() -> None:
    st.html(
        """
        <style>
        :root {
            --bg: #06101d;
            --surface: rgba(14, 27, 44, 0.92);
            --surface-2: rgba(19, 38, 61, 0.96);
            --border: rgba(148, 163, 184, 0.18);
            --text: #edf6ff;
            --muted: #9eb0c4;
            --accent: #41d9b5;
            --accent-2: #77a7ff;
            --gold: #f5c76b;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(65, 217, 181, .12), transparent 30rem),
                radial-gradient(circle at 88% 12%, rgba(119, 167, 255, .11), transparent 28rem),
                linear-gradient(145deg, #040a12 0%, var(--bg) 58%, #081526 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071220 0%, #0b1a2c 100%);
            border-right: 1px solid var(--border);
        }

        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 17px;
            padding: 15px 17px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, .18);
        }

        .hero,
        .signal-card,
        .method-card {
            border: 1px solid var(--border);
            border-radius: 23px;
            box-shadow: 0 20px 52px rgba(0, 0, 0, .22);
        }

        .hero {
            padding: 26px 29px;
            margin-bottom: 20px;
            background:
                linear-gradient(120deg, rgba(65, 217, 181, .13), rgba(119, 167, 255, .07)),
                var(--surface);
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2.15rem, 4vw, 3.65rem);
            letter-spacing: -.05em;
        }

        .hero p,
        .signal-note,
        .muted {
            color: var(--muted);
        }

        .eyebrow {
            margin-bottom: 7px;
            color: var(--accent);
            font-size: .72rem;
            font-weight: 850;
            letter-spacing: .16em;
        }

        .signal-card {
            min-height: 350px;
            padding: 25px;
            border-color: rgba(65, 217, 181, .28);
            background:
                linear-gradient(145deg, rgba(65, 217, 181, .13), rgba(119, 167, 255, .05)),
                var(--surface-2);
        }

        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
        }

        .signal-header h2 {
            margin: 0;
            font-size: 1.95rem;
        }

        .evidence-pill {
            display: inline-flex;
            white-space: nowrap;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: .77rem;
            font-weight: 850;
        }

        .evidence-forte {
            background: rgba(65, 217, 181, .16);
            color: #7ff4d8;
        }

        .evidence-moderada {
            background: rgba(245, 199, 107, .16);
            color: #ffe09d;
        }

        .evidence-fraca {
            background: rgba(255, 101, 119, .14);
            color: #ff9baa;
        }

        .ball-row {
            display: flex;
            flex-wrap: wrap;
            gap: 9px;
            margin: 22px 0;
        }

        .number-ball {
            display: inline-flex;
            width: 46px;
            height: 46px;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(255, 255, 255, .27);
            border-radius: 50%;
            font-weight: 900;
            box-shadow:
                inset 0 0 0 2px rgba(0, 0, 0, .15),
                0 7px 18px rgba(0, 0, 0, .23);
        }

        .ball-red {
            background: linear-gradient(145deg, #ed334e, #9f142a);
            color: white;
        }

        .ball-black {
            background: linear-gradient(145deg, #293648, #080c12);
            color: white;
        }

        .ball-green {
            background: linear-gradient(145deg, #31c68c, #087451);
            color: white;
        }

        .signal-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 9px;
            margin: 11px 0 17px;
        }

        .signal-grid > div {
            padding: 13px;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: rgba(6, 15, 27, .61);
        }

        .signal-grid span,
        .signal-grid small {
            display: block;
            color: var(--muted);
            font-size: .75rem;
        }

        .signal-grid strong {
            font-size: 1.15rem;
        }

        .history-box {
            max-height: 220px;
            overflow-y: auto;
            padding: 13px;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: rgba(3, 9, 17, .65);
            line-height: 2.45;
        }

        .method-card {
            padding: 18px 20px;
            background: var(--surface);
        }

        .disclaimer {
            margin-top: 18px;
            padding: 13px 16px;
            border-left: 3px solid var(--gold);
            border-radius: 8px;
            background: rgba(245, 199, 107, .08);
            color: #d8c79f;
            font-size: .89rem;
        }

        div.stButton > button {
            border: 1px solid var(--border);
            border-radius: 11px;
            transition: transform .15s ease, border-color .15s ease;
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(65, 217, 181, .55);
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
    )


def render_sidebar() -> tuple[int, float, int]:
    with st.sidebar:
        st.markdown(f"## 🎯 {APP_TITLE}")
        st.caption("Análise descritiva da roleta europeia")

        analysis_window = st.slider(
            "Janela de análise",
            min_value=12,
            max_value=200,
            value=48,
            help="Quantidade de resultados recentes considerada.",
        )
        decay = st.slider(
            "Peso da recência",
            min_value=0.75,
            max_value=0.99,
            value=0.92,
            step=0.01,
            help="Valores menores reduzem mais rapidamente o peso dos resultados antigos.",
        )
        neighbor_radius = st.select_slider(
            "Raio físico",
            options=[1, 2, 3],
            value=2,
            help="Quantidade de vizinhos cobertos de cada lado do epicentro.",
        )

        st.divider()
        keyboard_tab, text_tab = st.tabs(["Mesa", "Texto"])

        with keyboard_tab:
            if st.button("0 🟢", use_container_width=True, key="number_0"):
                add_numbers([0])
                st.rerun()

            for row in range(12):
                columns = st.columns(3)

                for offset, column in enumerate(columns, start=1):
                    number = row * 3 + offset
                    icon = "🔴" if engine.get_color(number) == "Vermelho" else "⚫"

                    with column:
                        if st.button(
                            f"{number} {icon}",
                            use_container_width=True,
                            key=f"number_{number}",
                        ):
                            add_numbers([number])
                            st.rerun()

        with text_tab:
            with st.form("sequence_form", clear_on_submit=True):
                raw_text = st.text_area(
                    "Cole uma sequência",
                    placeholder="17, 0, 32, 21, 8",
                    height=105,
                )
                submitted = st.form_submit_button(
                    "Adicionar sequência",
                    use_container_width=True,
                )

            if submitted:
                valid, invalid = parse_numbers(raw_text)

                if valid:
                    add_numbers(valid)

                if invalid:
                    st.session_state.input_feedback = (
                        "Ignorados por estarem fora de 0–36: "
                        + ", ".join(invalid)
                    )
                elif valid:
                    st.session_state.input_feedback = (
                        f"{len(valid)} resultado(s) adicionado(s)."
                    )
                else:
                    st.session_state.input_feedback = "Nenhum número encontrado."

                st.rerun()

            if st.session_state.input_feedback:
                st.caption(st.session_state.input_feedback)

        st.divider()
        st.markdown("### Histórico")

        if st.session_state.history:
            badges = " ".join(
                number_badge(number)
                for number in st.session_state.history[-60:]
            )
            st.html(f"<div class='history-box'>{badges}</div>")
            st.caption(f"{len(st.session_state.history)} resultados na sessão")

            undo_col, clear_col = st.columns(2)

            with undo_col:
                if st.button("↩ Desfazer", use_container_width=True):
                    st.session_state.history.pop()
                    st.rerun()

            with clear_col:
                if st.button("Limpar", type="primary", use_container_width=True):
                    st.session_state.history = []
                    st.session_state.input_feedback = ""
                    st.rerun()

            history_csv = pd.DataFrame(
                {"resultado": st.session_state.history}
            ).to_csv(index=False)

            st.download_button(
                "Baixar histórico CSV",
                data=history_csv,
                file_name="roulette_lens_historico.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("Adicione resultados para iniciar.")

    return analysis_window, decay, neighbor_radius


def render_hero() -> None:
    st.html(
        """
        <section class="hero">
            <div class="eyebrow">EUROPEAN ROULETTE ANALYTICS</div>
            <h1>Roulette Lens</h1>
            <p>
                Painel auditável para comparar concentração recente, tamanho
                teórico dos setores e desempenho walk-forward da regra.
            </p>
        </section>
        """
    )


def render_signal_card(signal: SignalResult) -> None:
    pill_class = {
        "Forte": "evidence-forte",
        "Moderada": "evidence-moderada",
        "Fraca": "evidence-fraca",
    }[signal.evidence_label]

    covered = "".join(
        number_badge(number)
        for number in signal.covered_numbers
    )

    st.html(
        f"""
        <section class="signal-card">
            <div class="eyebrow">LEITURA DESCRITIVA</div>

            <div class="signal-header">
                <div>
                    <h2>{escape(signal.target_sector)}</h2>
                    <p class="muted">
                        Epicentro físico: <strong>{signal.epicenter}</strong>
                    </p>
                </div>

                <span class="evidence-pill {pill_class}">
                    Evidência {escape(signal.evidence_label.lower())}
                </span>
            </div>

            <div class="ball-row">{covered}</div>

            <div class="signal-grid">
                <div>
                    <span>Participação recente</span>
                    <strong>{signal.sector_share_pct:.1f}%</strong>
                    <small>Esperado: {signal.sector_expected_pct:.1f}%</small>
                </div>

                <div>
                    <span>Backtest</span>
                    <strong>{signal.backtest.accuracy_pct:.1f}%</strong>
                    <small>
                        {signal.backtest.hits}/{signal.backtest.trials} acertos
                    </small>
                </div>

                <div>
                    <span>Score de evidência</span>
                    <strong>{signal.evidence_score:.1f}/100</strong>
                    <small>n efetivo: {signal.effective_sample_size:.1f}</small>
                </div>
            </div>

            <p class="signal-note">{escape(signal.explanation)}</p>
        </section>
        """
    )


def build_sector_frame(
    history: list[int],
    decay: float,
) -> pd.DataFrame:
    statistics = engine.sector_statistics(history, decay)

    return pd.DataFrame(
        [
            {
                "Setor": sector,
                "Observado": values["observed_share_pct"],
                "Esperado": values["expected_share_pct"],
                "Z-score": values["z_score"],
            }
            for sector, values in statistics.items()
        ]
    )


def render_dashboard(
    history: list[int],
    analysis_window: int,
    decay: float,
    neighbor_radius: int,
) -> None:
    current_window = history[-analysis_window:]
    signal = engine.build_signal(
        current_window,
        decay,
        neighbor_radius,
    )

    red_count = sum(engine.get_color(number) == "Vermelho" for number in current_window)
    black_count = sum(engine.get_color(number) == "Preto" for number in current_window)
    zero_count = current_window.count(0)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Resultados", len(history))
    metric_columns[1].metric("Janela ativa", len(current_window))
    metric_columns[2].metric("Vermelho / Preto", f"{red_count} / {black_count}")
    metric_columns[3].metric("Zeros", zero_count)

    st.write("")

    left_col, right_col = st.columns([1.08, 0.92], gap="large")

    with left_col:
        if signal:
            render_signal_card(signal)
        else:
            remaining = engine.MINIMUM_SAMPLE - len(current_window)
            st.warning(
                f"Adicione mais {remaining} resultado(s) para liberar a leitura."
            )

    with right_col:
        sector_frame = build_sector_frame(current_window, decay)
        melted = sector_frame.melt(
            id_vars=["Setor"],
            value_vars=["Observado", "Esperado"],
            var_name="Referência",
            value_name="Participação (%)",
        )

        sector_chart = px.bar(
            melted,
            x="Participação (%)",
            y="Setor",
            color="Referência",
            barmode="group",
            orientation="h",
            color_discrete_map={
                "Observado": "#41d9b5",
                "Esperado": "#596b80",
            },
            text_auto=".1f",
        )
        sector_chart.update_layout(
            title="Participação observada × esperada",
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=55, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            yaxis_title="",
        )
        st.plotly_chart(sector_chart, use_container_width=True)

    overview_tab, numbers_tab, audit_tab, method_tab = st.tabs(
        ["Visão geral", "Números", "Auditoria", "Método"]
    )

    with overview_tab:
        start_spin = max(1, len(history) - len(current_window) + 1)
        timeline = pd.DataFrame(
            {
                "Jogada": range(start_spin, len(history) + 1),
                "Número": current_window,
                "Setor": [engine.get_sector(number) for number in current_window],
                "Cor": [engine.get_color(number) for number in current_window],
            }
        )

        timeline_chart = px.scatter(
            timeline,
            x="Jogada",
            y="Setor",
            color="Cor",
            hover_data=["Número"],
            color_discrete_map=COLOR_MAP,
        )
        timeline_chart.update_traces(
            marker=dict(size=11, line=dict(width=1, color="white"))
        )
        timeline_chart.update_layout(
            title="Sequência recente por setor",
            template="plotly_dark",
            height=390,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="Cor",
        )
        st.plotly_chart(timeline_chart, use_container_width=True)

    with numbers_tab:
        frequency = Counter(current_window)
        expected_count = len(current_window) / 37

        number_table = pd.DataFrame(
            {
                "Número": list(range(37)),
                "Ocorrências": [
                    frequency.get(number, 0)
                    for number in range(37)
                ],
                "Esperado": [expected_count] * 37,
                "Diferença": [
                    frequency.get(number, 0) - expected_count
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
            ["Ocorrências", "Número"],
            ascending=[False, True],
        )

        st.dataframe(
            number_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Número": st.column_config.NumberColumn(format="%d"),
                "Ocorrências": st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=max(1, int(number_table["Ocorrências"].max())),
                ),
                "Esperado": st.column_config.NumberColumn(format="%.2f"),
                "Diferença": st.column_config.NumberColumn(format="%+.2f"),
            },
        )

    with audit_tab:
        if signal:
            audit_columns = st.columns(4)
            audit_columns[0].metric(
                "Taxa walk-forward",
                f"{signal.backtest.accuracy_pct:.1f}%",
            )
            audit_columns[1].metric(
                "Cobertura aleatória",
                f"{signal.backtest.baseline_pct:.1f}%",
            )
            audit_columns[2].metric(
                "Diferença",
                f"{signal.backtest.lift_pct_points:+.1f} p.p.",
            )
            audit_columns[3].metric(
                "Tentativas",
                signal.backtest.trials,
            )

            st.markdown(
                "**Intervalo de Wilson de 95%:** "
                f"{signal.backtest.wilson_low_pct:.1f}% a "
                f"{signal.backtest.wilson_high_pct:.1f}%."
            )

            st.progress(min(signal.evidence_score / 100, 1.0))
            st.caption(
                "O score usa tamanho efetivo da amostra, desvio normalizado do "
                "setor e o limite inferior do intervalo do backtest. Ele não é "
                "probabilidade de acerto futuro."
            )
        else:
            st.info("A auditoria é liberada com a leitura principal.")

    with method_tab:
        st.html(
            """
            <div class="method-card">
                <strong>O que foi corrigido no método</strong>
                <p class="muted">
                    Os setores têm tamanhos diferentes. Por isso, a versão atual
                    compara a participação observada com a participação teórica
                    de cada setor, em vez de escolher simplesmente o setor com
                    mais ocorrências.
                </p>
                <p class="muted">
                    O epicentro também não é mais o número isolado mais repetido:
                    ele é a posição cuja vizinhança física acumula maior peso
                    recente dentro do setor selecionado.
                </p>
            </div>
            """
        )


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initialize_session()
    render_styles()

    analysis_window, decay, neighbor_radius = render_sidebar()
    render_hero()

    if not st.session_state.history:
        st.info("Comece adicionando resultados no painel lateral.")
        return

    render_dashboard(
        st.session_state.history,
        analysis_window,
        decay,
        neighbor_radius,
    )

    st.html(
        """
        <div class="disclaimer">
            <strong>Importante:</strong> giros de roleta são independentes e
            aleatórios. O painel descreve o histórico e não garante vantagem,
            lucro ou previsão do próximo resultado.
        </div>
        """
    )


if __name__ == "__main__":
    main()

Biblioteca
/
roleta_pro.py
from __future__ import annotations

from collections import Counter
from html import escape
import re
from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from roulette_engine import EuropeanRouletteEngine, SignalResult


APP_TITLE = "Roulette Lens"
MAX_HISTORY = 500

COLOR_MAP = {
    "Vermelho": "#ed334e",
    "Preto": "#9aa8b7",
    "Verde": "#41d9b5",
}

SECTOR_COLORS = {
    "Jeu Zéro": "#41d9b5",
    "Voisins lateral": "#77a7ff",
    "Orphelins": "#f5c76b",
    "Tiers": "#d17cff",
}


@st.cache_resource
def get_engine() -> EuropeanRouletteEngine:
    return EuropeanRouletteEngine()


engine = get_engine()


def initialize_session() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("input_feedback", "")


def parse_numbers(text: str) -> tuple[list[int], list[str]]:
    tokens = re.findall(r"[-+]?\d+", text)
    valid: list[int] = []
    invalid: list[str] = []

    for token in tokens:
        try:
            valid.append(engine.validate_number(int(token)))
        except ValueError:
            invalid.append(token)

    return valid, invalid


def add_numbers(numbers: Iterable[int]) -> None:
    validated = [engine.validate_number(number) for number in numbers]
    st.session_state.history.extend(validated)
    st.session_state.history = st.session_state.history[-MAX_HISTORY:]


def number_badge(number: int) -> str:
    css_class = {
        "Vermelho": "ball-red",
        "Preto": "ball-black",
        "Verde": "ball-green",
    }[engine.get_color(number)]

    return f"<span class='number-ball {css_class}'>{number}</span>"


def render_styles() -> None:
    st.html(
        """
        <style>
        :root {
            --bg: #06101d;
            --surface: rgba(14, 27, 44, 0.92);
            --surface-2: rgba(19, 38, 61, 0.96);
            --border: rgba(148, 163, 184, 0.18);
            --text: #edf6ff;
            --muted: #9eb0c4;
            --accent: #41d9b5;
            --accent-2: #77a7ff;
            --gold: #f5c76b;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(65, 217, 181, .12), transparent 30rem),
                radial-gradient(circle at 88% 12%, rgba(119, 167, 255, .11), transparent 28rem),
                linear-gradient(145deg, #040a12 0%, var(--bg) 58%, #081526 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #071220 0%, #0b1a2c 100%);
            border-right: 1px solid var(--border);
        }

        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 17px;
            padding: 15px 17px;
            box-shadow: 0 12px 32px rgba(0, 0, 0, .18);
        }

        .hero,
        .signal-card,
        .method-card {
            border: 1px solid var(--border);
            border-radius: 23px;
            box-shadow: 0 20px 52px rgba(0, 0, 0, .22);
        }

        .hero {
            padding: 26px 29px;
            margin-bottom: 20px;
            background:
                linear-gradient(120deg, rgba(65, 217, 181, .13), rgba(119, 167, 255, .07)),
                var(--surface);
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(2.15rem, 4vw, 3.65rem);
            letter-spacing: -.05em;
        }

        .hero p,
        .signal-note,
        .muted {
            color: var(--muted);
        }

        .eyebrow {
            margin-bottom: 7px;
            color: var(--accent);
            font-size: .72rem;
            font-weight: 850;
            letter-spacing: .16em;
        }

        .signal-card {
            min-height: 350px;
            padding: 25px;
            border-color: rgba(65, 217, 181, .28);
            background:
                linear-gradient(145deg, rgba(65, 217, 181, .13), rgba(119, 167, 255, .05)),
                var(--surface-2);
        }

        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
        }

        .signal-header h2 {
            margin: 0;
            font-size: 1.95rem;
        }

        .evidence-pill {
            display: inline-flex;
            white-space: nowrap;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: .77rem;
            font-weight: 850;
        }

        .evidence-forte {
            background: rgba(65, 217, 181, .16);
            color: #7ff4d8;
        }

        .evidence-moderada {
            background: rgba(245, 199, 107, .16);
            color: #ffe09d;
        }

        .evidence-fraca {
            background: rgba(255, 101, 119, .14);
            color: #ff9baa;
        }

        .ball-row {
            display: flex;
            flex-wrap: wrap;
            gap: 9px;
            margin: 22px 0;
        }

        .number-ball {
            display: inline-flex;
            width: 46px;
            height: 46px;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(255, 255, 255, .27);
            border-radius: 50%;
            font-weight: 900;
            box-shadow:
                inset 0 0 0 2px rgba(0, 0, 0, .15),
                0 7px 18px rgba(0, 0, 0, .23);
        }

        .ball-red {
            background: linear-gradient(145deg, #ed334e, #9f142a);
            color: white;
        }

        .ball-black {
            background: linear-gradient(145deg, #293648, #080c12);
            color: white;
        }

        .ball-green {
            background: linear-gradient(145deg, #31c68c, #087451);
            color: white;
        }

        .signal-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 9px;
            margin: 11px 0 17px;
        }

        .signal-grid > div {
            padding: 13px;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: rgba(6, 15, 27, .61);
        }

        .signal-grid span,
        .signal-grid small {
            display: block;
            color: var(--muted);
            font-size: .75rem;
        }

        .signal-grid strong {
            font-size: 1.15rem;
        }

        .history-box {
            max-height: 220px;
            overflow-y: auto;
            padding: 13px;
            border: 1px solid var(--border);
            border-radius: 15px;
            background: rgba(3, 9, 17, .65);
            line-height: 2.45;
        }

        .method-card {
            padding: 18px 20px;
            background: var(--surface);
        }

        .disclaimer {
            margin-top: 18px;
            padding: 13px 16px;
            border-left: 3px solid var(--gold);
            border-radius: 8px;
            background: rgba(245, 199, 107, .08);
            color: #d8c79f;
            font-size: .89rem;
        }

        div.stButton > button {
            border: 1px solid var(--border);
            border-radius: 11px;
            transition: transform .15s ease, border-color .15s ease;
        }

        div.stButton > button:hover {
            transform: translateY(-1px);
            border-color: rgba(65, 217, 181, .55);
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
    )


def render_sidebar() -> tuple[int, float, int]:
    with st.sidebar:
        st.markdown(f"## 🎯 {APP_TITLE}")
        st.caption("Análise descritiva da roleta europeia")

        analysis_window = st.slider(
            "Janela de análise",
            min_value=12,
            max_value=200,
            value=48,
            help="Quantidade de resultados recentes considerada.",
        )
        decay = st.slider(
            "Peso da recência",
            min_value=0.75,
            max_value=0.99,
            value=0.92,
            step=0.01,
            help="Valores menores reduzem mais rapidamente o peso dos resultados antigos.",
        )
        neighbor_radius = st.select_slider(
            "Raio físico",
            options=[1, 2, 3],
            value=2,
            help="Quantidade de vizinhos cobertos de cada lado do epicentro.",
        )

        st.divider()
        keyboard_tab, text_tab = st.tabs(["Mesa", "Texto"])

        with keyboard_tab:
            if st.button("0 🟢", use_container_width=True, key="number_0"):
                add_numbers([0])
                st.rerun()

            for row in range(12):
                columns = st.columns(3)

                for offset, column in enumerate(columns, start=1):
                    number = row * 3 + offset
                    icon = "🔴" if engine.get_color(number) == "Vermelho" else "⚫"

                    with column:
                        if st.button(
                            f"{number} {icon}",
                            use_container_width=True,
                            key=f"number_{number}",
                        ):
                            add_numbers([number])
                            st.rerun()

        with text_tab:
            with st.form("sequence_form", clear_on_submit=True):
                raw_text = st.text_area(
                    "Cole uma sequência",
                    placeholder="17, 0, 32, 21, 8",
                    height=105,
                )
                submitted = st.form_submit_button(
                    "Adicionar sequência",
                    use_container_width=True,
                )

            if submitted:
                valid, invalid = parse_numbers(raw_text)

                if valid:
                    add_numbers(valid)

                if invalid:
                    st.session_state.input_feedback = (
                        "Ignorados por estarem fora de 0–36: "
                        + ", ".join(invalid)
                    )
                elif valid:
                    st.session_state.input_feedback = (
                        f"{len(valid)} resultado(s) adicionado(s)."
                    )
                else:
                    st.session_state.input_feedback = "Nenhum número encontrado."

                st.rerun()

            if st.session_state.input_feedback:
                st.caption(st.session_state.input_feedback)

        st.divider()
        st.markdown("### Histórico")

        if st.session_state.history:
            badges = " ".join(
                number_badge(number)
                for number in st.session_state.history[-60:]
            )
            st.html(f"<div class='history-box'>{badges}</div>")
            st.caption(f"{len(st.session_state.history)} resultados na sessão")

            undo_col, clear_col = st.columns(2)

            with undo_col:
                if st.button("↩ Desfazer", use_container_width=True):
                    st.session_state.history.pop()
                    st.rerun()

            with clear_col:
                if st.button("Limpar", type="primary", use_container_width=True):
                    st.session_state.history = []
                    st.session_state.input_feedback = ""
                    st.rerun()

            history_csv = pd.DataFrame(
                {"resultado": st.session_state.history}
            ).to_csv(index=False)

            st.download_button(
                "Baixar histórico CSV",
                data=history_csv,
                file_name="roulette_lens_historico.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.info("Adicione resultados para iniciar.")

    return analysis_window, decay, neighbor_radius


def render_hero() -> None:
    st.html(
        """
        <section class="hero">
            <div class="eyebrow">EUROPEAN ROULETTE ANALYTICS</div>
            <h1>Roulette Lens</h1>
            <p>
                Painel auditável para comparar concentração recente, tamanho
                teórico dos setores e desempenho walk-forward da regra.
            </p>
        </section>
        """
    )


def render_signal_card(signal: SignalResult) -> None:
    pill_class = {
        "Forte": "evidence-forte",
        "Moderada": "evidence-moderada",
        "Fraca": "evidence-fraca",
    }[signal.evidence_label]

    covered = "".join(
        number_badge(number)
        for number in signal.covered_numbers
    )

    st.html(
        f"""
        <section class="signal-card">
            <div class="eyebrow">LEITURA DESCRITIVA</div>

            <div class="signal-header">
                <div>
                    <h2>{escape(signal.target_sector)}</h2>
                    <p class="muted">
                        Epicentro físico: <strong>{signal.epicenter}</strong>
                    </p>
                </div>

                <span class="evidence-pill {pill_class}">
                    Evidência {escape(signal.evidence_label.lower())}
                </span>
            </div>

            <div class="ball-row">{covered}</div>

            <div class="signal-grid">
                <div>
                    <span>Participação recente</span>
                    <strong>{signal.sector_share_pct:.1f}%</strong>
                    <small>Esperado: {signal.sector_expected_pct:.1f}%</small>
                </div>

                <div>
                    <span>Backtest</span>
                    <strong>{signal.backtest.accuracy_pct:.1f}%</strong>
                    <small>
                        {signal.backtest.hits}/{signal.backtest.trials} acertos
                    </small>
                </div>

                <div>
                    <span>Score de evidência</span>
                    <strong>{signal.evidence_score:.1f}/100</strong>
                    <small>n efetivo: {signal.effective_sample_size:.1f}</small>
                </div>
            </div>

            <p class="signal-note">{escape(signal.explanation)}</p>
        </section>
        """
    )


def build_sector_frame(
    history: list[int],
    decay: float,
) -> pd.DataFrame:
    statistics = engine.sector_statistics(history, decay)

    return pd.DataFrame(
        [
            {
                "Setor": sector,
                "Observado": values["observed_share_pct"],
                "Esperado": values["expected_share_pct"],
                "Z-score": values["z_score"],
            }
            for sector, values in statistics.items()
        ]
    )


def render_dashboard(
    history: list[int],
    analysis_window: int,
    decay: float,
    neighbor_radius: int,
) -> None:
    current_window = history[-analysis_window:]
    signal = engine.build_signal(
        current_window,
        decay,
        neighbor_radius,
    )

    red_count = sum(engine.get_color(number) == "Vermelho" for number in current_window)
    black_count = sum(engine.get_color(number) == "Preto" for number in current_window)
    zero_count = current_window.count(0)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Resultados", len(history))
    metric_columns[1].metric("Janela ativa", len(current_window))
    metric_columns[2].metric("Vermelho / Preto", f"{red_count} / {black_count}")
    metric_columns[3].metric("Zeros", zero_count)

    st.write("")

    left_col, right_col = st.columns([1.08, 0.92], gap="large")

    with left_col:
        if signal:
            render_signal_card(signal)
        else:
            remaining = engine.MINIMUM_SAMPLE - len(current_window)
            st.warning(
                f"Adicione mais {remaining} resultado(s) para liberar a leitura."
            )

    with right_col:
        sector_frame = build_sector_frame(current_window, decay)
        melted = sector_frame.melt(
            id_vars=["Setor"],
            value_vars=["Observado", "Esperado"],
            var_name="Referência",
            value_name="Participação (%)",
        )

        sector_chart = px.bar(
            melted,
            x="Participação (%)",
            y="Setor",
            color="Referência",
            barmode="group",
            orientation="h",
            color_discrete_map={
                "Observado": "#41d9b5",
                "Esperado": "#596b80",
            },
            text_auto=".1f",
        )
        sector_chart.update_layout(
            title="Participação observada × esperada",
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=55, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="",
            yaxis_title="",
        )
        st.plotly_chart(sector_chart, use_container_width=True)

    overview_tab, numbers_tab, audit_tab, method_tab = st.tabs(
        ["Visão geral", "Números", "Auditoria", "Método"]
    )

    with overview_tab:
        start_spin = max(1, len(history) - len(current_window) + 1)
        timeline = pd.DataFrame(
            {
                "Jogada": range(start_spin, len(history) + 1),
                "Número": current_window,
                "Setor": [engine.get_sector(number) for number in current_window],
                "Cor": [engine.get_color(number) for number in current_window],
            }
        )

        timeline_chart = px.scatter(
            timeline,
            x="Jogada",
            y="Setor",
            color="Cor",
            hover_data=["Número"],
            color_discrete_map=COLOR_MAP,
        )
        timeline_chart.update_traces(
            marker=dict(size=11, line=dict(width=1, color="white"))
        )
        timeline_chart.update_layout(
            title="Sequência recente por setor",
            template="plotly_dark",
            height=390,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend_title_text="Cor",
        )
        st.plotly_chart(timeline_chart, use_container_width=True)

    with numbers_tab:
        frequency = Counter(current_window)
        expected_count = len(current_window) / 37

        number_table = pd.DataFrame(
            {
                "Número": list(range(37)),
                "Ocorrências": [
                    frequency.get(number, 0)
                    for number in range(37)
                ],
                "Esperado": [expected_count] * 37,
                "Diferença": [
                    frequency.get(number, 0) - expected_count
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
            ["Ocorrências", "Número"],
            ascending=[False, True],
        )

        st.dataframe(
            number_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Número": st.column_config.NumberColumn(format="%d"),
                "Ocorrências": st.column_config.ProgressColumn(
                    min_value=0,
                    max_value=max(1, int(number_table["Ocorrências"].max())),
                ),
                "Esperado": st.column_config.NumberColumn(format="%.2f"),
                "Diferença": st.column_config.NumberColumn(format="%+.2f"),
            },
        )

    with audit_tab:
        if signal:
            audit_columns = st.columns(4)
            audit_columns[0].metric(
                "Taxa walk-forward",
                f"{signal.backtest.accuracy_pct:.1f}%",
            )
            audit_columns[1].metric(
                "Cobertura aleatória",
                f"{signal.backtest.baseline_pct:.1f}%",
            )
            audit_columns[2].metric(
                "Diferença",
                f"{signal.backtest.lift_pct_points:+.1f} p.p.",
            )
            audit_columns[3].metric(
                "Tentativas",
                signal.backtest.trials,
            )

            st.markdown(
                "**Intervalo de Wilson de 95%:** "
                f"{signal.backtest.wilson_low_pct:.1f}% a "
                f"{signal.backtest.wilson_high_pct:.1f}%."
            )

            st.progress(min(signal.evidence_score / 100, 1.0))
            st.caption(
                "O score usa tamanho efetivo da amostra, desvio normalizado do "
                "setor e o limite inferior do intervalo do backtest. Ele não é "
                "probabilidade de acerto futuro."
            )
        else:
            st.info("A auditoria é liberada com a leitura principal.")

    with method_tab:
        st.html(
            """
            <div class="method-card">
                <strong>O que foi corrigido no método</strong>
                <p class="muted">
                    Os setores têm tamanhos diferentes. Por isso, a versão atual
                    compara a participação observada com a participação teórica
                    de cada setor, em vez de escolher simplesmente o setor com
                    mais ocorrências.
                </p>
                <p class="muted">
                    O epicentro também não é mais o número isolado mais repetido:
                    ele é a posição cuja vizinhança física acumula maior peso
                    recente dentro do setor selecionado.
                </p>
            </div>
            """
        )


def main() -> None:
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initialize_session()
    render_styles()

    analysis_window, decay, neighbor_radius = render_sidebar()
    render_hero()

    if not st.session_state.history:
        st.info("Comece adicionando resultados no painel lateral.")
        return

    render_dashboard(
        st.session_state.history,
        analysis_window,
        decay,
        neighbor_radius,
    )

    st.html(
        """
        <div class="disclaimer">
            <strong>Importante:</strong> giros de roleta são independentes e
            aleatórios. O painel descreve o histórico e não garante vantagem,
            lucro ou previsão do próximo resultado.
        </div>
        """
    )


if __name__ == "__main__":
    main()
