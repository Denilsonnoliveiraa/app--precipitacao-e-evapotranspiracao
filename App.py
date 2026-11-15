
import re
import unicodedata
from pathlib import Path
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# 1. CONFIGURAÇÃO GERAL
# ============================================================

st.set_page_config(
    page_title="HidroClima Nordeste",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = Path(__file__).resolve().parent

NOME_EXCEL = "Nordeste_2000_2024_precipitacao_evapotranspiracao"

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro"
]

P = "Precipitacao_mm_mes"
ET = "Evapotranspiracao_mm_mes"

COLUNAS = {
    "Precipitação": P,
    "Evapotranspiração": ET
}

CORES = {
    "Precipitação": "#1677AD",
    "Evapotranspiração": "#168C9A"
}

EMOJIS = {
    "Precipitação": "🌧️",
    "Evapotranspiração": "💧",
    "Comparativo": "🌊"
}

PERIODOS = {
    "Todos os anos": "01_Todos_os_anos",
    "De 2 em 2 anos": "02_De_2_em_2_anos",
    "De 5 em 5 anos": "03_De_5_em_5_anos",
    "De 10 em 10 anos": "04_De_10_em_10_anos",
    "Por década": "05_Por_decada"
}

EXTENSOES = {
    ".png", ".jpg", ".jpeg",
    ".webp", ".tif", ".tiff"
}

# ============================================================
# 2. CSS GLOBAL - CONTRASTE CORRIGIDO
# ============================================================

st.markdown("""
<style>

/* ============================================================
   FUNDO GERAL
   ============================================================ */

.stApp {
    background: linear-gradient(
        130deg,
        #f1f9fb 0%,
        #f5faf6 100%
    ) !important;
    color: #111827 !important;
}

.block-container {
    max-width: 1650px;
    padding-top: 1.4rem;
    padding-bottom: 2rem;
}

/* ============================================================
   TÍTULOS
   ============================================================ */

.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4 {
    color: #11627b !important;
    opacity: 1 !important;
}

/* ============================================================
   TEXTOS EM FUNDOS CLAROS
   ============================================================ */

.stApp [data-testid="stMarkdownContainer"] p,
.stApp [data-testid="stMarkdownContainer"] li,
.stApp [data-testid="stMarkdownContainer"] strong,
.stApp [data-testid="stMarkdownContainer"] em {
    color: #172b36;
    opacity: 1 !important;
}

.justificado {
    color: #14232b !important;
    text-align: justify;
    line-height: 1.85;
    font-size: 15px;
    margin-bottom: 14px;
}

.justificado p {
    color: #14232b !important;
    text-align: justify !important;
    line-height: 1.85;
}

.pendente {
    color: #1c3039 !important;
    text-align: justify;
    line-height: 1.8;
    opacity: 1 !important;
}

/* ============================================================
   CABEÇALHO
   ============================================================ */

.cabecalho {
    background: linear-gradient(
        110deg,
        #075878,
        #1595b1,
        #48a88c
    );
    border-radius: 17px;
    padding: 26px 30px;
    margin-bottom: 19px;
    box-shadow: 0 5px 18px rgba(12,84,113,0.13);
}

.cabecalho h1,
.cabecalho p,
.cabecalho span,
.cabecalho strong {
    color: #ffffff !important;
    opacity: 1 !important;
}

.cabecalho p {
    text-align: justify;
    line-height: 1.7;
}

/* ============================================================
   ABAS
   ============================================================ */

.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    flex-wrap: wrap;
}

.stTabs [data-baseweb="tab"] {
    background: #e3f1f3 !important;
    border-radius: 8px;
    padding: 9px 12px;
}

.stTabs [data-baseweb="tab"] p {
    color: #115973 !important;
    opacity: 1 !important;
}

.stTabs [aria-selected="true"] {
    background: #147b99 !important;
}

.stTabs [aria-selected="true"] p {
    color: #ffffff !important;
}

/* ============================================================
   BOTÕES
   ============================================================ */

.stApp .stButton > button,
.stApp .stDownloadButton > button {
    background: #126f8a !important;
    border: 1px solid #126f8a !important;
    color: #ffffff !important;
    border-radius: 9px !important;
    min-height: 42px;
    font-weight: 650 !important;
    opacity: 1 !important;
}

.stApp .stButton > button *,
.stApp .stDownloadButton > button * {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    opacity: 1 !important;
}

.stApp .stButton > button:hover,
.stApp .stDownloadButton > button:hover {
    background: #074e65 !important;
    border-color: #074e65 !important;
}

.stApp .stButton > button:focus-visible,
.stApp .stDownloadButton > button:focus-visible {
    outline: 2px solid #158eab !important;
    outline-offset: 2px;
}

[data-testid="stDownloadButton"] button svg {
    color: #ffffff !important;
    stroke: #ffffff !important;
}

/* ============================================================
   CAMPOS DE SELEÇÃO
   ============================================================ */

div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #b6ced3 !important;
    border-radius: 8px;
    color: #111827 !important;
}

div[data-baseweb="select"] span,
div[data-baseweb="select"] input {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    opacity: 1 !important;
}

div[data-baseweb="select"] svg {
    color: #11627b !important;
    fill: #11627b !important;
}

div[data-baseweb="popover"],
div[data-baseweb="popover"] ul,
div[data-baseweb="popover"] li {
    background: #ffffff !important;
    color: #111827 !important;
}

div[role="option"] {
    color: #111827 !important;
    opacity: 1 !important;
}

div[role="option"]:hover {
    background: #e4f3f6 !important;
    color: #103d50 !important;
}

/* ============================================================
   INPUTS
   ============================================================ */

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: #ffffff !important;
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    caret-color: #111827 !important;
}

[data-testid="stTextInput"] div[data-baseweb="input"],
[data-testid="stNumberInput"] div[data-baseweb="input"] {
    background: #ffffff !important;
    border-color: #b5cdd3 !important;
}

/* ============================================================
   LEGENDAS E TEXTOS AUXILIARES
   ============================================================ */

[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
.stApp small {
    color: #344b58 !important;
    opacity: 1 !important;
}

/* ============================================================
   EXPANDERS
   ============================================================ */

[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #cfdee4 !important;
    border-radius: 10px !important;
}

[data-testid="stExpander"] summary {
    background: #e7f2f4 !important;
    color: #103d50 !important;
    border-radius: 8px !important;
}

[data-testid="stExpander"] summary *,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #103d50 !important;
    opacity: 1 !important;
}

[data-testid="stExpander"] summary svg {
    color: #11627b !important;
    stroke: #11627b !important;
}

[data-testid="stExpander"]
[data-testid="stMarkdownContainer"] p {
    color: #172b36 !important;
}

/* ============================================================
   MÉTRICAS
   ============================================================ */

[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #d8e8eb !important;
    border-left: 4px solid #178ca0 !important;
    border-radius: 11px;
    padding: 13px;
    min-height: 113px;
}

[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"] {
    color: #103d50 !important;
    opacity: 1 !important;
}

/* ============================================================
   FAIXAS E SEÇÕES
   ============================================================ */

.faixa {
    background: #e5f2f4 !important;
    border-left: 4px solid #1189a5;
    color: #105773 !important;
    padding: 11px 14px;
    border-radius: 8px;
    font-weight: 700;
    margin: 14px 0;
}

/* ============================================================
   CARTÕES
   ============================================================ */

.cartao {
    background: #ffffff;
    border: 1px solid #d3e7ec;
    border-left: 4px solid #178ca0;
    border-radius: 12px;
    padding: 16px;
    overflow-wrap: anywhere;
}

.cartao p {
    color: #182b35 !important;
}

/* ============================================================
   TABELAS
   ============================================================ */

[data-testid="stDataFrame"] {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #d6e7eb !important;
    border-radius: 9px;
}

.stApp table {
    background: #ffffff;
    color: #111827;
}

.stApp table th {
    background: #e4f1f4;
    color: #113f53;
}

.stApp table td {
    color: #172b36;
}

/* ============================================================
   MAPAS
   ============================================================ */

.metadata {
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    margin-bottom: 12px;
}

.metadata span {
    background: #e5f2f4 !important;
    border: 1px solid #cde2e8;
    color: #163d4c !important;
    padding: 5px 9px;
    border-radius: 6px;
    font-size: 12px;
    opacity: 1 !important;
}

[data-testid="stImage"] img {
    border-radius: 7px;
}

/* ============================================================
   CONTROLES
   ============================================================ */

[data-testid="stSlider"] label p,
[data-testid="stSelectSlider"] label p,
[data-testid="stSelectbox"] label p,
[data-testid="stRadio"] label p {
    color: #172b36 !important;
    opacity: 1 !important;
}

/* ============================================================
   FÓRMULAS
   ============================================================ */

div[data-testid="stLatex"] {
    text-align: center;
    margin: 16px 0;
    color: #111827 !important;
    opacity: 1 !important;
}

/* ============================================================
   BARRA LATERAL
   ============================================================ */

section[data-testid="stSidebar"] {
    background: #e7f3f5 !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] li {
    color: #193945 !important;
    opacity: 1 !important;
}

/* ============================================================
   RODAPÉ
   ============================================================ */

.rodape {
    text-align: center;
    color: #345363 !important;
    font-size: 13px;
    padding: 15px;
}

/* ============================================================
   RESPONSIVIDADE
   ============================================================ */

@media (max-width: 768px) {

    .cabecalho h1 {
        font-size: 26px;
    }

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. FUNÇÕES AUXILIARES
# ============================================================

def norm(s):

    s = unicodedata.normalize(
        "NFKD",
        str(s)
    )

    s = "".join(
        c for c in s
        if not unicodedata.combining(c)
    )

    return re.sub(
        r"[^a-z0-9]",
        "",
        s.lower()
    )


def localizar(pasta, nome):

    if pasta is None or not pasta.is_dir():
        return None

    return next(
        (
            x for x in pasta.iterdir()
            if x.is_dir() and norm(x.name) == norm(nome)
        ),
        None
    )


def texto(s):

    partes = re.split(
        r"\n\s*\n",
        s.strip()
    )

    html = "".join(
        "<p>" + escape(" ".join(p.split())) + "</p>"
        for p in partes
        if p.strip()
    )

    st.markdown(
        '<div class="justificado">'
        + html
        + "</div>",
        unsafe_allow_html=True
    )


def pendente(s):

    st.markdown(
        '<p class="pendente">'
        + escape(s)
        + '</p>',
        unsafe_allow_html=True
    )


def secao(titulo, conteudo):

    st.subheader(titulo)
    texto(conteudo)


def faixa(s):

    st.markdown(
        '<div class="faixa">'
        + escape(s)
        + '</div>',
        unsafe_allow_html=True
    )


def num(n, d=2):

    if pd.isna(n):
        return "—"

    return (
        f"{n:,.{d}f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# ============================================================
# 4. CONFIGURAÇÃO GLOBAL DOS GRÁFICOS PLOTLY
# ============================================================

def figura_base(fig, titulo="", altura=380):

    fig.update_layout(
        template="plotly_white",

        title=dict(
            text=titulo,
            font=dict(
                color="#142f3d",
                size=15
            )
        ),

        height=altura,

        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",

        font=dict(
            family="Arial",
            size=12,
            color="#152f3c"
        ),

        margin=dict(
            l=55,
            r=25,
            t=55,
            b=60
        ),

        legend=dict(
            font=dict(
                color="#142f3d"
            ),
            orientation="h",
            y=-0.25
        ),

        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor="#9cb7c0",
            font=dict(
                color="#142f3d"
            )
        )
    )

    fig.update_xaxes(
        tickfont=dict(
            color="#183846"
        ),
        title_font=dict(
            color="#183846"
        ),
        linecolor="#aebdc4",
        gridcolor="#e5ecf0"
    )

    fig.update_yaxes(
        tickfont=dict(
            color="#183846"
        ),
        title_font=dict(
            color="#183846"
        ),
        linecolor="#aebdc4",
        gridcolor="#e5ecf0"
    )

    return fig


def mostrar_grafico(fig, chave):

    st.plotly_chart(
        fig,
        use_container_width=True,
        key=chave
    )


# ============================================================
# 5. LEITURA DA PLANILHA EXCEL
# ============================================================

def converter_num(s):

    if pd.api.types.is_numeric_dtype(s):

        return pd.to_numeric(
            s,
            errors="coerce"
        )

    def conv(v):

        if pd.isna(v):
            return np.nan

        v = str(v).strip().replace(" ", "")

        if "," in v and "." in v:

            if v.rfind(",") > v.rfind("."):
                v = v.replace(".", "").replace(",", ".")

            else:
                v = v.replace(",", "")

        else:
            v = v.replace(",", ".")

        try:
            return float(v)

        except (ValueError, TypeError):
            return np.nan

    return s.map(conv).astype(float)


def caminho_excel():

    candidatos = [
        BASE / (NOME_EXCEL + ".xlsx"),
        BASE / (NOME_EXCEL + ".xlsm"),
        BASE / NOME_EXCEL / (NOME_EXCEL + ".xlsx"),
        BASE / NOME_EXCEL / (NOME_EXCEL + ".xlsm")
    ]

    for caminho in candidatos:

        if caminho.is_file():
            return caminho

    for pasta in [BASE, BASE / NOME_EXCEL]:

        if pasta.is_dir():

            for arq in pasta.iterdir():

                if (
                    arq.is_file()
                    and arq.suffix.lower() in {".xlsx", ".xlsm"}
                    and not arq.name.startswith("~$")
                    and norm(arq.stem) == norm(NOME_EXCEL)
                ):
                    return arq

    return None


@st.cache_data(show_spinner=False)
def carregar_excel(caminho, mtime):

    sheets = pd.read_excel(
        caminho,
        sheet_name=None,
        engine="openpyxl"
    )

    sheets = {
        norm(k): v
        for k, v in sheets.items()
    }

    exigidas = {
        "mensal",
        "precipitacao",
        "evapotranspiracao"
    }

    if not exigidas.issubset(sheets):

        raise ValueError(
            "A planilha precisa conter as abas "
            "Mensal, Precipitacao e Evapotranspiracao."
        )

    df = sheets["mensal"].copy()

    mapa_colunas = {
        "ano": "Ano",
        "mes": "Mes",
        "mesnome": "Mes_nome",
        "precipitacaommes": P,
        "evapotranspiracaommes": ET
    }

    df = df.rename(
        columns={
            c: mapa_colunas[norm(c)]
            for c in df.columns
            if norm(c) in mapa_colunas
        }
    )

    if not {"Ano", "Mes", P, ET}.issubset(df.columns):

        raise ValueError(
            "A aba Mensal deve conter Ano, Mes, "
            "Precipitacao_mm_mes e Evapotranspiracao_mm_mes."
        )

    for coluna in ["Ano", "Mes", P, ET]:

        df[coluna] = converter_num(
            df[coluna]
        )

    df = df.dropna(
        subset=["Ano", "Mes"]
    ).copy()

    df = df.loc[
        df["Mes"].between(1, 12)
    ].copy()

    df["Ano"] = df["Ano"].astype(int)
    df["Mes"] = df["Mes"].astype(int)

    if df.duplicated(["Ano", "Mes"]).any():

        raise ValueError(
            "Há registros duplicados para o mesmo "
            "ano e mês na aba Mensal."
        )

    df["Mes_nome"] = df["Mes"].map(
        lambda x: MESES[x - 1]
    )

    df["Data"] = pd.to_datetime(
        dict(
            year=df["Ano"],
            month=df["Mes"],
            day=1
        )
    )

    return df.sort_values(
        ["Ano", "Mes"]
    ).reset_index(drop=True)


def obter_dados():

    arq = caminho_excel()

    if arq is None:

        st.warning(
            f"Arquivo {NOME_EXCEL}.xlsx não encontrado. "
            "Coloque a planilha ao lado de app.py "
            "ou em uma pasta com o mesmo nome."
        )

        return None

    try:

        return carregar_excel(
            str(arq),
            arq.stat().st_mtime_ns
        )

    except Exception as erro:

        st.error(
            f"Não foi possível ler a planilha: {erro}"
        )

        return None


# ============================================================
# 6. FUNÇÕES ESTATÍSTICAS
# ============================================================

def stats(s):

    s = s.dropna().astype(float)

    if s.empty:
        return None

    media = s.mean()
    dp = s.std()

    return {
        "N": len(s),
        "Média": media,
        "Mediana": s.median(),
        "Mínimo": s.min(),
        "Máximo": s.max(),
        "Desvio padrão": dp,
        "CV (%)": (
            dp / abs(media) * 100
            if media != 0 and pd.notna(dp)
            else np.nan
        ),
        "Q1": s.quantile(0.25),
        "Q3": s.quantile(0.75),
        "Amplitude": s.max() - s.min()
    }


def anuais_completos(df):

    registros = []

    for ano, grupo in df.groupby("Ano"):

        linha = {
            "Ano": int(ano)
        }

        for coluna in [P, ET]:

            validos = grupo.dropna(
                subset=[coluna]
            )

            if (
                len(validos) == 12
                and validos["Mes"].nunique() == 12
            ):
                linha[coluna] = validos[coluna].sum()

            else:
                linha[coluna] = np.nan

        registros.append(linha)

    return pd.DataFrame(registros).sort_values("Ano")


# ============================================================
# 7. GRÁFICOS DA ANÁLISE DESCRITIVA
# ============================================================

def grafico_boxplot(df, nomes):

    fig = go.Figure()

    for nome in nomes:

        fig.add_trace(
            go.Box(
                y=df[COLUNAS[nome]].dropna(),
                name=nome,
                marker_color=CORES[nome],
                boxpoints="outliers",
                showlegend=False
            )
        )

    fig.update_yaxes(
        title_text="mm/mês"
    )

    return figura_base(
        fig,
        "Distribuição mensal",
        350
    )


def grafico_histograma(df, nomes):

    fig = go.Figure()

    for nome in nomes:

        fig.add_trace(
            go.Histogram(
                x=df[COLUNAS[nome]].dropna(),
                name=nome,
                marker_color=CORES[nome],
                opacity=0.70,
                nbinsx=14
            )
        )

    fig.update_layout(
        barmode="overlay",
        showlegend=len(nomes) > 1
    )

    fig.update_xaxes(
        title_text="mm/mês"
    )

    fig.update_yaxes(
        title_text="Frequência"
    )

    return figura_base(
        fig,
        "Histograma",
        350
    )


def grafico_correlacao(df):

    pares = df[[P, ET]].dropna()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=pares[P],
            y=pares[ET],
            mode="markers",
            marker=dict(
                color="#148aa4",
                size=6,
                opacity=0.75
            ),
            showlegend=False
        )
    )

    if (
        len(pares) >= 3
        and pares[P].nunique() > 1
        and pares[ET].nunique() > 1
    ):

        coef = np.polyfit(
            pares[P],
            pares[ET],
            1
        )

        xx = np.array([
            pares[P].min(),
            pares[P].max()
        ])

        fig.add_trace(
            go.Scatter(
                x=xx,
                y=coef[0] * xx + coef[1],
                mode="lines",
                line=dict(
                    color="#dc8735",
                    width=2
                ),
                showlegend=False
            )
        )

    fig.update_xaxes(
        title_text="P (mm/mês)"
    )

    fig.update_yaxes(
        title_text="ET (mm/mês)"
    )

    return figura_base(
        fig,
        "Correlação P × ET",
        350
    )


# ============================================================
# 8. PAINEL DESCRITIVO
# ============================================================

def painel_descritivo():

    st.header("📊 Análise Descritiva")

    texto("""
    Explore a distribuição e a variabilidade da
    precipitação e da evapotranspiração no Nordeste
    brasileiro. Selecione uma variável ou o modo
    comparativo para visualizar indicadores, gráficos,
    sazonalidade e estatísticas.
    """)

    if "descritivo_modo" not in st.session_state:
        st.session_state.descritivo_modo = None

    modo = st.session_state.descritivo_modo

    if modo is None:

        st.subheader("Selecione a análise")

        colunas = st.columns(3)

        for col, nome in zip(
            colunas,
            [
                "Precipitação",
                "Evapotranspiração",
                "Comparativo"
            ]
        ):

            with col:

                with st.container(border=True):

                    st.markdown(
                        f"### {EMOJIS[nome]} {nome}"
                    )

                    descricao = {
                        "Precipitação":
                            "Análise dos registros de precipitação.",
                        "Evapotranspiração":
                            "Análise dos registros de evapotranspiração.",
                        "Comparativo":
                            "Comparação estatística entre P e ET."
                    }

                    texto(descricao[nome])

                    st.button(
                        f"Analisar {nome}",
                        use_container_width=True,
                        key="desc_" + norm(nome),
                        on_click=lambda n=nome: st.session_state.update(
                            descritivo_modo=n
                        )
                    )

        return

    df = obter_dados()

    if df is None or df.empty:
        return

    titulo, botao = st.columns(
        [4, 1.25],
        vertical_alignment="center"
    )

    with titulo:

        st.subheader(
            f"{EMOJIS[modo]} {modo}"
        )

    with botao:

        st.button(
            "← Voltar às análises",
            use_container_width=True,
            key="voltar_descritivo",
            on_click=lambda: st.session_state.update(
                descritivo_modo=None
            )
        )

    # --------------------------------------------------------
    # FILTROS
    # --------------------------------------------------------

    faixa("📅 Período de análise")

    anos = sorted(
        df["Ano"].unique().tolist()
    )

    ai, af = st.select_slider(
        "Selecione o intervalo de anos",
        options=anos,
        value=(anos[0], anos[-1]),
        key="descritivo_periodo"
    )

    dados = df[
        df["Ano"].between(ai, af)
    ].copy()

    nomes = (
        list(COLUNAS)
        if modo == "Comparativo"
        else [modo]
    )

    totais = anuais_completos(dados)

    st.caption(
        f"Período: {ai}–{af} | "
        f"{len(dados)} registros mensais."
    )

    # --------------------------------------------------------
    # INDICADORES
    # --------------------------------------------------------

    faixa("📌 Indicadores principais")

    if modo == "Comparativo":

        indicadores = [
            ("Média mensal P", dados[P].mean(), "mm"),
            ("Média mensal ET", dados[ET].mean(), "mm"),
            ("Total anual médio P", totais[P].mean(), "mm"),
            ("Total anual médio ET", totais[ET].mean(), "mm")
        ]

    else:

        s = stats(
            dados[COLUNAS[modo]]
        )

        if s is None:
            st.warning("Sem dados válidos.")
            return

        indicadores = [
            ("Média", s["Média"], "mm"),
            ("Mediana", s["Mediana"], "mm"),
            ("Desvio padrão", s["Desvio padrão"], "mm"),
            ("CV", s["CV (%)"], "%")
        ]

    for col, item in zip(
        st.columns(4),
        indicadores
    ):

        with col:

            st.metric(
                item[0],
                f"{num(item[1])} {item[2]}"
            )

    # --------------------------------------------------------
    # GRÁFICOS EM TRÊS COLUNAS
    # --------------------------------------------------------

    st.divider()

    faixa("📊 Distribuição estatística")

    c1, c2, c3 = st.columns(
        3,
        gap="small"
    )

    with c1:

        mostrar_grafico(
            grafico_boxplot(dados, nomes),
            "desc_box_" + norm(modo)
        )

    with c2:

        mostrar_grafico(
            grafico_histograma(dados, nomes),
            "desc_hist_" + norm(modo)
        )

    with c3:

        if modo == "Comparativo":

            mostrar_grafico(
                grafico_correlacao(dados),
                "desc_corr"
            )

            pares = dados[[P, ET]].dropna()

            r = (
                pares[P].corr(pares[ET])
                if len(pares) > 2
                else np.nan
            )

            st.caption(
                f"Correlação de Pearson: r = {num(r, 3)}"
            )

        else:

            tabela = stats(
                dados[COLUNAS[modo]]
            )

            st.dataframe(
                pd.DataFrame({
                    "Indicador": list(tabela.keys()),
                    "Valor": [
                        num(v)
                        for v in tabela.values()
                    ]
                }),
                use_container_width=True,
                hide_index=True,
                height=350
            )

    # --------------------------------------------------------
    # SAZONALIDADE
    # --------------------------------------------------------

    st.divider()

    faixa("📅 Médias mensais")

    medias = (
        dados.groupby("Mes")[
            [COLUNAS[n] for n in nomes]
        ]
        .mean()
        .reindex(range(1, 13))
    )

    fig = go.Figure()

    for nome in nomes:

        fig.add_trace(
            go.Bar(
                x=MESES,
                y=medias[COLUNAS[nome]],
                name=nome,
                marker_color=CORES[nome]
            )
        )

    fig.update_layout(
        barmode="group",
        xaxis_title="Mês",
        yaxis_title="Média (mm/mês)"
    )

    mostrar_grafico(
        figura_base(
            fig,
            "Comportamento médio mensal",
            420
        ),
        "desc_mensal_" + norm(modo)
    )

    # --------------------------------------------------------
    # ESTATÍSTICAS
    # --------------------------------------------------------

    st.divider()

    faixa("📋 Estatísticas mensais e anuais")

    c1, c2 = st.columns(2)

    with c1:

        linhas = []

        for nome in nomes:

            s = stats(
                dados[COLUNAS[nome]]
            )

            if s:
                linhas.append({
                    "Variável": nome,
                    **s
                })

        st.markdown("**Estatísticas mensais**")

        st.dataframe(
            pd.DataFrame(linhas),
            use_container_width=True,
            hide_index=True
        )

    with c2:

        linhas = []

        for nome in nomes:

            s = stats(
                totais[COLUNAS[nome]]
            )

            if s:
                linhas.append({
                    "Variável": nome,
                    **s
                })

        st.markdown("**Estatísticas anuais**")

        st.dataframe(
            pd.DataFrame(linhas),
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # DIFERENÇA P - ET
    # --------------------------------------------------------

    if modo == "Comparativo":

        st.divider()

        faixa("💧 Indicador simplificado P − ET")

        texto("""
        A diferença P − ET representa um indicador
        simplificado de entrada e transferência
        de água para a atmosfera. Não corresponde
        ao balanço hídrico completo.
        """)

        st.latex(r"D=P-ET")

        dif = (
            medias[P] - medias[ET]
        ).values

        fig = go.Figure(
            go.Bar(
                x=MESES,
                y=dif,
                marker_color=[
                    "#1677AD" if x >= 0 else "#CD7B32"
                    for x in dif
                ]
            )
        )

        fig.add_hline(
            y=0,
            line_color="#344653"
        )

        fig.update_layout(
            yaxis_title="P − ET (mm)"
        )

        mostrar_grafico(
            figura_base(
                fig,
                "Diferença média mensal",
                380
            ),
            "desc_balanco"
        )

    # --------------------------------------------------------
    # CONSULTA AOS DADOS
    # --------------------------------------------------------

    with st.expander("📋 Consultar e exportar dados"):

        visual = dados[
            ["Ano", "Mes", "Mes_nome"]
            + [COLUNAS[n] for n in nomes]
        ]

        st.dataframe(
            visual,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "⬇️ Baixar dados em CSV",
            data=visual.to_csv(
                index=False,
                sep=";",
                decimal=","
            ).encode("utf-8-sig"),
            file_name=f"descritivo_{ai}_{af}.csv",
            mime="text/csv",
            key="desc_csv"
        )

    # --------------------------------------------------------
    # NOTAS METODOLÓGICAS
    # --------------------------------------------------------

    with st.expander("📚 Notas metodológicas"):

        texto("""
        As estatísticas foram calculadas a partir
        dos registros mensais. O desvio padrão é
        amostral e o coeficiente de variação deve
        ser interpretado com cautela quando a média
        está próxima de zero. Os totais anuais
        consideram apenas anos completos.
        """)

        st.latex(
            r"\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i"
        )

        st.latex(
            r"s=\sqrt{\frac{\sum_{i=1}^{n}(x_i-\bar{x})^2}{n-1}}"
        )

        st.latex(
            r"CV=100\frac{s}{|\bar{x}|}"
        )


# ============================================================
# 9. FUNÇÕES DAS SÉRIES TEMPORAIS
# ============================================================

def media_movel(df, coluna, janela):

    serie = (
        df.set_index("Data")[coluna]
        .asfreq("MS")
    )

    return serie.rolling(
        window=janela,
        min_periods=janela
    ).mean()


def anomalias_mensais(df, coluna):

    dados = df.copy()

    climatologia = dados.groupby("Mes")[coluna].mean()

    dados["Climatologia"] = dados["Mes"].map(
        climatologia
    )

    dados["Anomalia"] = (
        dados[coluna] - dados["Climatologia"]
    )

    return dados


def grafico_serie_mensal(df, coluna, nome, janela):

    serie = (
        df.set_index("Data")[coluna]
        .asfreq("MS")
    )

    mm = serie.rolling(
        window=janela,
        min_periods=janela
    ).mean()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=serie.index,
            y=serie.values,
            mode="lines",
            name="Observado",
            line=dict(
                color=CORES[nome],
                width=1.5
            ),
            opacity=0.70
        )
    )

    fig.add_trace(
        go.Scatter(
            x=mm.index,
            y=mm.values,
            mode="lines",
            name=f"Média móvel {janela} meses",
            line=dict(
                color="#D07B2D",
                width=2.8
            )
        )
    )

    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="mm/mês"
    )

    return figura_base(
        fig,
        f"Série mensal — {nome}",
        440
    )


def grafico_serie_anual(df, coluna, nome):

    totais = anuais_completos(df)

    dados = totais[
        ["Ano", coluna]
    ].dropna()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=dados["Ano"],
            y=dados[coluna],
            name="Total anual",
            marker_color=CORES[nome]
        )
    )

    if len(dados) >= 3:

        x = dados["Ano"].to_numpy(dtype=float)
        y = dados[coluna].to_numpy(dtype=float)

        coef = np.polyfit(x, y, 1)

        fig.add_trace(
            go.Scatter(
                x=dados["Ano"],
                y=np.polyval(coef, x),
                name="Tendência linear",
                mode="lines",
                line=dict(
                    color="#C36B29",
                    width=2.5,
                    dash="dash"
                )
            )
        )

    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Total anual (mm)"
    )

    return figura_base(
        fig,
        f"Totais anuais — {nome}",
        420
    )


def grafico_heatmap(df, coluna, nome):

    tabela = df.pivot_table(
        index="Ano",
        columns="Mes",
        values=coluna,
        aggfunc="mean"
    )

    tabela = tabela.reindex(
        columns=list(range(1, 13))
    ).sort_index()

    fig = go.Figure(
        go.Heatmap(
            z=tabela.values,
            x=MESES,
            y=tabela.index.astype(str),
            colorscale="YlGnBu",
            colorbar=dict(
                title=dict(
                    text="mm",
                    font=dict(
                        color="#183846"
                    )
                ),
                tickfont=dict(
                    color="#183846"
                )
            ),
            hovertemplate=(
                "Ano: %{y}"
                "<br>Mês: %{x}"
                "<br>Valor: %{z:.2f} mm"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        xaxis_title="Mês",
        yaxis_title="Ano"
    )

    fig = figura_base(
        fig,
        f"Heatmap mensal — {nome}",
        600
    )

    fig.update_yaxes(
        autorange="reversed",
        type="category"
    )

    return fig


def grafico_anomalias(df, coluna, nome):

    dados = anomalias_mensais(
        df,
        coluna
    )

    cores = [
        "#1677AD" if v >= 0 else "#D17C39"
        for v in dados["Anomalia"]
    ]

    fig = go.Figure(
        go.Bar(
            x=dados["Data"],
            y=dados["Anomalia"],
            marker_color=cores,
            name="Anomalia"
        )
    )

    fig.add_hline(
        y=0,
        line_color="#344653",
        line_width=1
    )

    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Anomalia (mm/mês)"
    )

    return figura_base(
        fig,
        f"Anomalias mensais — {nome}",
        400
    )


# ============================================================
# 10. PREVISÃO EXPLORATÓRIA ATÉ 2028
# ============================================================

def preparar_anos_completos(df, coluna):

    completos = []

    for ano, grupo in df.groupby("Ano"):

        validos = grupo.dropna(
            subset=[coluna]
        )

        if (
            len(validos) == 12
            and validos["Mes"].nunique() == 12
        ):
            completos.append(int(ano))

    return df[
        df["Ano"].isin(completos)
    ].copy()


def prever_serie(df, coluna, ano_final=2028):

    treino = preparar_anos_completos(
        df,
        coluna
    )

    anos = sorted(
        treino["Ano"].unique()
    )

    if len(anos) < 6:

        return None, (
            "São necessários pelo menos seis anos "
            "com doze meses válidos para a projeção."
        )

    ultimo_ano = max(anos)

    if ultimo_ano >= ano_final:

        return None, (
            "Não há horizonte futuro até "
            f"{ano_final} para projetar."
        )

    # Tendência das médias anuais.
    anuais = treino.groupby("Ano")[coluna].mean()

    x = anuais.index.to_numpy(dtype=float)
    y = anuais.to_numpy(dtype=float)

    centro = x.mean()

    inclinacao, intercepto = np.polyfit(
        x - centro,
        y,
        1
    )

    treino["Tendencia"] = (
        intercepto
        + inclinacao * (treino["Ano"] - centro)
    )

    # Componente sazonal.
    treino["Residual_sazonal"] = (
        treino[coluna] - treino["Tendencia"]
    )

    sazonalidade = (
        treino.groupby("Mes")["Residual_sazonal"]
        .mean()
        .reindex(range(1, 13))
    )

    treino["Ajustado"] = (
        treino["Tendencia"]
        + treino["Mes"].map(sazonalidade)
    )

    treino["Erro"] = (
        treino[coluna] - treino["Ajustado"]
    )

    dp_residuos = treino["Erro"].std(ddof=1)

    if not np.isfinite(dp_residuos):
        dp_residuos = 0.0

    registros = []

    for ano in range(
        ultimo_ano + 1,
        ano_final + 1
    ):

        horizonte = ano - ultimo_ano

        for mes in range(1, 13):

            estimativa = (
                intercepto
                + inclinacao * (ano - centro)
                + sazonalidade.loc[mes]
            )

            estimativa = max(
                0.0,
                estimativa
            )

            # Faixa indicativa de dispersão.
            margem = (
                1.282
                * dp_residuos
                * np.sqrt(horizonte)
            )

            registros.append({
                "Ano": ano,
                "Mes": mes,
                "Data": pd.Timestamp(
                    year=ano,
                    month=mes,
                    day=1
                ),
                "Previsto": estimativa,
                "Limite_inferior": max(
                    0.0,
                    estimativa - margem
                ),
                "Limite_superior": (
                    estimativa + margem
                )
            })

    return pd.DataFrame(registros), None


def grafico_previsao(df, coluna, nome, previsao):

    observado = df[
        ["Data", coluna]
    ].dropna().sort_values("Data")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=observado["Data"],
            y=observado[coluna],
            mode="lines",
            name="Observado",
            line=dict(
                color=CORES[nome],
                width=1.8
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=previsao["Data"],
            y=previsao["Limite_superior"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=previsao["Data"],
            y=previsao["Limite_inferior"],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(22,119,173,0.16)",
            line=dict(width=0),
            name="Faixa indicativa",
            hoverinfo="skip"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=previsao["Data"],
            y=previsao["Previsto"],
            mode="lines+markers",
            name="Projeção",
            line=dict(
                color="#CA7132",
                width=2.5,
                dash="dash"
            ),
            marker=dict(size=5)
        )
    )

    fig.add_vline(
        x=previsao["Data"].min(),
        line_dash="dot",
        line_color="#506873"
    )

    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="mm/mês"
    )

    return figura_base(
        fig,
        f"Observado e projetado — {nome}",
        460
    )


def grafico_previsao_anual(
    df,
    coluna,
    nome,
    previsao
):

    observado = anuais_completos(df)

    observado = observado[
        ["Ano", coluna]
    ].dropna()

    anual_previsto = (
        previsao.groupby("Ano")[
            [
                "Previsto",
                "Limite_inferior",
                "Limite_superior"
            ]
        ]
        .sum()
        .reset_index()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=observado["Ano"],
            y=observado[coluna],
            name="Observado",
            marker_color=CORES[nome]
        )
    )

    fig.add_trace(
        go.Bar(
            x=anual_previsto["Ano"],
            y=anual_previsto["Previsto"],
            name="Projetado",
            marker_color="#CE803E"
        )
    )

    fig.update_layout(
        xaxis_title="Ano",
        yaxis_title="Total anual (mm)"
    )

    return (
        figura_base(
            fig,
            f"Totais anuais e projeções — {nome}",
            430
        ),
        anual_previsto
    )


# ============================================================
# 11. PAINEL DE SÉRIES TEMPORAIS
# ============================================================

def painel_series():

    st.header("📈 Análise de Séries Temporais")

    texto("""
    Esta seção apresenta a evolução temporal
    da precipitação e da evapotranspiração no
    Nordeste brasileiro, incluindo séries mensais,
    totais anuais, médias móveis, anomalias,
    sazonalidade, heatmaps e projeções exploratórias.
    """)

    if "series_modo" not in st.session_state:
        st.session_state.series_modo = None

    modo = st.session_state.series_modo

    # --------------------------------------------------------
    # ESCOLHA DA ANÁLISE
    # --------------------------------------------------------

    if modo is None:

        st.subheader("Selecione a análise temporal")

        colunas = st.columns(
            3,
            gap="medium"
        )

        opcoes = [
            (
                "Precipitação",
                "Evolução temporal da precipitação."
            ),
            (
                "Evapotranspiração",
                "Evolução temporal da evapotranspiração."
            ),
            (
                "Comparativo",
                "Comparação temporal entre P e ET."
            )
        ]

        for coluna, (nome, descricao) in zip(
            colunas,
            opcoes
        ):

            with coluna:

                with st.container(border=True):

                    st.markdown(
                        f"### {EMOJIS[nome]} {nome}"
                    )

                    texto(descricao)

                    st.button(
                        f"Analisar {nome}",
                        use_container_width=True,
                        key="serie_" + norm(nome),
                        on_click=lambda n=nome: st.session_state.update(
                            series_modo=n
                        )
                    )

        return

    # --------------------------------------------------------
    # DADOS
    # --------------------------------------------------------

    df = obter_dados()

    if df is None or df.empty:
        return

    titulo, voltar = st.columns(
        [4, 1.25],
        vertical_alignment="center"
    )

    with titulo:

        st.subheader(
            f"{EMOJIS[modo]} {modo}"
        )

    with voltar:

        st.button(
            "← Voltar às análises",
            use_container_width=True,
            key="voltar_series",
            on_click=lambda: st.session_state.update(
                series_modo=None
            )
        )

    # --------------------------------------------------------
    # FILTROS
    # --------------------------------------------------------

    faixa("⚙️ Configuração da análise temporal")

    anos = sorted(
        df["Ano"].unique().tolist()
    )

    c1, c2 = st.columns(2)

    with c1:

        ai, af = st.select_slider(
            "Período observado",
            options=anos,
            value=(anos[0], anos[-1]),
            key="series_periodo"
        )

    with c2:

        janela = st.selectbox(
            "Janela da média móvel",
            options=[3, 6, 12],
            index=2,
            format_func=lambda x: f"{x} meses",
            key="series_media_movel"
        )

    dados = df[
        df["Ano"].between(ai, af)
    ].copy()

    nomes = (
        list(COLUNAS)
        if modo == "Comparativo"
        else [modo]
    )

    st.caption(
        f"Período observado: {ai}–{af} | "
        f"Média móvel: {janela} meses."
    )

    # --------------------------------------------------------
    # INDICADORES
    # --------------------------------------------------------

    st.divider()

    faixa("📌 Indicadores temporais")

    if modo == "Comparativo":

        indicadores = [
            ("Média mensal P", dados[P].mean()),
            ("Média mensal ET", dados[ET].mean()),
            ("Máximo mensal P", dados[P].max()),
            ("Máximo mensal ET", dados[ET].max())
        ]

    else:

        coluna = COLUNAS[modo]

        indicadores = [
            ("Média mensal", dados[coluna].mean()),
            ("Mediana", dados[coluna].median()),
            ("Máximo mensal", dados[coluna].max()),
            ("Mínimo mensal", dados[coluna].min())
        ]

    for coluna, item in zip(
        st.columns(4),
        indicadores
    ):

        with coluna:

            st.metric(
                item[0],
                f"{num(item[1])} mm"
            )

    # --------------------------------------------------------
    # SÉRIES MENSAIS
    # --------------------------------------------------------

    st.divider()

    faixa("📉 Séries mensais e médias móveis")

    texto("""
    As séries mensais apresentam os registros observados.
    As médias móveis suavizam parte das oscilações de
    curto prazo e facilitam a identificação de padrões
    gerais no comportamento temporal das variáveis.
    """)

    if modo == "Comparativo":

        c1, c2 = st.columns(2)

        with c1:

            mostrar_grafico(
                grafico_serie_mensal(
                    dados,
                    P,
                    "Precipitação",
                    janela
                ),
                "serie_mensal_p"
            )

        with c2:

            mostrar_grafico(
                grafico_serie_mensal(
                    dados,
                    ET,
                    "Evapotranspiração",
                    janela
                ),
                "serie_mensal_et"
            )

    else:

        mostrar_grafico(
            grafico_serie_mensal(
                dados,
                COLUNAS[modo],
                modo,
                janela
            ),
            "serie_mensal_unica"
        )

    # --------------------------------------------------------
    # SÉRIES ANUAIS
    # --------------------------------------------------------

    st.divider()

    faixa("📊 Totais anuais e tendências lineares")

    texto("""
    Os totais anuais permitem observar a variabilidade
    interanual. A linha de tendência corresponde a um
    ajuste linear descritivo e não representa, isoladamente,
    evidência de mudança climática.
    """)

    if modo == "Comparativo":

        c1, c2 = st.columns(2)

        with c1:

            mostrar_grafico(
                grafico_serie_anual(
                    dados,
                    P,
                    "Precipitação"
                ),
                "serie_anual_p"
            )

        with c2:

            mostrar_grafico(
                grafico_serie_anual(
                    dados,
                    ET,
                    "Evapotranspiração"
                ),
                "serie_anual_et"
            )

    else:

        mostrar_grafico(
            grafico_serie_anual(
                dados,
                COLUNAS[modo],
                modo
            ),
            "serie_anual_unica"
        )

    # --------------------------------------------------------
    # HEATMAP
    # --------------------------------------------------------

    st.divider()

    faixa("🗓️ Heatmap — ano × mês")

    texto("""
    O heatmap representa a distribuição dos valores
    mensais de cada ano. A intensidade das cores permite
    identificar períodos relativamente mais elevados
    ou reduzidos e observar a sazonalidade.
    """)

    if modo == "Comparativo":

        variavel_heatmap = st.selectbox(
            "Variável do heatmap",
            options=[
                "Precipitação",
                "Evapotranspiração"
            ],
            key="series_heatmap_variavel"
        )

    else:

        variavel_heatmap = modo

    mostrar_grafico(
        grafico_heatmap(
            dados,
            COLUNAS[variavel_heatmap],
            variavel_heatmap
        ),
        "heatmap_temporal"
    )

    # --------------------------------------------------------
    # ANOMALIAS
    # --------------------------------------------------------

    st.divider()

    faixa("📈 Anomalias mensais")

    texto("""
    As anomalias representam a diferença entre
    o registro observado e a média histórica
    daquele mês no intervalo analisado.
    """)

    if modo == "Comparativo":

        c1, c2 = st.columns(2)

        with c1:

            mostrar_grafico(
                grafico_anomalias(
                    dados,
                    P,
                    "Precipitação"
                ),
                "anomalia_p"
            )

        with c2:

            mostrar_grafico(
                grafico_anomalias(
                    dados,
                    ET,
                    "Evapotranspiração"
                ),
                "anomalia_et"
            )

    else:

        mostrar_grafico(
            grafico_anomalias(
                dados,
                COLUNAS[modo],
                modo
            ),
            "anomalia_unica"
        )

    # --------------------------------------------------------
    # SAZONALIDADE
    # --------------------------------------------------------

    st.divider()

    faixa("🌦️ Sazonalidade hidroclimática")

    medias_mensais = (
        dados.groupby("Mes")[
            [COLUNAS[n] for n in nomes]
        ]
        .mean()
        .reindex(range(1, 13))
    )

    fig_sazonal = go.Figure()

    for nome in nomes:

        fig_sazonal.add_trace(
            go.Scatter(
                x=MESES,
                y=medias_mensais[COLUNAS[nome]],
                mode="lines+markers",
                name=nome,
                line=dict(
                    color=CORES[nome],
                    width=3
                )
            )
        )

    fig_sazonal.update_layout(
        xaxis_title="Mês",
        yaxis_title="Média mensal (mm)"
    )

    mostrar_grafico(
        figura_base(
            fig_sazonal,
            "Ciclo sazonal médio",
            400
        ),
        "series_sazonal"
    )

    # --------------------------------------------------------
    # PROJEÇÃO 2025-2028
    # --------------------------------------------------------

    st.divider()

    faixa("🔮 Projeção exploratória até 2028")

    texto("""
    As projeções combinam uma tendência linear estimada
    a partir das médias anuais e um padrão sazonal
    calculado com os registros mensais. São estimativas
    estatísticas exploratórias, não previsões meteorológicas
    operacionais. As faixas de incerteza são indicativas
    e não representam intervalos probabilísticos calibrados.
    """)

    st.caption(
        "As projeções utilizam os anos completos "
        "disponíveis na planilha, independentemente "
        "do filtro de visualização."
    )

    ultimo_ano = int(
        df["Ano"].max()
    )

    if ultimo_ano >= 2028:

        st.warning(
            "A planilha já contém dados de 2028 "
            "ou posteriores. Não existe horizonte "
            "futuro até 2028."
        )

    else:

        previsoes = {}

        for nome in nomes:

            previsao, erro = prever_serie(
                df,
                COLUNAS[nome],
                ano_final=2028
            )

            if erro:

                st.warning(
                    f"{nome}: {erro}"
                )

            else:

                previsoes[nome] = previsao

        if previsoes:

            if len(previsoes) == 2:

                col1, col2 = st.columns(2)

                for coluna_visual, nome in zip(
                    [col1, col2],
                    previsoes
                ):

                    with coluna_visual:

                        mostrar_grafico(
                            grafico_previsao(
                                df,
                                COLUNAS[nome],
                                nome,
                                previsoes[nome]
                            ),
                            "prev_mensal_" + norm(nome)
                        )

            else:

                nome = list(previsoes)[0]

                mostrar_grafico(
                    grafico_previsao(
                        df,
                        COLUNAS[nome],
                        nome,
                        previsoes[nome]
                    ),
                    "prev_mensal_unica"
                )

            # ------------------------------------------------
            # PROJEÇÕES ANUAIS
            # ------------------------------------------------

            faixa("📊 Totais anuais observados e projetados")

            tabelas = []

            for nome, previsao in previsoes.items():

                fig, anual = grafico_previsao_anual(
                    df,
                    COLUNAS[nome],
                    nome,
                    previsao
                )

                mostrar_grafico(
                    fig,
                    "prev_anual_" + norm(nome)
                )

                anual["Variável"] = nome

                tabelas.append(anual)

            if tabelas:

                tabela_final = pd.concat(
                    tabelas,
                    ignore_index=True
                )

                tabela_final = tabela_final.rename(
                    columns={
                        "Previsto": "Total previsto (mm)",
                        "Limite_inferior": "Limite inferior indicativo (mm)",
                        "Limite_superior": "Limite superior indicativo (mm)"
                    }
                )

                st.markdown(
                    "**Tabela das projeções anuais**"
                )

                st.dataframe(
                    tabela_final,
                    use_container_width=True,
                    hide_index=True
                )

                st.caption(
                    "Os limites anuais são somas dos "
                    "limites mensais indicativos, não "
                    "intervalos probabilísticos calibrados."
                )

                csv = tabela_final.to_csv(
                    index=False,
                    sep=";",
                    decimal=","
                ).encode("utf-8-sig")

                st.download_button(
                    "⬇️ Baixar projeções até 2028",
                    data=csv,
                    file_name="projecoes_hidroclima_2028.csv",
                    mime="text/csv",
                    key="baixar_previsoes"
                )

    # --------------------------------------------------------
    # CONSULTA AOS DADOS
    # --------------------------------------------------------

    st.divider()

    with st.expander(
        "📋 Consultar e baixar séries observadas"
    ):

        consulta = dados[
            ["Ano", "Mes", "Mes_nome", "Data"]
            + [COLUNAS[n] for n in nomes]
        ].copy()

        st.dataframe(
            consulta,
            use_container_width=True,
            hide_index=True
        )

        csv = consulta.to_csv(
            index=False,
            sep=";",
            decimal=","
        ).encode("utf-8-sig")

        st.download_button(
            "⬇️ Baixar séries observadas",
            data=csv,
            file_name=f"series_{ai}_{af}.csv",
            mime="text/csv",
            key="baixar_series_observadas"
        )

    # --------------------------------------------------------
    # NOTAS METODOLÓGICAS
    # --------------------------------------------------------

    with st.expander(
        "📚 Fórmulas e notas metodológicas"
    ):

        st.subheader("1. Média móvel")

        texto("""
        A média móvel simples corresponde à média dos
        valores observados em uma janela temporal
        de comprimento definido.
        """)

        st.latex(
            r"MM_t=\frac{1}{k}\sum_{i=0}^{k-1}X_{t-i}"
        )

        st.subheader("2. Anomalia mensal")

        st.latex(
            r"A_{y,m}=X_{y,m}-\overline{X}_{m}"
        )

        texto("""
        A anomalia é calculada como a diferença
        entre o valor observado e a média histórica
        correspondente ao mesmo mês.
        """)

        st.subheader("3. Tendência linear")

        st.latex(
            r"\hat{Y}_t=\alpha+\beta t"
        )

        texto("""
        O coeficiente beta representa a inclinação
        da reta ajustada pelo método dos mínimos quadrados.
        """)

        st.subheader("4. Modelo sazonal de projeção")

        st.latex(
            r"\hat{X}_{y,m}="
            r"\alpha+\beta(y-\bar{y})+S_m"
        )

        texto("""
        O modelo combina tendência linear e um
        componente sazonal mensal. Valores previstos
        negativos são limitados a zero.
        """)

        st.subheader("5. Faixa indicativa")

        st.latex(
            r"L_{y,m}^{\pm}="
            r"\hat{X}_{y,m}\pm1.282s_e\sqrt{h}"
        )

        texto("""
        O termo s_e representa o desvio padrão dos resíduos,
        e h representa o horizonte em anos desde o
        último ano observado. Essa faixa não foi calibrada
        nem validada como intervalo probabilístico.
        """)

        st.subheader("6. Limitações da previsão")

        texto("""
        O modelo não incorpora informações futuras de
        temperatura, circulação atmosférica, El Niño,
        La Niña ou alterações no uso do solo. As projeções
        devem ser interpretadas apenas como extrapolações
        exploratórias dos padrões históricos.
        """)


# ============================================================
# 12. VISUALIZADOR DE MAPAS
# ============================================================

def visualizar_mapas():

    if "mapa_variavel" not in st.session_state:
        st.session_state.mapa_variavel = None

    variavel = st.session_state.mapa_variavel

    if variavel is None:

        st.subheader(
            "Selecione a variável hidroclimática"
        )

        colunas = st.columns(
            2,
            gap="large"
        )

        for coluna, nome in zip(
            colunas,
            [
                "Precipitação",
                "Evapotranspiração"
            ]
        ):

            with coluna:

                with st.container(border=True):

                    st.markdown(
                        f"### {EMOJIS[nome]} {nome}"
                    )

                    texto(
                        f"Visualização dos mapas de "
                        f"{nome.lower()} no Nordeste brasileiro."
                    )

                    st.button(
                        "Visualizar " + nome,
                        key="mapa_btn_" + norm(nome),
                        use_container_width=True,
                        on_click=lambda n=nome: st.session_state.update(
                            mapa_variavel=n
                        )
                    )

        return

    titulo, botao = st.columns(
        [4, 1.3],
        vertical_alignment="center"
    )

    with titulo:

        st.subheader(
            f"{EMOJIS[variavel]} Mapas de {variavel}"
        )

    with botao:

        st.button(
            "← Voltar às variáveis",
            use_container_width=True,
            key="voltar_mapa",
            on_click=lambda: st.session_state.update(
                mapa_variavel=None
            )
        )

    raiz = localizar(
        BASE,
        "Mapas_Nordeste"
    )

    pasta = localizar(
        raiz,
        variavel
    )

    if pasta is None:

        st.error(
            f"Pasta Mapas_Nordeste/{variavel} "
            "não encontrada."
        )

        return

    esquerda, direita = st.columns(
        [1, 3],
        gap="large"
    )

    # --------------------------------------------------------
    # CONTROLES À ESQUERDA
    # --------------------------------------------------------

    with esquerda:

        faixa("⚙️ Seleção dos Mapas")

        st.markdown(
            f"**Variável:** {EMOJIS[variavel]} {variavel}"
        )

        periodo = st.selectbox(
            "📅 Periodicidade",
            list(PERIODOS),
            key="mapa_periodo_" + norm(variavel)
        )

        pasta = localizar(
            pasta,
            PERIODOS[periodo]
        )

        if pasta is None:

            st.warning(
                "Pasta da periodicidade não encontrada."
            )

            return

        decada = None

        if periodo == "Por década":

            decada = st.selectbox(
                "📂 Década",
                [
                    "2000s",
                    "2010s",
                    "2020s"
                ],
                key="mapa_decada_" + norm(variavel)
            )

            pasta = localizar(
                pasta,
                decada
            )

            if pasta is None:

                st.warning(
                    "Pasta da década não encontrada."
                )

                return

        prefixo = norm(
            variavel + "_Nordeste"
        )

        encontrados = {}

        for arq in pasta.iterdir():

            if (
                arq.is_file()
                and arq.suffix.lower() in EXTENSOES
            ):

                padrao = (
                    rf"{re.escape(prefixo)}"
                    rf"((?:19|20)\d{{2}})"
                )

                resultado = re.fullmatch(
                    padrao,
                    norm(arq.stem)
                )

                if resultado:

                    encontrados[
                        int(resultado.group(1))
                    ] = arq

        if not encontrados:

            st.warning(
                "Nenhum mapa disponível nessa pasta."
            )

            return

        anos = sorted(encontrados)

        ano = st.selectbox(
            "🔎 Ano de interesse",
            anos,
            key=(
                "mapa_ano_"
                + norm(variavel)
                + "_"
                + norm(periodo)
                + "_"
                + str(decada)
            )
        )

        st.caption(
            f"Intervalo: {min(anos)}–{max(anos)}"
        )

    # --------------------------------------------------------
    # MAPA À DIREITA
    # --------------------------------------------------------

    with direita:

        faixa("🗺️ Visualização Cartográfica")

        st.markdown(
            '<div class="metadata">'
            f'<span>Variável: {escape(variavel)}</span>'
            '<span>Nordeste</span>'
            f'<span>{escape(periodo)}</span>'
            f'<span>Ano: {ano}</span>'
            '</div>',
            unsafe_allow_html=True
        )

        try:

            st.image(
                str(encontrados[ano]),
                use_container_width=True
            )

        except Exception as erro:

            st.error(
                f"Erro ao abrir mapa: {erro}"
            )


# ============================================================
# 13. CABEÇALHO PRINCIPAL
# ============================================================

st.markdown(
    '<div class="cabecalho">'
    '<h1>💧 HidroClima Nordeste</h1>'
    '<p>'
    'Plataforma de análise da precipitação e da '
    'evapotranspiração no Nordeste brasileiro, '
    'com informações hidroclimáticas provenientes '
    'de sensoriamento remoto e processamento geoespacial.'
    '</p>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# 14. BARRA LATERAL
# ============================================================

with st.sidebar:

    st.title("💧 HidroClima")

    st.caption("Nordeste Brasileiro")

    st.divider()

    st.markdown("### 🌎 Área de estudo")

    st.write(
        "Região Nordeste do Brasil"
    )

    st.markdown("### 🌊 Variáveis")

    st.write("🌧️ Precipitação")
    st.write("💧 Evapotranspiração")
  

    st.divider()

    st.markdown("### 🛰️ Tecnologias")

    st.write("Google Earth Engine")
    st.write("Python")
    st.write("Streamlit")
    st.write("Sensoriamento remoto")

    st.divider()

    st.caption(
        "Versão 1.9 — HidroClima Nordeste"
    )


# ============================================================
# 15. ABAS PRINCIPAIS
# ============================================================

abas = st.tabs([
    "👥 Autores",
    "📚 Documentação",
    "📖 Resumo",
    "🔬 Materiais e Métodos",
    "📊 Descritivo",
    "📈 Séries Temporais",
    "🗺️ Mapas",
    "✅ Conclusão"
])


# ============================================================
# ABA 1 - AUTORES
# ============================================================


# ============================================================
# ABA 1 - AUTORES
# ============================================================

with abas[0]:

    st.header("👥 Autores")

    texto("""
    Esta seção apresenta os pesquisadores responsáveis
    pelo desenvolvimento da plataforma HidroClima Nordeste,
    suas respectivas instituições acadêmicas, informações
    de contato e identificadores científicos.
    """)

    # --------------------------------------------------------
    # INFORMAÇÕES DOS AUTORES
    # --------------------------------------------------------

    autores = [
        {
            "nome": "Denilson de Oliveira Silva",
            "instituicao": (
                "Universidade Federal Rural de Pernambuco "
                "(UFRPE)"
            ),
            "vinculo": (
                "Programa de Pós-Graduação em Biometria "
                "e Estatística Aplicada"
            ),
            "local": "Recife, Pernambuco, Brasil",
            "email": "denilson.oliveira@ufrpe.br",
            "orcid": (
                "https://orcid.org/0009-0000-4031-7772"
            ),
            "lattes": (
                "http://lattes.cnpq.br/0351473442865925"
            )
        },

        {
            "nome": "Jader da Silva Jale",
            "instituicao": (
                "Universidade Federal Rural de Pernambuco "
                "(UFRPE)"
            ),
            "vinculo": (
                "Programa de Pós-Graduação em Biometria "
                "e Estatística Aplicada"
            ),
            "local": "Recife, Pernambuco, Brasil",
            "email": "jader.silvajale@ufrpe.br",
            "orcid": (
                "https://orcid.org/0000-0001-7414-1154"
            ),
            "lattes": (
                "http://lattes.cnpq.br/8171702059557650"
            )
        },

        {
            "nome": "Silvio Fernando Alves Xavier",
            "instituicao": (
                "Universidade Estadual da Paraíba "
                "(UEPB)"
            ),
            "vinculo": "Departamento de Estatística",
            "local": "Campina Grande, Paraíba, Brasil",
            "email": "silvio@servidor.uepb.edu.br",
            "orcid": (
                "https://orcid.org/0000-0002-4832-0711"
            ),
            "lattes": (
                "http://lattes.cnpq.br/7089093133803231"
            )
        },

        {
            "nome": "Débora de Sousa Cordeiro",
            "instituicao": "Universidade Estadual da Paraíba (UEPB)",
            "vinculo": "Departamento de Estatística",
            "local": "Campina Grande, Paraíba, Brasil",
            "email": "ddesousacordeiro2015@gmail.com",
            "orcid": "https://orcid.org/0009-0006-1410-4718",
            "lattes": "http://lattes.cnpq.br/1980673256363690"
        }
    ]

    # --------------------------------------------------------
    # CARTÕES DOS PESQUISADORES
    # --------------------------------------------------------

    colunas = st.columns(
        4,
        gap="medium"
    )

    for coluna, autor in zip(colunas, autores):

        with coluna:

            with st.container(border=True):

                st.markdown(
                    f"### 👤 {autor['nome']}"
                )

                st.markdown(
                    f"**🏛️ Instituição:** "
                    f"{autor['instituicao']}"
                )

                st.markdown(
                    f"**🎓 Vínculo acadêmico:** "
                    f"{autor['vinculo']}"
                )

                st.markdown(
                    f"**📍 Localização:** "
                    f"{autor['local']}"
                )

                st.divider()

                st.markdown(
                    "#### 📬 Contato"
                )

                st.markdown(
                    f"**E-mail:** "
                    f"[{autor['email']}]"
                    f"(mailto:{autor['email']})"
                )

                st.divider()

                st.markdown(
                    "#### 🔗 Identificadores acadêmicos"
                )

                st.markdown(
                    f"**ORCID:** "
                    f"[Visualizar perfil]({autor['orcid']})"
                )

                st.markdown(
                    f"**Currículo Lattes:** "
                    f"[Acessar currículo]({autor['lattes']})"
                )

    # --------------------------------------------------------
    # INSTITUIÇÕES ENVOLVIDAS
    # --------------------------------------------------------

    st.divider()

    st.subheader("🏛️ Instituições Acadêmicas")

    texto("""
    O desenvolvimento da plataforma envolve pesquisadores
    vinculados à Universidade Federal Rural de Pernambuco
    (UFRPE), por meio do Programa de Pós-Graduação em
    Biometria e Estatística Aplicada, e à Universidade
    Estadual da Paraíba (UEPB), por meio do Departamento
    de Estatística.
    """)

    # --------------------------------------------------------
    # INFORMAÇÕES COMPLEMENTARES
    # --------------------------------------------------------

    st.subheader("📚 Identificação Científica")

    texto("""
    Os identificadores ORCID e os currículos Lattes
    disponibilizados nesta seção permitem acessar
    informações sobre a trajetória acadêmica,
    produção científica e atuação dos pesquisadores
    participantes do projeto.
    """)



# ============================================================
# ABA 2 - DOCUMENTAÇÃO
# ============================================================


# ============================================================
# ABA 2 - DOCUMENTAÇÃO COMPLETA DA APLICAÇÃO
# ============================================================

with abas[1]:

    st.header("📚 Documentação da Aplicação")

    texto("""
    A plataforma HidroClima Nordeste foi desenvolvida
    com o objetivo de organizar, analisar e visualizar
    informações hidroclimáticas referentes à precipitação
    e à evapotranspiração na região Nordeste do Brasil.
    A aplicação reúne procedimentos de aquisição de dados,
    processamento geoespacial, organização de informações,
    análise estatística e visualização interativa.

    O desenvolvimento foi realizado utilizando a linguagem
    Python e o framework Streamlit, permitindo integrar
    informações tabulares, indicadores estatísticos,
    gráficos temporais e produtos cartográficos em um
    ambiente único. A plataforma foi estruturada de
    maneira modular, possibilitando a atualização das
    bases de dados, a ampliação dos procedimentos
    analíticos e a incorporação de novas funcionalidades.
    """)

    st.divider()

    # ========================================================
    # 1. AQUISIÇÃO DOS DADOS
    # ========================================================

    st.subheader("1. Origem e aquisição dos dados")

    texto("""
    Os dados utilizados no desenvolvimento da aplicação
    foram obtidos por meio do Google Earth Engine (GEE),
    uma plataforma de computação em nuvem que disponibiliza
    coleções de dados geoespaciais e ferramentas para
    processamento de informações provenientes de
    sensoriamento remoto e outras fontes ambientais.

    A aquisição das informações teve como foco a região
    Nordeste do Brasil, considerando duas variáveis
    hidroclimáticas principais: precipitação e
    evapotranspiração. Essas variáveis foram selecionadas
    devido à sua importância para a compreensão da
    dinâmica do ciclo hidrológico, da disponibilidade
    hídrica e das interações entre a superfície terrestre
    e a atmosfera.

    O conjunto de dados organizado para a aplicação
    compreende o período de 2000 a 2024, permitindo
    investigar a variabilidade mensal e interanual
    das variáveis e representar espacialmente suas
    distribuições na área de estudo.
    """)

    st.subheader("1.1. Ambiente de processamento")

    texto("""
    Além do Google Earth Engine, foi informado o uso
    do RIT Ignite no desenvolvimento do trabalho.
    A descrição específica de sua participação no
    fluxo de aquisição, processamento ou execução
    computacional será complementada de acordo com
    os procedimentos efetivamente realizados.

    A utilização de ambientes computacionais voltados
    ao processamento e à análise de dados contribui
    para a organização de rotinas científicas e
    para a integração de diferentes etapas de
    desenvolvimento da aplicação.
    """)

    st.subheader("1.2. Produtos e coleções utilizados")

    texto("""
    As informações de precipitação e evapotranspiração
    foram obtidas de bases geoespaciais acessadas
    por meio do Google Earth Engine. A identificação
    definitiva das coleções utilizadas, dos sensores,
    da resolução espacial, da resolução temporal,
    das unidades originais e dos fatores de conversão
    deverá ser incorporada à documentação técnica.

    Essas informações são necessárias para garantir
    a rastreabilidade dos dados e permitir que outros
    pesquisadores compreendam e reproduzam os
    procedimentos de obtenção e processamento.
    """)

    st.caption(
        "Informações a complementar: nomes das coleções "
        "GEE, identificadores dos produtos, resoluções "
        "e fatores de conversão."
    )

    # ========================================================
    # 2. ÁREA DE ESTUDO
    # ========================================================

    st.divider()

    st.subheader("2. Caracterização da área de estudo")

    texto("""
    A área de estudo corresponde à região Nordeste
    do Brasil, composta por nove estados e caracterizada
    por expressiva diversidade de condições climáticas,
    ambientais e hidrológicas. A região apresenta
    contrastes na distribuição da precipitação,
    na cobertura vegetal e na disponibilidade de água,
    especialmente entre áreas litorâneas, zonas
    de transição e regiões semiáridas.

    A análise conjunta da precipitação e da
    evapotranspiração é relevante para investigar
    as relações entre a entrada de água no sistema
    terrestre e sua transferência para a atmosfera.
    A representação espacial dessas variáveis
    possibilita identificar padrões regionais,
    diferenças entre períodos e possíveis
    concentrações de valores elevados ou reduzidos.

    Os produtos cartográficos utilizados no aplicativo
    correspondem à delimitação espacial adotada durante
    o processamento dos dados. A fonte do limite
    geográfico e os procedimentos específicos
    de recorte serão documentados posteriormente.
    """)

    # ========================================================
    # 3. PROCESSAMENTO
    # ========================================================

    st.divider()

    st.subheader("3. Processamento das informações")

    texto("""
    O fluxo de trabalho foi organizado para integrar
    as informações obtidas no ambiente geoespacial
    às ferramentas de análise e visualização em Python.
    Os dados foram estruturados em registros temporais
    e produtos cartográficos, de forma a permitir
    a interpretação tanto da evolução das variáveis
    ao longo dos anos quanto de sua distribuição espacial.

    Os procedimentos analíticos implementados no
    aplicativo utilizam valores mensais de precipitação
    e evapotranspiração expressos em milímetros.
    A partir desses registros, são calculadas
    estatísticas descritivas, agregações anuais,
    médias móveis, anomalias, correlações e
    projeções estatísticas exploratórias.

    Os mapas temáticos são apresentados a partir
    de arquivos de imagem previamente produzidos
    e organizados em diretórios locais. Dessa forma,
    o visualizador cartográfico não realiza novos
    cálculos geoespaciais sobre as imagens durante
    a navegação, mas permite consultar os produtos
    existentes de maneira interativa.
    """)

    # ========================================================
    # 4. ORGANIZAÇÃO DA BASE DE DADOS
    # ========================================================

    st.divider()

    st.subheader("4. Organização da base de dados")

    texto("""
    As informações utilizadas nas análises estatísticas
    e temporais foram organizadas em um arquivo Excel
    denominado Nordeste_2000_2024_precipitacao_
    evapotranspiracao.xlsx, composto por três planilhas:
    Mensal, Precipitacao e Evapotranspiracao.

    Essa organização permite manter os registros
    mensais e os dados anuais em estruturas
    complementares, facilitando a consulta,
    a verificação e a integração das informações
    ao aplicativo desenvolvido em Streamlit.
    """)

    st.subheader("4.1. Planilha Mensal")

    texto("""
    A planilha Mensal constitui a principal fonte
    de dados utilizada nos cálculos interativos
    das abas Descritivo e Séries Temporais. Ela
    apresenta os campos Ano, Mes, Mes_nome,
    Precipitacao_mm_mes e Evapotranspiracao_mm_mes.

    Cada registro corresponde a determinado mês
    e ano, contendo os valores das duas variáveis
    hidroclimáticas. Essa estrutura permite calcular
    médias mensais, medidas de dispersão, agregações
    anuais, relações estatísticas e indicadores
    de variabilidade temporal.

    A utilização de uma base mensal integrada
    também possibilita comparar diretamente
    precipitação e evapotranspiração em intervalos
    temporais equivalentes.
    """)

    st.subheader("4.2. Planilha Precipitacao")

    texto("""
    A planilha Precipitacao apresenta os registros
    organizados por ano, contendo os valores dos
    doze meses e uma coluna de total anual,
    denominada Total_anual_mm.

    Essa organização facilita a consulta aos
    acumulados anuais e a comparação dos valores
    registrados entre diferentes anos. Na versão
    atual do aplicativo, os totais apresentados
    nas análises interativas são calculados a
    partir dos registros da planilha Mensal,
    considerando apenas anos com doze meses válidos.
    """)

    st.subheader("4.3. Planilha Evapotranspiracao")

    texto("""
    A planilha Evapotranspiracao apresenta estrutura
    semelhante à da precipitação, organizando
    os valores mensais por ano e disponibilizando
    um total anual para cada período.

    Esses registros permitem consultar a magnitude
    da evapotranspiração ao longo do tempo e comparar
    o comportamento anual dessa variável com o da
    precipitação. Assim como na precipitação, as
    análises interativas utilizam a base Mensal
    para realizar os cálculos apresentados.
    """)

    # ========================================================
    # 5. ESTRUTURA DA APLICAÇÃO
    # ========================================================

    st.divider()

    st.subheader("5. Desenvolvimento da aplicação")

    texto("""
    A plataforma HidroClima Nordeste foi implementada
    na linguagem Python, utilizando o framework
    Streamlit para a construção da interface web.
    A aplicação permite executar análises e apresentar
    resultados diretamente no navegador, sem a
    necessidade de desenvolver uma interface
    independente utilizando linguagens tradicionais
    de programação web.

    As bibliotecas Pandas e NumPy são utilizadas
    para leitura, organização e processamento
    das informações numéricas. A biblioteca Plotly
    é empregada na elaboração de gráficos
    interativos, enquanto o Streamlit organiza
    os elementos visuais, os controles de seleção,
    as tabelas e os mecanismos de exportação
    dos resultados.

    A interface foi estruturada com um padrão visual
    relacionado aos elementos hídricos, utilizando
    tonalidades de azul e verde-água, texto com
    contraste adequado e recursos de navegação
    que permitem selecionar variáveis e períodos
    de interesse.
    """)

    # ========================================================
    # 6. ABA AUTORES
    # ========================================================

    st.divider()

    st.subheader("6. Aba Autores")

    texto("""
    A aba Autores apresenta as informações acadêmicas
    e institucionais dos pesquisadores responsáveis
    pelo desenvolvimento da plataforma HidroClima
    Nordeste: Denilson de Oliveira Silva, Jader da
    Silva Jale, Silvio Fernando Alves Xavier e
    Débora de Sousa Cordeiro.

    Nessa seção são disponibilizados os vínculos
    institucionais, os endereços eletrônicos,
    os identificadores ORCID e os links para
    os currículos Lattes. O objetivo é permitir
    a identificação dos pesquisadores e facilitar
    o acesso às suas informações acadêmicas
    e produções científicas.
    """)

    # ========================================================
    # 7. ABA DOCUMENTAÇÃO
    # ========================================================

    st.divider()

    st.subheader("7. Aba Documentação")

    texto("""
    A aba Documentação reúne as informações
    relacionadas à origem dos dados, à área
    de estudo, à organização da base, aos
    procedimentos computacionais e à estrutura
    de funcionamento da aplicação.

    Essa seção foi desenvolvida para registrar
    o fluxo metodológico utilizado no projeto
    e facilitar a compreensão dos procedimentos
    empregados. A documentação também contribui
    para a transparência, rastreabilidade
    e possibilidade de reprodução das análises.
    """)

    # ========================================================
    # 8. ABA RESUMO
    # ========================================================

    st.divider()

    st.subheader("8. Aba Resumo")

    texto("""
    A aba Resumo apresenta uma descrição geral
    da proposta científica e tecnológica do
    HidroClima Nordeste, destacando sua finalidade,
    seu objetivo geral e os principais objetivos
    específicos.

    Essa seção permite ao usuário compreender
    a motivação do desenvolvimento da plataforma,
    as variáveis investigadas e os tipos de
    análises disponibilizadas. O resumo científico
    definitivo poderá ser complementado
    posteriormente com os principais resultados
    obtidos durante a investigação.
    """)

    # ========================================================
    # 9. ABA MATERIAIS E MÉTODOS
    # ========================================================

    st.divider()

    st.subheader("9. Aba Materiais e Métodos")

    texto("""
    A aba Materiais e Métodos apresenta a fundamentação
    conceitual e metodológica utilizada na aplicação.
    São abordadas a área de estudo, as bases de dados,
    os conceitos de precipitação e evapotranspiração,
    a transpiração vegetal e os principais recursos
    computacionais utilizados.

    A seção apresenta expressões matemáticas
    relacionadas à precipitação acumulada,
    à decomposição da evapotranspiração em
    evaporação e transpiração e à evapotranspiração
    de referência pelo método Penman-Monteith FAO-56.

    A equação de Penman-Monteith é incluída como
    fundamentação teórica, não constituindo
    necessariamente o método de estimativa
    utilizado no produto de evapotranspiração
    obtido do Google Earth Engine.

    Também são descritos os conceitos de
    sensoriamento remoto, processamento
    geoespacial, linguagem Python e framework
    Streamlit, estabelecendo a relação entre
    os recursos metodológicos e tecnológicos
    empregados no projeto.
    """)

    # ========================================================
    # 10. ABA DESCRITIVO
    # ========================================================

    st.divider()

    st.subheader("10. Aba Descritivo")

    texto("""
    A aba Descritivo foi desenvolvida para
    caracterizar estatisticamente os registros
    mensais de precipitação e evapotranspiração
    no Nordeste brasileiro. O usuário pode
    selecionar individualmente uma das variáveis
    ou utilizar o modo comparativo, que apresenta
    informações das duas variáveis simultaneamente.

    A interface permite definir o período de
    análise e atualiza automaticamente os
    indicadores estatísticos e os gráficos
    apresentados. Entre as medidas calculadas
    estão média aritmética, mediana, valores
    mínimo e máximo, desvio padrão, coeficiente
    de variação, quartis e amplitude.

    A aplicação apresenta diagramas de caixa
    (boxplots), histogramas, gráficos de médias
    mensais e tabelas estatísticas. Os boxplots
    permitem examinar a dispersão dos registros
    e identificar possíveis valores extremos,
    enquanto os histogramas apresentam a
    distribuição de frequência dos valores.

    No modo comparativo, a aplicação também
    apresenta um diagrama de dispersão para
    investigar a associação linear entre
    precipitação e evapotranspiração, utilizando
    o coeficiente de correlação de Pearson.

    Outro recurso implementado consiste na
    diferença entre precipitação e
    evapotranspiração, expressa por P menos ET.
    Esse indicador permite comparar as magnitudes
    mensais das duas variáveis, mas não representa
    um balanço hídrico completo, pois não considera
    diretamente componentes como armazenamento
    e escoamento.

    A aba também permite consultar os registros
    utilizados nos cálculos, exportar os dados
    filtrados em formato CSV e acessar notas
    metodológicas contendo expressões matemáticas
    e explicações das medidas estatísticas.
    """)

    # ========================================================
    # 11. ABA SÉRIES TEMPORAIS
    # ========================================================

    st.divider()

    st.subheader("11. Aba Séries Temporais")

    texto("""
    A aba Séries Temporais foi estruturada para
    investigar a evolução da precipitação e da
    evapotranspiração ao longo do período
    de observação. Assim como na análise
    descritiva, o usuário pode selecionar
    uma variável individual ou o modo comparativo.

    O painel disponibiliza séries mensais,
    totais anuais e médias móveis de três,
    seis e doze meses. As médias móveis
    são utilizadas para suavizar oscilações
    de curto prazo, facilitando a visualização
    de padrões temporais mais persistentes.

    A análise dos totais anuais permite
    examinar a variabilidade interanual,
    sendo apresentada uma linha de tendência
    ajustada por regressão linear simples.
    Esse ajuste possui caráter descritivo
    e não deve ser interpretado isoladamente
    como evidência de mudanças climáticas.

    A seção também apresenta mapas de calor
    temporais, denominados heatmaps, que
    organizam os valores de cada variável
    em uma matriz de anos e meses. As cores
    representam as magnitudes dos registros,
    permitindo identificar padrões sazonais
    e diferenças entre os anos.

    Outro procedimento consiste no cálculo
    das anomalias mensais, determinadas pela
    diferença entre o valor observado e a
    média histórica do mês correspondente.
    Essa representação permite identificar
    períodos com valores acima ou abaixo
    do comportamento médio da série.

    O painel inclui ainda gráficos do ciclo
    sazonal médio, permitindo analisar
    a distribuição dos valores ao longo
    dos doze meses do calendário.
    """)

    # ========================================================
    # 12. PREVISÃO ESTATÍSTICA
    # ========================================================

    st.divider()

    st.subheader("12. Projeções estatísticas de 2025 a 2028")

    texto("""
    A seção de Séries Temporais incorpora
    um procedimento de projeção estatística
    exploratória das variáveis hidroclimáticas,
    com horizonte até o ano de 2028,
    considerando a base histórica disponível
    até 2024.

    O método implementado combina uma tendência
    linear estimada a partir das médias anuais
    com um componente sazonal determinado
    pelos registros mensais. A tendência
    busca representar a direção geral da
    série histórica, enquanto o componente
    sazonal incorpora as diferenças médias
    entre os meses do ano.

    Os valores projetados são apresentados
    em gráficos mensais e agregações anuais,
    permitindo comparar visualmente os dados
    observados com as estimativas futuras.
    O aplicativo também disponibiliza faixas
    indicativas de incerteza, construídas
    a partir da dispersão dos resíduos do
    ajuste histórico.

    É importante destacar que essas faixas
    não constituem intervalos probabilísticos
    formalmente calibrados, uma vez que
    não foi implementada uma etapa completa
    de validação preditiva fora da amostra.

    As projeções devem ser interpretadas
    exclusivamente como extrapolações
    estatísticas exploratórias, e não como
    previsões meteorológicas operacionais.
    O modelo não incorpora diretamente
    fenômenos como El Niño e La Niña,
    condições meteorológicas futuras,
    alterações na circulação atmosférica
    ou cenários de mudanças climáticas.
    """)

    # ========================================================
    # 13. ABA MAPAS
    # ========================================================

    st.divider()

    st.subheader("13. Aba Mapas")

    texto("""
    A aba Mapas foi desenvolvida para
    disponibilizar uma visualização
    cartográfica interativa da precipitação
    e da evapotranspiração no Nordeste
    brasileiro. A interface permite
    selecionar inicialmente a variável
    hidroclimática de interesse e,
    posteriormente, a periodicidade
    e o ano desejados.

    O visualizador utiliza arquivos de imagem
    previamente gerados e armazenados na pasta
    Mapas_Nordeste. Os produtos são organizados
    em diretórios específicos de precipitação
    e evapotranspiração, mantendo uma estrutura
    semelhante para as duas variáveis.

    Cada diretório apresenta cinco categorias
    de organização temporal: todos os anos,
    de dois em dois anos, de cinco em cinco
    anos, de dez em dez anos e agrupamentos
    por década.

    Na categoria por década, os arquivos
    são subdivididos em pastas correspondentes
    aos anos 2000, 2010 e 2020. A aplicação
    identifica automaticamente os arquivos
    disponíveis e apresenta apenas os anos
    efetivamente encontrados na pasta
    selecionada.

    A visualização utiliza uma organização
    em duas colunas. Na primeira coluna
    encontram-se os controles de seleção
    da periodicidade, década e ano. Na
    segunda coluna é apresentado o mapa
    temático correspondente à escolha
    realizada pelo usuário.

    As informações exibidas incluem a
    variável hidroclimática, a região
    analisada, a periodicidade e o ano
    selecionado. O painel também dispõe
    de um botão de retorno para permitir
    a escolha de outra variável.

    A apresentação dos mapas facilita a
    observação de diferenças espaciais,
    padrões regionais e possíveis alterações
    na distribuição das variáveis entre
    os períodos representados.
    """)

    # ========================================================
    # 14. ABA CONCLUSÃO
    # ========================================================

    st.divider()

    st.subheader("14. Aba Conclusão")

    texto("""
    A aba Conclusão foi reservada para
    apresentar a síntese dos principais
    resultados científicos obtidos a
    partir da análise integrada das
    informações de precipitação e
    evapotranspiração.

    Essa seção poderá reunir interpretações
    sobre a variabilidade temporal,
    os padrões espaciais identificados,
    as associações entre as variáveis
    e as contribuições da plataforma
    para o monitoramento hidroclimático
    do Nordeste brasileiro.

    A elaboração das conclusões definitivas
    dependerá da interpretação completa
    dos resultados e da avaliação de suas
    limitações metodológicas.
    """)



    # ========================================================
    # 16. INTEGRAÇÃO DOS RESULTADOS
    # ========================================================

    st.divider()

    st.subheader("16. Integração das análises")

    texto("""
    A estrutura do HidroClima Nordeste foi
    planejada para permitir a interpretação
    complementar das informações estatísticas,
    temporais e espaciais. A análise descritiva
    caracteriza a distribuição e a variabilidade
    dos registros, enquanto as séries temporais
    permitem investigar sua evolução ao longo
    dos anos.

    A visualização cartográfica acrescenta
    uma dimensão espacial à interpretação,
    possibilitando observar como as variáveis
    se distribuem geograficamente na região
    Nordeste do Brasil.

    A integração dessas abordagens contribui
    para uma compreensão mais ampla do
    comportamento hidroclimático regional,
    permitindo explorar padrões, contrastes
    e relações entre precipitação e
    evapotranspiração.

    Dessa forma, a plataforma constitui
    uma ferramenta de apoio à organização,
    exploração e comunicação de informações
    hidroclimáticas, com potencial de
    aplicação em atividades acadêmicas,
    científicas e de monitoramento ambiental.
    """)

    # ========================================================
    # 17. REPRODUTIBILIDADE
    # ========================================================

    st.divider()

    st.subheader("17. Reprodutibilidade e atualização")

    texto("""
    A aplicação foi desenvolvida com uma
    estrutura modular que possibilita
    atualizar a base Excel e incorporar
    novos produtos cartográficos sem
    modificar integralmente sua interface.

    Os procedimentos de leitura e processamento
    utilizam os registros disponíveis no arquivo
    de entrada, permitindo que os indicadores
    estatísticos e os gráficos sejam recalculados
    quando novos dados compatíveis forem
    adicionados.

    Para garantir a reprodutibilidade completa
    do estudo, a documentação final deverá
    incluir os scripts originais de aquisição
    e processamento no Google Earth Engine,
    os identificadores dos produtos utilizados,
    os critérios de tratamento dos dados,
    as unidades e os procedimentos de
    agregação temporal e espacial.
    """)

    st.divider()

    st.caption(
        "HidroClima Nordeste | Documentação técnica "
        "e metodológica da aplicação."
    )


# ============================================================
# ABA 3 - RESUMO
# ============================================================


# ============================================================
# ABA 3 - RESUMO DA APLICAÇÃO
# ============================================================

with abas[2]:

    st.header("📖 Resumo da Aplicação")

    # ========================================================
    # 1. RESUMO GERAL
    # ========================================================

    st.subheader("1. Resumo geral")

    texto("""
    O monitoramento da precipitação e da evapotranspiração
    constitui uma importante ferramenta para a compreensão
    da dinâmica hidroclimática, especialmente em regiões
    caracterizadas por elevada variabilidade espacial e
    temporal da disponibilidade hídrica, como o Nordeste
    brasileiro. Nesse contexto, a utilização de dados
    provenientes de sensoriamento remoto, associada a
    ferramentas computacionais de análise e visualização,
    possibilita investigar o comportamento dessas
    variáveis em diferentes escalas temporais e espaciais.

    A plataforma HidroClima Nordeste foi desenvolvida
    com a finalidade de integrar, organizar e apresentar
    informações de precipitação e evapotranspiração
    referentes ao período de 2000 a 2024, utilizando
    dados obtidos por meio do Google Earth Engine (GEE).
    A aplicação foi implementada na linguagem Python,
    com o framework Streamlit, permitindo a construção
    de um ambiente web interativo voltado à exploração
    de informações hidroclimáticas.

    O sistema contempla ferramentas de análise estatística
    descritiva, visualização de séries temporais e
    representação espacial das variáveis. Na análise
    descritiva, são disponibilizadas medidas de tendência
    central e dispersão, histogramas, diagramas de caixa,
    climatologias mensais e indicadores de associação
    entre precipitação e evapotranspiração.

    Na análise temporal, a plataforma disponibiliza
    gráficos de evolução mensal e anual, médias móveis,
    anomalias e mapas de calor temporais, permitindo
    investigar a variabilidade hidroclimática e os
    padrões sazonais. Adicionalmente, são apresentadas
    projeções estatísticas exploratórias até 2028,
    construídas a partir da combinação de tendência
    linear e componentes sazonais dos dados históricos.

    A análise espacial é realizada por meio de mapas
    temáticos organizados em diferentes periodicidades,
    possibilitando examinar a distribuição geográfica
    da precipitação e da evapotranspiração no Nordeste
    brasileiro. A integração dessas funcionalidades
    proporciona um ambiente didático e científico de
    apoio à interpretação de dados hidroclimáticos,
    contribuindo para a exploração de padrões espaciais,
    temporais e estatísticos relevantes ao entendimento
    das condições ambientais da região.
    """)

    st.divider()

    # ========================================================
    # 2. OBJETIVO GERAL
    # ========================================================

    st.subheader("2. Objetivo geral")

    texto("""
    Desenvolver uma plataforma web interativa, utilizando
    a linguagem Python e o framework Streamlit, para
    integrar, analisar e visualizar dados de precipitação
    e evapotranspiração no Nordeste brasileiro, no período
    de 2000 a 2024, provenientes de bases geoespaciais
    acessadas por meio do Google Earth Engine, permitindo
    a realização de análises estatísticas descritivas,
    investigações temporais, projeções exploratórias e
    representações cartográficas, com o propósito de
    auxiliar a compreensão da variabilidade hidroclimática
    regional.
    """)

    st.divider()

    # ========================================================
    # 3. OBJETIVOS ESPECÍFICOS
    # ========================================================

    st.subheader("3. Objetivos específicos")

    texto("""
    Organizar e integrar informações mensais e anuais de
    precipitação e evapotranspiração referentes ao Nordeste
    brasileiro, estruturando uma base de dados que permita
    o processamento, a consulta e a visualização das
    variáveis hidroclimáticas no período de estudo.
    """)

    texto("""
    Caracterizar estatisticamente a precipitação e a
    evapotranspiração por meio do cálculo de medidas de
    tendência central, dispersão e variabilidade, incluindo
    média, mediana, valores mínimos e máximos, desvio
    padrão, quartis e coeficiente de variação.
    """)

   
    texto("""
    Avaliar a associação estatística entre precipitação
    e evapotranspiração por meio de diagramas de dispersão
    e do coeficiente de correlação de Pearson, possibilitando
    examinar a intensidade e o sentido da relação linear
    entre os registros mensais.
    """)

    texto("""
    Analisar a evolução temporal das variáveis
    hidroclimáticas utilizando séries mensais e anuais,
    médias móveis, ajustes de tendência linear e anomalias
    mensais, a fim de explorar padrões de variabilidade
    e possíveis mudanças no comportamento dos registros
    ao longo do período analisado.
    """)

    texto("""
    Identificar padrões sazonais e interanuais da
    precipitação e da evapotranspiração por meio da
    elaboração de climatologias mensais e mapas de
    calor temporais, permitindo comparar a distribuição
    dos valores entre diferentes meses e anos.
    """)


    texto("""
    Disponibilizar mapas temáticos de precipitação
    e evapotranspiração do Nordeste brasileiro,
    organizados em diferentes periodicidades,
    permitindo a seleção interativa de variáveis,
    anos e agrupamentos temporais para a análise
    da distribuição espacial dos dados.
    """)

    texto("""
    Integrar os resultados estatísticos, temporais
    e cartográficos em uma interface acessível,
    organizada e didática, contribuindo para a
    interpretação científica das condições
    hidroclimáticas e para a disseminação de
    informações ambientais da região Nordeste.
    """)

    st.divider()

    # ========================================================
    # 4. PALAVRAS-CHAVE
    # ========================================================

    st.subheader("4. Palavras-chave")

    texto("""
    Precipitação; Evapotranspiração; Nordeste brasileiro;
    Sensoriamento remoto; Google Earth Engine;
    Análise estatística; Séries temporais;
    Variabilidade hidroclimática; Streamlit.
    """)

    st.divider()

    st.caption(
        "HidroClima Nordeste | Síntese e objetivos "
        "da aplicação científica."
    )


# ============================================================
# ABA 4 - MATERIAIS E MÉTODOS
# ============================================================


# ============================================================
# ABA 4 - MATERIAIS E MÉTODOS
# ============================================================

with abas[3]:

    import geopandas as gpd
    import matplotlib.pyplot as plt

    st.header("🔬 Materiais e Métodos")

    # ========================================================
    # 1. ÁREA DE ESTUDO
    # ========================================================

    st.subheader("1. Área de estudo")

    texto("""
    A área de estudo compreende a região Nordeste do Brasil,
    caracterizada por diversidade climática e elevada
    variabilidade espacial e temporal da precipitação
    e da evapotranspiração.
    """)

    # --------------------------------------------------------
    # MAPA DO NORDESTE
    # --------------------------------------------------------

    st.markdown("#### 🗺️ Localização da área de estudo")

    # Localiza automaticamente o shapefile no projeto.
    candidatos_shp = [
        BASE / "nordeste.shp",
        BASE / "Dados" / "nordeste.shp",
        BASE / "Shapefiles" / "nordeste.shp",
        BASE / "Mapas_Nordeste" / "nordeste.shp"
    ]

    caminho_shp = next(
        (p for p in candidatos_shp if p.is_file()),
        None
    )

    if caminho_shp is None:

        st.warning(
            "O arquivo nordeste.shp não foi encontrado. "
            "Coloque o shapefile e seus arquivos auxiliares "
            "na mesma pasta do app.py."
        )

    else:

        try:

            nordeste = gpd.read_file(caminho_shp)

            if nordeste.empty:
                st.warning(
                    "O shapefile não contém geometrias."
                )

            else:

                # Garante um sistema de coordenadas
                # apropriado à visualização.
                if nordeste.crs is not None:

                    nordeste_mapa = nordeste.to_crs(
                        epsg=4674
                    )

                else:

                    nordeste_mapa = nordeste.copy()

                    st.caption(
                        "O shapefile não apresenta um sistema "
                        "de referência identificado. "
                        "Foram mantidas as coordenadas originais."
                    )

                # --------------------------------------------
                # CONSTRUÇÃO DO MAPA
                # --------------------------------------------

                fig, ax = plt.subplots(
                    figsize=(8, 7),
                    dpi=150
                )

                fig.patch.set_facecolor("#ffffff")
                ax.set_facecolor("#ffffff")

                nordeste_mapa.plot(
                    ax=ax,
                    facecolor="#a8dce8",
                    edgecolor="#12617a",
                    linewidth=1.1
                )

                ax.set_title(
                    "Região Nordeste do Brasil",
                    fontsize=15,
                    fontweight="bold",
                    color="#125f78",
                    pad=15
                )

                ax.set_aspect("equal")
                ax.set_axis_off()

                ax.margins(0.08)

                fig.tight_layout()

                coluna1, coluna2, coluna3 = st.columns(
                    [1, 2.5, 1]
                )

                with coluna2:

                    st.pyplot(
                        fig,
                        use_container_width=True
                    )

                plt.close(fig)

                st.caption(
                    "Figura 1 – Delimitação espacial da "
                    "região Nordeste do Brasil. "
                    "Fonte: arquivo geográfico nordeste.shp."
                )

        except Exception as erro:

            st.error(
                f"Não foi possível carregar o mapa: {erro}"
            )

    st.divider()

    # ========================================================
    # 2. BASE DE DADOS
    # ========================================================

    st.subheader("2. Base de dados")

    texto("""
    Foram utilizados dados mensais de precipitação
    e evapotranspiração referentes ao período de
    2000 a 2024, obtidos por meio do Google Earth
    Engine (GEE) e organizados em planilhas.
    """)

    # ========================================================
    # 2.1. PRECIPITAÇÃO
    # ========================================================

    st.subheader("2.1. Precipitação")

    texto("""
    A precipitação corresponde à quantidade de água
    que atinge a superfície terrestre. O acumulado
    é determinado pela soma dos registros de cada
    intervalo temporal, expressos em milímetros.
    """)

    st.latex(
        r"P_{acum} = \sum_{i=1}^{n} P_i"
    )

    texto("""
    Em que P_acum representa a precipitação acumulada,
    P_i corresponde à precipitação em cada intervalo
    e n ao número de registros considerados.
    """)

    # ========================================================
    # 2.2. EVAPOTRANSPIRAÇÃO
    # ========================================================

    st.subheader("2.2. Evapotranspiração")

    texto("""
    A evapotranspiração representa a transferência
    de água para a atmosfera por meio da evaporação
    da superfície e da transpiração vegetal.
    """)

    st.latex(
        r"ET = E + T"
    )

    texto("""
    Em que ET é a evapotranspiração, E corresponde
    à evaporação e T representa a transpiração
    vegetal, em unidades temporais compatíveis.
    """)

    # ========================================================
    # 2.3. TRANSPIRAÇÃO VEGETAL
    # ========================================================

    st.subheader("2.3. Transpiração vegetal")

    texto("""
    A transpiração corresponde à liberação de
    vapor de água pelas plantas, principalmente
    através dos estômatos, sendo influenciada
    pelas condições ambientais e hídricas.
    """)

    st.latex(
        r"T = ET - E"
    )

    texto("""
    A expressão representa a transpiração como
    componente residual, quando evaporação e
    evapotranspiração são conhecidas e compatíveis.
    """)

    # ========================================================
    # 2.4. EVAPOTRANSPIRAÇÃO DE REFERÊNCIA
    # ========================================================

    st.subheader("2.4. Evapotranspiração de referência")

    texto("""
    A evapotranspiração de referência (ET₀) pode
    ser estimada pelo método de Penman-Monteith
    FAO-56, que integra variáveis meteorológicas
    e condições de transferência de energia e vapor.
    """)

    st.latex(
        r"ET_0 = "
        r"\frac{0.408\Delta(R_n-G)"
        r"+\gamma\frac{900}{T_a+273}u_2(e_s-e_a)}"
        r"{\Delta+\gamma(1+0.34u_2)}"
    )

    texto("""
    Em que Rn é o saldo de radiação, G o fluxo
    de calor no solo, Ta a temperatura do ar,
    u₂ a velocidade do vento e os demais termos
    representam parâmetros psicrométricos e de vapor.
    """)

    st.caption(
        "A equação FAO-56 é apresentada como referência "
        "teórica e não corresponde necessariamente "
        "ao método do produto utilizado no GEE."
    )

    st.divider()

    # ========================================================
    # 3. SENSORIAMENTO REMOTO
    # ========================================================

    st.subheader("3. Sensoriamento remoto")

    texto("""
    O sensoriamento remoto permite obter informações
    da superfície terrestre a partir de sensores
    orbitais, contribuindo para o monitoramento
    de variáveis ambientais e hidroclimáticas.
    """)

    # ========================================================
    # 4. GOOGLE EARTH ENGINE
    # ========================================================

    st.subheader("4. Google Earth Engine")

    texto("""
    O Google Earth Engine foi utilizado como
    plataforma de acesso e processamento das
    informações geoespaciais, permitindo
    trabalhar com dados de sensoriamento remoto.
    """)

    # ========================================================
    # 5. PYTHON
    # ========================================================

    st.subheader("5. Linguagem Python")

    texto("""
    A linguagem Python foi utilizada na organização,
    processamento e análise dos dados, por meio
    de bibliotecas científicas como Pandas,
    NumPy e Plotly.
    """)

    # ========================================================
    # 6. STREAMLIT
    # ========================================================

    st.subheader("6. Framework Streamlit")

    texto("""
    O Streamlit foi empregado para desenvolver
    a interface web da aplicação, integrando
    estatísticas, gráficos, séries temporais,
    projeções e visualizações cartográficas.
    """)

    # ========================================================
    # 7. ANÁLISE DESCRITIVA
    # ========================================================

    st.subheader("7. Análise estatística descritiva")

    texto("""
    Foram implementadas medidas de tendência
    central e dispersão, incluindo média, mediana,
    desvio padrão, quartis e coeficiente de variação,
    além de histogramas e boxplots.
    """)

    st.latex(
        r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i"
    )

    st.latex(
        r"CV = \frac{s}{|\bar{x}|}\times 100"
    )

    # ========================================================
    # 8. SÉRIES TEMPORAIS
    # ========================================================

    st.subheader("8. Análise de séries temporais")

    texto("""
    As séries temporais foram analisadas por meio
    de registros mensais e totais anuais, médias
    móveis, anomalias e mapas de calor, permitindo
    investigar padrões sazonais e interanuais.
    """)

    st.latex(
        r"MM_t = \frac{1}{k}\sum_{i=0}^{k-1}X_{t-i}"
    )

    # ========================================================
    # 9. PROJEÇÕES ESTATÍSTICAS
    # ========================================================

    st.subheader("9. Projeções estatísticas")

    texto("""
    Foram implementadas projeções exploratórias
    até 2028, combinando uma tendência linear
    histórica com um componente sazonal mensal,
    sem incorporar variáveis meteorológicas futuras.
    """)

    st.latex(
        r"\hat{X}_{y,m} = "
        r"\alpha + \beta(y-\bar{y}) + S_m"
    )

    st.caption(
        "As projeções não constituem previsões "
        "meteorológicas operacionais."
    )

    # ========================================================
    # 10. ANÁLISE ESPACIAL
    # ========================================================

    st.subheader("10. Análise espacial")

    texto("""
    A análise espacial foi realizada por meio
    de mapas temáticos previamente elaborados,
    organizados por variável e periodicidade,
    possibilitando visualizar a distribuição
    geográfica dos dados no Nordeste.
    """)

    # ========================================================
    # 11. FLUXO METODOLÓGICO
    # ========================================================

    st.subheader("11. Fluxo metodológico")

    texto("""
    O processamento compreendeu a aquisição dos
    dados no Google Earth Engine, sua organização
    em planilhas e mapas, a análise em Python
    e a apresentação interativa no Streamlit.
    """)

    st.divider()

    st.caption(
        "HidroClima Nordeste | Materiais e Métodos"
    )


# ============================================================
# ABA 5 - DESCRITIVO
# ============================================================

with abas[4]:

    painel_descritivo()


# ============================================================
# ABA 6 - SÉRIES TEMPORAIS
# ============================================================

with abas[5]:

    painel_series()


# ============================================================
# ABA 7 - MAPAS
# ============================================================

with abas[6]:

    st.header("🗺️ Análise Espacial e Mapas")

    texto("""
    Esta seção permite visualizar mapas temáticos
    de precipitação e evapotranspiração do Nordeste
    brasileiro, considerando diferentes periodicidades.
    """)

    st.divider()

    visualizar_mapas()


# ============================================================
# ABA 8 - CONCLUSÃO
# ============================================================


# ============================================================
# ABA 8 - CONCLUSÃO
# ============================================================

with abas[7]:

    st.header("✅ Conclusão")

    # ========================================================
    # 1. CONSIDERAÇÕES GERAIS
    # ========================================================

    st.subheader("1. Considerações gerais")

    texto("""
    O desenvolvimento da plataforma HidroClima Nordeste
    possibilitou a integração de informações de precipitação
    e evapotranspiração em um ambiente computacional
    interativo, organizado e acessível. A utilização
    da linguagem Python e do framework Streamlit
    permitiu reunir procedimentos estatísticos,
    análises temporais e visualizações cartográficas
    em uma única aplicação.

    A estrutura desenvolvida contribui para a
    organização e exploração de informações
    hidroclimáticas do Nordeste brasileiro,
    considerando o período de 2000 a 2024.
    A integração dessas informações oferece
    recursos para investigar a variabilidade
    das condições hídricas regionais em
    diferentes escalas temporais e espaciais.
    """)

    st.divider()

    # ========================================================
    # 2. CONTRIBUIÇÕES DA APLICAÇÃO
    # ========================================================

    st.subheader("2. Contribuições da aplicação")

    texto("""
    A plataforma disponibiliza ferramentas de
    análise estatística descritiva, permitindo
    caracterizar a distribuição e a dispersão
    dos registros de precipitação e evapotranspiração.
    A apresentação de indicadores, histogramas,
    diagramas de caixa e medidas estatísticas
    facilita a interpretação das características
    dos dados hidroclimáticos.

    As funcionalidades de séries temporais
    possibilitam explorar o comportamento
    mensal e anual das variáveis, incluindo
    médias móveis, anomalias, sazonalidade
    e tendências lineares. A utilização
    de mapas de calor temporais também
    contribui para a identificação visual
    de padrões e contrastes entre os
    diferentes períodos analisados.

    A integração de mapas temáticos complementa
    essas análises, permitindo visualizar
    a distribuição espacial da precipitação
    e da evapotranspiração no Nordeste brasileiro,
    com diferentes opções de periodicidade.
    """)

    st.divider()

    # ========================================================
    # 3. PROJEÇÕES E LIMITAÇÕES
    # ========================================================

    st.subheader("3. Projeções e limitações")

    texto("""
    A implementação de projeções estatísticas
    exploratórias até 2028 amplia as possibilidades
    de investigação temporal da plataforma,
    permitindo visualizar extrapolações construídas
    a partir de tendências históricas e componentes
    sazonais das séries observadas.

    Entretanto, essas projeções apresentam
    limitações metodológicas, pois não incorporam
    diretamente informações meteorológicas futuras,
    fenômenos de variabilidade climática ou
    cenários de mudanças ambientais. Dessa forma,
    os valores projetados devem ser interpretados
    como estimativas exploratórias, não como
    previsões meteorológicas definitivas.

    A interpretação científica dos resultados
    também depende das características dos
    produtos geoespaciais utilizados, de suas
    resoluções, da qualidade dos registros
    e dos procedimentos de processamento.
    """)

    st.divider()

    # ========================================================
    # 4. PERSPECTIVAS FUTURAS
    # ========================================================

    st.subheader("4. Perspectivas futuras")

    texto("""
    Como perspectivas de aprimoramento, destaca-se
    a possibilidade de incorporar novas bases
    hidroclimáticas, ampliar a cobertura temporal
    dos dados e implementar procedimentos adicionais
    de análise estatística e modelagem preditiva.

    A aplicação também poderá ser aperfeiçoada
    mediante a inclusão de análises por estado,
    município ou bacia hidrográfica, permitindo
    avaliações espaciais em escalas mais detalhadas.

    A validação das projeções com dados independentes
    e a comparação entre diferentes modelos
    estatísticos constituem possibilidades
    relevantes para o desenvolvimento futuro
    da plataforma.
    """)

    st.divider()

    # ========================================================
    # 5. CONSIDERAÇÕES FINAIS
    # ========================================================

    st.subheader("5. Considerações finais")

    texto("""
    Conclui-se que o HidroClima Nordeste constitui
    uma ferramenta computacional de apoio à análise
    e visualização de informações de precipitação
    e evapotranspiração, integrando recursos
    estatísticos, temporais e cartográficos
    em uma interface interativa.

    A aplicação apresenta potencial para auxiliar
    atividades de ensino, pesquisa e monitoramento
    ambiental, contribuindo para a organização,
    exploração e comunicação de informações
    relacionadas à dinâmica hidroclimática
    do Nordeste brasileiro.
    """)

    st.divider()

    st.caption(
        "HidroClima Nordeste | Conclusões e "
        "perspectivas da aplicação científica."
    )
