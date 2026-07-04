"""
Casa&Obra — Painel de Vendas
Folha de estilo injetada no Streamlit.

Conceito visual ("Circuito"):
Um painel escuro, tecnológico e direto — cartões flutuantes com uma borda de
acento em gradiente laranja→lima (as cores da marca), leve brilho no hover,
tipografia forte para números (mono) e uma grade sutil de fundo lembrando um
circuito/planta técnica, sem nunca comprometer a legibilidade do texto.
"""

from utils import COLORS, FONT_DISPLAY, FONT_BODY, FONT_MONO


def get_css() -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Work+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600;700&display=swap');

html, body, [class*="css"] {{
    font-family: {FONT_BODY};
    color: {COLORS['text']};
}}

/* Fundo geral: navy profundo com brilho radial sutil das cores da marca */
.stApp {{
    background-color: {COLORS['navy']};
    background-image:
        radial-gradient(ellipse 900px 500px at 12% -10%, rgba(232,117,46,0.14), transparent 60%),
        radial-gradient(ellipse 700px 500px at 100% 0%, rgba(228,242,34,0.08), transparent 55%);
}}

/* Régua de acento — divisor de seção assinatura do painel */
.ruler-divider {{
    height: 4px;
    width: 100%;
    margin: 0 0 22px 0;
    border-radius: 3px;
    background: linear-gradient(90deg,
        {COLORS['orange']} 0%, {COLORS['orange']} 30%,
        {COLORS['lime']} 55%, {COLORS['slate_light']} 100%);
    box-shadow: 0 0 16px rgba(232,117,46,0.35);
}}

/* Cabeçalho de página */
.page-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}}
.page-title {{
    font-family: {FONT_DISPLAY};
    font-size: 30px;
    color: {COLORS['text']};
    letter-spacing: 0.5px;
    margin: 0;
}}
.page-subtitle {{
    font-family: {FONT_BODY};
    font-size: 14px;
    color: {COLORS['muted']};
    margin-top: 2px;
}}

/* ---------------------------------------------------------------------- */
/* CARTÕES DE INDICADOR (KPI)                                             */
/* ---------------------------------------------------------------------- */
.kpi-card {{
    position: relative;
    background: linear-gradient(180deg, {COLORS['surface_alt']} 0%, {COLORS['surface']} 100%);
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
    padding: 20px 22px 18px 22px;
    height: 100%;
    overflow: hidden;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}}
.kpi-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {COLORS['orange']}, {COLORS['lime']});
}}
.kpi-card:hover {{
    transform: translateY(-2px);
    border-color: rgba(232,117,46,0.45);
    box-shadow: 0 10px 28px rgba(0,0,0,0.35), 0 0 0 1px rgba(232,117,46,0.12);
}}

.kpi-label {{
    font-family: {FONT_BODY};
    font-weight: 600;
    font-size: 11.5px;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: {COLORS['muted']};
    margin-bottom: 8px;
}}
.kpi-value {{
    font-family: {FONT_MONO};
    font-weight: 700;
    font-size: 25px;
    color: {COLORS['text']};
    line-height: 1.15;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.kpi-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
    flex-wrap: wrap;
}}
.kpi-delta {{
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-family: {FONT_MONO};
    font-size: 11.5px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 999px;
}}
.kpi-delta-up {{ color: {COLORS['success']}; background: rgba(62,213,152,0.14); }}
.kpi-delta-down {{ color: {COLORS['danger']}; background: rgba(255,92,122,0.14); }}
.kpi-note {{ color: {COLORS['muted']}; font-size: 12px; margin-top: 2px; }}

/* ---------------------------------------------------------------------- */
/* CARTÃO DE GRÁFICO / TABELA                                              */
/* ---------------------------------------------------------------------- */
.chart-card {{
    position: relative;
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
    padding: 16px 18px 6px 18px;
    margin-bottom: 18px;
}}
.chart-card-title {{
    font-family: {FONT_BODY};
    font-weight: 700;
    font-size: 12.5px;
    color: {COLORS['text']};
    letter-spacing: 0.6px;
    margin-bottom: 6px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
}}
.chart-card-title::before {{
    content: "";
    width: 7px; height: 7px;
    border-radius: 2px;
    background: {COLORS['orange']};
    display: inline-block;
    box-shadow: 0 0 8px rgba(232,117,46,0.6);
}}

/* ---------------------------------------------------------------------- */
/* PÁGINA INICIAL — saudação e destaque                                   */
/* ---------------------------------------------------------------------- */
.hero-card {{
    position: relative;
    background:
        radial-gradient(ellipse 500px 260px at 100% 0%, rgba(228,242,34,0.10), transparent 60%),
        linear-gradient(135deg, {COLORS['surface_alt']} 0%, {COLORS['surface']} 100%);
    border: 1px solid {COLORS['border']};
    border-radius: 18px;
    padding: 28px 30px;
    margin-bottom: 22px;
    overflow: hidden;
}}
.hero-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, {COLORS['orange']}, {COLORS['lime']}, {COLORS['slate_light']});
}}
.hero-greeting {{
    font-family: {FONT_DISPLAY};
    font-size: 32px;
    color: {COLORS['text']};
    margin: 0;
}}
.hero-date {{
    font-family: {FONT_MONO};
    font-size: 13px;
    color: {COLORS['muted']};
    margin-top: 4px;
}}
.hero-tag {{
    display: inline-block;
    font-family: {FONT_BODY};
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: {COLORS['navy']};
    background: linear-gradient(90deg, {COLORS['orange']}, {COLORS['lime']});
    padding: 4px 12px;
    border-radius: 999px;
    margin-bottom: 10px;
}}

.highlight-card {{
    position: relative;
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
    padding: 16px 18px;
    height: 100%;
}}
.highlight-kicker {{
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    color: {COLORS['muted']};
    margin-bottom: 6px;
}}
.highlight-title {{
    font-family: {FONT_DISPLAY};
    font-size: 18px;
    color: {COLORS['text']};
    margin: 0 0 2px 0;
}}
.highlight-sub {{
    font-family: {FONT_MONO};
    font-size: 13px;
    color: {COLORS['lime']};
}}

/* Botões — navegação (topo das páginas) e ações em geral */
.stButton>button, .stDownloadButton>button {{
    border-radius: 8px;
    font-weight: 600;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}}

/* Botão "primary" = página ativa na navegação */
[data-testid="stBaseButton-primary"] {{
    background: linear-gradient(90deg, {COLORS['orange']}, {COLORS['orange_dark']}) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 0 14px rgba(232,117,46,0.35);
}}

/* Botão "secondary" = demais páginas / ações neutras */
[data-testid="stBaseButton-secondary"] {{
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid {COLORS['border']} !important;
    color: {COLORS['muted']} !important;
}}
[data-testid="stBaseButton-secondary"]:hover {{
    background: rgba(232,117,46,0.16) !important;
    border-color: {COLORS['orange']} !important;
    color: {COLORS['text']} !important;
}}

.stDownloadButton>button {{
    background: linear-gradient(90deg, {COLORS['orange']}, {COLORS['orange_dark']});
    color: white;
    border: none;
}}
.stDownloadButton>button:hover {{
    background: {COLORS['lime']};
    color: {COLORS['navy']};
}}

/* Contêiner com borda (usado na barra de filtros de cada página) */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    border-color: {COLORS['border']} !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,0.02);
}}

footer {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}

/* Marca d'água */
.watermark {{
    position: fixed;
    bottom: 14px;
    right: 18px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    color: {COLORS['muted']};
    opacity: 0.5;
    z-index: 9999;
    pointer-events: none;
    user-select: none;
}}
</style>
"""
