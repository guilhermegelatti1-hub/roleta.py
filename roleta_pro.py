from __future__ import annotations

from collections import Counter
from html import escape
import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from roulette_engine import EuropeanRouletteEngine, SignalResult


st.set_page_config(
    page_title="Roulette Lens",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

engine = EuropeanRouletteEngine()

if "history" not in st.session_state:
    st.session_state.history = []


def add_number(number: int) -> None:
    st.session_state.history.append(number)
    st.session_state.history = st.session_state.history[-500:]


def submit_text_input() -> None:
    raw = st.session_state.get("quick_input", "")
    numbers = [int(value) for value in re.findall(r"(?<!\d)(?:[0-9]|[12][0-9]|3[0-6])(?!\d)", raw)]
    for number in numbers:
        add_number(number)
    st.session_state.quick_input = ""


def number_badge(number: int) -> str:
    color = engine.get_color(number)
    css_class = {
        "Vermelho": "ball-red",
        "Preto": "ball-black",
        "Verde": "ball-green",
    }[color]
    return f"<span class='number-ball {css_class}'>{number}</span>"


def render_signal_card(signal: SignalResult) -> None:
    confidence_class = {
        "Alta": "confidence-high",
        "Média": "confidence-medium",
        "Baixa": "confidence-low",
        "Insuficiente": "confidence-low",
    }[signal.confidence_label]

    covered = "".join(number_badge(number) for number in signal.covered_numbers)
    st.markdown(
        f"""
        <section class="signal-card">
            <div class="eyebrow">SINAL ESTATÍSTICO</div>
            <div class="signal-header">
                <div>
                    <h2>{escape(signal.target_sector)}</h2>
                    <p>Epicentro físico: <strong>{signal.epicenter}</strong></p>
                </div>
                <span class="confidence-pill {confidence_class}">
                    Confiança {escape(signal.confidence_label)}
                </span>
            </div>
            <div class="ball-row">{covered}</div>
            <div class="signal-grid">
                <div><span>Pontuação</span><strong>{signal.score:.1f}%</strong></div>
                <div><span>Backtest</span><strong>{signal.backtest_accuracy:.1f}%</strong></div>
                <div><span>Amostra</span><strong>{signal.sample_size}</strong></div>
            </div>
            <p class="signal-note">{escape(signal.explanation)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
    :root {
        --bg: #07111f;
        --surface: rgba(15, 28, 46, 0.88);
        --surface-2: rgba(20, 39, 63, 0.94);
        --border: rgba(148, 163, 184, 0.18);
        --text: #edf6ff;
        --muted: #9eb0c4;
        --accent: #41d9b5;
        --accent-2: #77a7ff;
        --gold: #f5c76b;
        --danger: #ff6577;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(65, 217, 181, 0.12), transparent 32rem),
            radial-gradient(circle at 88% 18%, rgba(119, 167, 255, 0.11), transparent 28rem),
            linear-gradient(145deg, #050b14 0%, var(--bg) 55%, #081425 100%);
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #081321 0%, #0c1b2d 100%);
        border-right: 1px solid var(--border);
    }

    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 16px 18px;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.18);
    }

    .hero {
        padding: 28px 30px;
        border: 1px solid var(--border);
        border-radius: 24px;
        background:
            linear-gradient(120deg, rgba(65, 217, 181, 0.13), rgba(119, 167, 255, 0.08)),
            var(--surface);
        box-shadow: 0 22px 55px rgba(0, 0, 0, 0.22);
        margin-bottom: 22px;
    }

    .hero h1 {
        font-size: clamp(2.1rem, 4vw, 3.7rem);
        margin: 0;
        letter-spacing: -0.05em;
    }

    .hero p {
        max-width: 780px;
        color: var(--muted);
        font-size: 1.05rem;
        margin: 12px 0 0;
    }

    .eyebrow {
        color: var(--accent);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        margin-bottom: 8px;
    }

    .signal-card {
        min-height: 360px;
        padding: 26px;
        border: 1px solid rgba(65, 217, 181, 0.28);
        border-radius: 24px;
        background:
            linear-gradient(145deg, rgba(65, 217, 181, 0.14), rgba(119, 167, 255, 0.06)),
            var(--surface-2);
        box-shadow: 0 22px 55px rgba(0, 0, 0, 0.25);
    }

    .signal-header {
        display: flex;
        justify-content: space-between;
        gap: 18px;
        align-items: flex-start;
    }

    .signal-header h2 {
        margin: 0;
        font-size: 2rem;
    }

    .signal-header p, .signal-note {
        color: var(--muted);
    }

    .confidence-pill {
        display: inline-flex;
        align-items: center;
        white-space: nowrap;
        padding: 8px 12px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 800;
    }

    .confidence-high { background: rgba(65, 217, 181, 0.16); color: #7ff4d8; }
    .confidence-medium { background: rgba(245, 199, 107, 0.16); color: #ffe09d; }
    .confidence-low { background: rgba(255, 101, 119, 0.14); color: #ff9baa; }

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
        border-radius: 50%;
        font-weight: 900;
        border: 2px solid rgba(255,255,255,.28);
        box-shadow: inset 0 0 0 2px rgba(0,0,0,.16), 0 8px 20px rgba(0,0,0,.25);
    }

    .ball-red { background: linear-gradient(145deg, #ed334e, #9f142a); color: white; }
    .ball-black { background: linear-gradient(145deg, #293648, #080c12); color: white; }
    .ball-green { background: linear-gradient(145deg, #31c68c, #087451); color: white; }

    .signal-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
        margin: 12px 0 20px;
    }

    .signal-grid div, .panel {
        background: rgba(7, 17, 31, 0.64);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 14px;
    }

    .signal-grid span {
        display: block;
        color: var(--muted);
        font-size: 0.76rem;
        margin-bottom: 4px;
    }

    .signal-grid strong {
        font-size: 1.2rem;
    }

    .history-box {
        max-height: 230px;
        overflow-y: auto;
        padding: 14px;
        border-radius: 16px;
        background: rgba(3, 9, 17, 0.66);
        border: 1px solid var(--border);
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
        border-radius: 12px;
        border: 1px solid var(--border);
        transition: transform .15s ease, border-color .15s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(65, 217, 181, .55);
    }

    @media (max-width: 760px) {
        .signal-grid { grid-template-columns: 1fr; }
        .signal-header { flex-direction: column; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🎯 Roulette Lens")
    st.caption("Leitura estatística da roleta europeia")

    analysis_window = st.slider(
        "Janela de análise",
        min_value=12,
        max_value=120,
        value=36,
        help="Quantidade de resultados recentes usada no sinal.",
    )
    decay = st.slider(
        "Peso da recência",
        min_value=0.75,
        max_value=0.98,
        value=0.90,
        step=0.01,
        help="Valores menores dão mais peso às jogadas recentes.",
    )
    neighbor_radius = st.select_slider(
        "Cobertura de vizinhos",
        options=[1, 2, 3],
        value=2,
        help="Quantidade de vizinhos físicos de cada lado do epicentro.",
    )

    st.divider()
    keyboard_tab, text_tab = st.tabs(["Mesa", "Texto"])

    with keyboard_tab:
        if st.button("0 🟢", use_container_width=True, key="number_0"):
            add_number(0)
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
                        add_number(number)
                        st.rerun()

    with text_tab:
        st.text_input(
            "Cole uma sequência",
            key="quick_input",
            placeholder="Ex.: 17, 0, 32, 21, 8",
            on_change=submit_text_input,
        )
        st.caption("Aceita números de 0 a 36 separados por espaço, vírgula ou quebra de linha.")

    st.divider()
    st.markdown("### Histórico")

    if st.session_state.history:
        recent_badges = " ".join(number_badge(number) for number in st.session_state.history[-60:])
        st.markdown(f"<div class='history-box'>{recent_badges}</div>", unsafe_allow_html=True)
        st.caption(f"{len(st.session_state.history)} resultados registrados")

        undo_col, clear_col = st.columns(2)
        with undo_col:
            if st.button("↩ Desfazer", use_container_width=True):
                st.session_state.history.pop()
                st.rerun()
        with clear_col:
            if st.button("Limpar", type="primary", use_container_width=True):
                st.session_state.history = []
                st.rerun()
    else:
        st.info("Adicione resultados para iniciar.")

st.markdown(
    """
    <section class="hero">
        <div class="eyebrow">EUROPEAN ROULETTE ANALYTICS</div>
        <h1>Roulette Lens</h1>
        <p>
            Um painel mais limpo e auditável para visualizar frequência, setores físicos,
            recência e desempenho histórico dos sinais.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

history = st.session_state.history
total_spins = len(history)

if total_spins == 0:
    st.info("Comece adicionando os resultados no painel lateral.")
    st.stop()

current_window = history[-analysis_window:]
signal = engine.build_signal(
    current_window,
    decay=decay,
    neighbor_radius=neighbor_radius,
)

red_count = sum(engine.get_color(number) == "Vermelho" for number in current_window)
black_count = sum(engine.get_color(number) == "Preto" for number in current_window)
zero_count = current_window.count(0)

metric_cols = st.columns(4)
metric_cols[0].metric("Resultados", total_spins)
metric_cols[1].metric("Janela ativa", len(current_window))
metric_cols[2].metric("Vermelho / Preto", f"{red_count} / {black_count}")
metric_cols[3].metric("Zeros", zero_count)

st.markdown("<br>", unsafe_allow_html=True)

left_col, right_col = st.columns([1.16, 0.84], gap="large")

with left_col:
    if signal:
        render_signal_card(signal)
    else:
        st.warning("São necessários pelo menos 8 resultados válidos para gerar um sinal.")

with right_col:
    sector_counts = Counter(engine.get_sector(number) for number in current_window)
    sector_names = list(engine.SECTORS)
    sector_values = [sector_counts.get(name, 0) for name in sector_names]

    fig_sector = go.Figure(
        go.Bar(
            x=sector_values,
            y=sector_names,
            orientation="h",
            text=sector_values,
            textposition="auto",
            marker=dict(
                color=["#41d9b5", "#77a7ff", "#f5c76b", "#d17cff"],
                line=dict(width=0),
            ),
        )
    )
    fig_sector.update_layout(
        title="Distribuição por setor",
        template="plotly_dark",
        height=360,
        margin=dict(l=10, r=10, t=55, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Ocorrências",
        yaxis_title="",
        showlegend=False,
    )
    st.plotly_chart(fig_sector, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

tab_overview, tab_numbers, tab_audit = st.tabs(
    ["Visão geral", "Números", "Auditoria do sinal"]
)

with tab_overview:
    timeline = pd.DataFrame(
        {
            "Jogada": range(max(1, total_spins - len(current_window) + 1), total_spins + 1),
            "Número": current_window,
            "Setor": [engine.get_sector(number) for number in current_window],
            "Cor": [engine.get_color(number) for number in current_window],
        }
    )
    fig_timeline = px.scatter(
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
    fig_timeline.update_traces(marker=dict(size=11, line=dict(width=1, color="white")))
    fig_timeline.update_layout(
        template="plotly_dark",
        height=390,
        title="Sequência recente por setor",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Cor",
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

with tab_numbers:
    frequency = Counter(current_window)
    number_df = pd.DataFrame(
        {
            "Número": list(range(37)),
            "Ocorrências": [frequency.get(number, 0) for number in range(37)],
            "Cor": [engine.get_color(number) for number in range(37)],
            "Setor": [engine.get_sector(number) for number in range(37)],
        }
    ).sort_values(["Ocorrências", "Número"], ascending=[False, True])

    st.dataframe(
        number_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Número": st.column_config.NumberColumn(format="%d"),
            "Ocorrências": st.column_config.ProgressColumn(
                min_value=0,
                max_value=max(1, number_df["Ocorrências"].max()),
            ),
        },
    )

with tab_audit:
    if signal:
        baseline = len(signal.covered_numbers) / 37 * 100
        audit_cols = st.columns(3)
        audit_cols[0].metric("Taxa do backtest", f"{signal.backtest_accuracy:.1f}%")
        audit_cols[1].metric("Cobertura teórica", f"{baseline:.1f}%")
        audit_cols[2].metric(
            "Diferença observada",
            f"{signal.backtest_accuracy - baseline:+.1f} p.p.",
        )

        st.write(
            "O backtest percorre o histórico sem olhar o resultado seguinte, "
            "gera o sinal com os dados disponíveis naquele momento e mede se a "
            "próxima jogada caiu na cobertura."
        )
        st.progress(min(signal.confidence_score / 100, 1.0))
        st.caption(
            f"Índice de confiança: {signal.confidence_score:.1f}/100. "
            "Quanto maior a amostra e mais consistente o backtest, maior o índice."
        )
    else:
        st.info("Adicione mais resultados para liberar a auditoria.")

st.markdown(
    """
    <div class="disclaimer">
        <strong>Importante:</strong> resultados de roleta são independentes e aleatórios.
        Este painel descreve o histórico; ele não garante vantagem, lucro ou previsão do próximo giro.
    </div>
    """,
    unsafe_allow_html=True,
)
