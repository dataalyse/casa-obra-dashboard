"""
Casa&Obra — Painel de Vendas
Folha de estilo injetada no Streamlit.

Conceito visual ("Planta Baixa"):
Uma loja de material de construção pensa em plantas técnicas, réguas e
medidas. O painel usa cartões com "cantos de projeto" (marcas em L, como em
desenhos técnicos), uma régua de três cores como divisor de seção e uma grade
pontilhada muito sutil de fundo — sem apelar para clichês literais (tijolo,
capacete) fora da tela de abertura.
"""

from utils import COLORS, FONT_DISPLAY, FONT_BODY, FONT_MONO


def get_css() -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo+Black&family=Work+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');

html, body, [class*="css"] {{
    font-family: {FONT_BODY};
    color: {COLORS['text']};
}}

/* Fundo geral: cor de concreto com grade de projeto muito sutil */
.stApp {{
    background-color: {COLORS['concrete']};
    background-image:
        linear-gradient(rgba(34,49,74,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34,49,74,0.035) 1px, transparent 1px);
    background-size: 34px 34px;
}}

section[data-testid="stSidebar"] {{
    background-color: {COLORS['navy']};
    border-right: 3px solid {COLORS['orange']};
}}
section[data-testid="stSidebar"] * {{
    color: #EDEFF4 !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.15);
}}

/* Régua de três cores — divisor de seção assinatura do painel */
.ruler-divider {{
    height: 6px;
    width: 100%;
    margin: 0 0 22px 0;
    border-radius: 3px;
    background: repeating-linear-gradient(
        90deg,
        {COLORS['orange']} 0px, {COLORS['orange']} 22px,
        {COLORS['navy']} 22px, {COLORS['navy']} 34px,
        {COLORS['lime']} 34px, {COLORS['lime']} 40px,
        {COLORS['navy']} 40px, {COLORS['navy']} 52px
    );
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
    color: {COLORS['navy']};
    letter-spacing: 0.5px;
    margin: 0;
}}
.page-subtitle {{
    font-family: {FONT_BODY};
    font-size: 14px;
    color: {COLORS['muted']};
    margin-top: 2px;
}}

/* Cartões de indicador com "cantos de projeto" (marcas em L) */
.kpi-card {{
    position: relative;
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 18px 20px 16px 20px;
    height: 100%;
}}
.kpi-card::before, .kpi-card::after,
.kpi-card .corner-br, .kpi-card .corner-bl {{
    content: "";
    position: absolute;
    width: 14px;
    height: 14px;
    border-color: {COLORS['orange']};
    border-style: solid;
    border-width: 0;
}}
.kpi-card::before {{ top: -1px; left: -1px; border-top-width: 3px; border-left-width: 3px; }}
.kpi-card::after {{ bottom: -1px; right: -1px; border-bottom-width: 3px; border-right-width: 3px; }}

.kpi-label {{
    font-family: {FONT_BODY};
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    color: {COLORS['muted']};
    margin-bottom: 6px;
}}
.kpi-value {{
    font-family: {FONT_MONO};
    font-weight: 600;
    font-size: 26px;
    color: {COLORS['navy']};
    line-height: 1.1;
}}
.kpi-delta-up {{ color: {COLORS['success']}; font-size: 12px; font-weight: 600; }}
.kpi-delta-down {{ color: {COLORS['danger']}; font-size: 12px; font-weight: 600; }}
.kpi-note {{ color: {COLORS['muted']}; font-size: 12px; margin-top: 2px; }}

/* Cartão neutro para envolver gráficos/tabelas */
.chart-card {{
    background: {COLORS['card']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 14px 16px 6px 16px;
    margin-bottom: 18px;
}}
.chart-card-title {{
    font-family: {FONT_DISPLAY};
    font-size: 14px;
    color: {COLORS['navy']};
    letter-spacing: 0.3px;
    margin-bottom: 4px;
    text-transform: uppercase;
}}

/* Navegação lateral estilo "menu do painel" */
.nav-badge {{
    font-family: {FONT_DISPLAY};
    color: {COLORS['orange']};
    font-size: 20px;
}}
.nav-item-label {{
    font-family: {FONT_BODY};
    font-weight: 600;
}}

div[data-testid="stSidebar"] .stRadio > label {{
    display: none;
}}
div[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {{
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 4px;
    padding: 10px 12px;
    margin-bottom: 8px;
    width: 100%;
    transition: background 0.15s ease, border-color 0.15s ease;
}}
div[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {{
    background: rgba(232,117,46,0.18);
    border-color: {COLORS['orange']};
}}

/* Botões */
.stButton>button, .stDownloadButton>button {{
    background-color: {COLORS['orange']};
    color: white;
    border: none;
    border-radius: 4px;
    font-weight: 600;
}}
.stButton>button:hover, .stDownloadButton>button:hover {{
    background-color: {COLORS['navy']};
    color: {COLORS['lime']};
}}

footer {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
</style>
"""
