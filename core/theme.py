"""
Identidade visual Casa&Obra (escopo, seção 1): tokens de cor, CSS global,
tema dos gráficos Plotly, formatadores pt-BR e ícones lucide inline.
"""

from __future__ import annotations

import math

import pandas as pd

# ----------------------------------------------------------------------------
# PALETA
# ----------------------------------------------------------------------------
ORANGE = "#F07335"
YELLOW = "#F0FA28"
BLUE = "#1F4E79"
BG = "#0A1626"
SURFACE = "#10233A"
SURFACE2 = "#163150"
BORDER = "rgba(255,255,255,0.08)"
TEXT = "#EAF0F7"
MUTED = "#8FA3BA"
GRID = "rgba(255,255,255,0.06)"
POS = "#2ECC8F"
WARN = YELLOW
CRIT = "#FF4D5E"
INFO = "#4FA3E0"

SEQ = [ORANGE, YELLOW, INFO, POS, "#B07CFF", "#FF8FB1", "#7F93AA"]
SCALE = [[0, SURFACE], [0.33, BLUE], [0.66, ORANGE], [1, YELLOW]]

LOJA_COR = {"Centro": ORANGE, "Barra Mansa": INFO, "Resende": POS}
SIT_COR = {"Normal": POS, "Abaixo do mínimo": WARN, "Ruptura": CRIT, "Excesso": INFO}

FONT_TITLE = "'Space Grotesk', 'Inter', sans-serif"
FONT_BODY = "'Inter', 'Segoe UI', sans-serif"


def rgba(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{a})"


# ----------------------------------------------------------------------------
# FORMATADORES pt-BR
# ----------------------------------------------------------------------------
def _br(s: str) -> str:
    return s.replace(",", "#").replace(".", ",").replace("#", ".")


def _ok(v) -> bool:
    return v is not None and not (isinstance(v, float) and (math.isnan(v) or math.isinf(v))) and not pd.isna(v)


def moeda(v, casas: int = 2) -> str:
    if not _ok(v):
        return "—"
    return ("-" if v < 0 else "") + "R$ " + _br(f"{abs(v):,.{casas}f}")


def moeda_curta(v) -> str:
    """R$ 2,91 mi · R$ 458 mil · R$ 812"""
    if not _ok(v):
        return "—"
    s = "-" if v < 0 else ""
    a = abs(v)
    if a >= 1e6:
        return f"{s}R$ {_br(f'{a / 1e6:,.2f}')} mi"
    if a >= 1e3:
        return f"{s}R$ {_br(f'{a / 1e3:,.0f}')} mil"
    return f"{s}R$ {_br(f'{a:,.0f}')}"


def num(v, casas: int = 0) -> str:
    if not _ok(v):
        return "—"
    return _br(f"{v:,.{casas}f}")


def pct(v, casas: int = 1, sinal: bool = False) -> str:
    """Recebe fração (0,287) e devolve '28,7%'."""
    if not _ok(v):
        return "—"
    s = f"{v * 100:+,.{casas}f}%" if sinal else f"{v * 100:,.{casas}f}%"
    return _br(s)


def data_br(d) -> str:
    if d is None or pd.isna(d):
        return "—"
    return pd.Timestamp(d).strftime("%d/%m/%Y")


MES_ABREV = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
DIA_ABREV = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def mes_ano(d) -> str:
    d = pd.Timestamp(d)
    return f"{MES_ABREV[d.month - 1]}/{d.year}"


def mes_ano_curto(d) -> str:
    d = pd.Timestamp(d)
    return f"{MES_ABREV[d.month - 1]}/{str(d.year)[2:]}"


# ----------------------------------------------------------------------------
# ÍCONES (lucide, inline SVG)
# ----------------------------------------------------------------------------
_ICONS = {
    "dollar": '<line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "trending": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "trending-down": '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
    "percent": '<line x1="19" x2="5" y1="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
    "cart": '<circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/>',
    "receipt": '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 17.5v-11"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "package": '<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "x-circle": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "refresh": '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "wallet": '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "user-plus": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/>',
    "user-x": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="17" x2="22" y1="8" y2="13"/><line x1="22" x2="17" y1="8" y2="13"/>',
    "repeat": '<path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/>',
    "smile": '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" x2="9.01" y1="9" y2="9"/><line x1="15" x2="15.01" y1="9" y2="9"/>',
    "tag": '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r=".5"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "banknote": '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "activity": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "home": '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    "dashboard": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "boxes": '<path d="M2.97 12.92A2 2 0 0 0 2 14.63v3.24a2 2 0 0 0 .97 1.71l3 1.8a2 2 0 0 0 2.06 0L12 19v-5.5l-5-3-4.03 2.42Z"/><path d="m7 16.5-4.74-2.85"/><path d="m7 16.5 5-3"/><path d="M7 16.5v5.17"/><path d="M12 13.5V19l3.97 2.38a2 2 0 0 0 2.06 0l3-1.8a2 2 0 0 0 .97-1.71v-3.24a2 2 0 0 0-.97-1.71L17 10.5l-5 3Z"/><path d="m17 16.5-5-3"/><path d="m17 16.5 4.74-2.85"/><path d="M17 16.5v5.17"/><path d="M7.97 4.42A2 2 0 0 0 7 6.13v4.37l5 3 5-3V6.13a2 2 0 0 0-.97-1.71l-3-1.8a2 2 0 0 0-2.06 0l-3 1.8Z"/><path d="M12 8 7.26 5.15"/><path d="m12 8 4.74-2.85"/><path d="M12 13.5V8"/>',
    "sparkles": '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/>',
    "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "inbox": '<polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
}


def icon(name: str, size: int = 20, color: str = ORANGE, stroke: float = 2) -> str:
    body = _ICONS.get(name, _ICONS["activity"])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</svg>'
    )


# ----------------------------------------------------------------------------
# TEMA PLOTLY
# ----------------------------------------------------------------------------
def style(fig, height: int = 340, legend: bool = True, margin: dict | None = None):
    fig.update_layout(
        height=height,
        margin=margin or dict(l=8, r=8, t=28, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        separators=",.",
        font=dict(family=FONT_BODY, color=TEXT, size=12),
        showlegend=legend,
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0,
            font=dict(size=11, color=MUTED), title_text="", bgcolor="rgba(0,0,0,0)",
        ),
        hoverlabel=dict(
            bgcolor=SURFACE2, bordercolor=ORANGE, font=dict(family=FONT_BODY, color=TEXT, size=12),
            align="left",
        ),
        transition=dict(duration=500, easing="cubic-out"),
        colorway=SEQ,
        bargap=0.28,
    )
    fig.update_xaxes(showgrid=False, linecolor=BORDER, zeroline=False, tickfont=dict(size=11, color=MUTED),
                     title_font=dict(size=11, color=MUTED))
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, tickfont=dict(size=11, color=MUTED),
                     title_font=dict(size=11, color=MUTED), linecolor=BORDER)
    return fig


PLOTLY_CONFIG = {
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d", "zoomIn2d", "zoomOut2d", "toggleSpikelines"],
    "toImageButtonOptions": {"format": "png", "scale": 2},
    "locale": "pt-BR",
}


# ----------------------------------------------------------------------------
# CSS GLOBAL
# ----------------------------------------------------------------------------
CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {{
  --brand-orange:{ORANGE}; --brand-yellow:{YELLOW}; --brand-blue:{BLUE};
  --bg:{BG}; --surface:{SURFACE}; --surface-2:{SURFACE2}; --border:{BORDER};
  --text:{TEXT}; --text-muted:{MUTED}; --positive:{POS}; --critical:{CRIT}; --info:{INFO};
}}
html, body, [class*="css"], .stApp {{ font-family:{FONT_BODY}; color:var(--text); }}
.stApp {{
  background-color:var(--bg);
  background-image: radial-gradient(ellipse 1100px 700px at 0% 0%, {rgba(BLUE, .20)}, transparent 65%);
  background-attachment: fixed;
}}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1880px; }}
footer, #MainMenu {{ visibility:hidden; }}
h1,h2,h3,h4 {{ font-family:{FONT_TITLE}; }}

/* ---------- Menu lateral ---------- */
[data-testid="stSidebar"] {{ background: {SURFACE}; border-right:1px solid var(--border); }}
[data-testid="stSidebarNav"] a {{ border-radius:10px; margin:2px 0; border-left:3px solid transparent; }}
[data-testid="stSidebarNav"] a[aria-current="page"] {{
  background: var(--surface-2); border-left:3px solid var(--brand-orange);
}}
[data-testid="stSidebarNav"] a span {{ color: var(--text) !important; font-weight:500; }}
[data-testid="stSidebarNav"] a[aria-current="page"] svg, [data-testid="stSidebarNav"] a[aria-current="page"] span[data-testid="stIconMaterial"] {{ color: var(--brand-orange) !important; }}

/* ---------- Cabeçalho ---------- */
.co-header {{ display:flex; align-items:center; gap:18px; flex-wrap:wrap; }}
.co-header img {{ height:34px; }}
.co-title {{ font-family:{FONT_TITLE}; font-weight:700; font-size:24px; margin:0; line-height:1.15; color:var(--text); }}
.co-sub {{ color:var(--text-muted); font-size:13px; margin:2px 0 0 0; }}
.co-badge {{ display:inline-flex; align-items:center; gap:6px; font-size:12px; color:var(--text-muted);
  border:1px solid var(--border); background:{rgba(SURFACE, .85)}; padding:6px 12px; border-radius:999px; white-space:nowrap; }}
.co-badge b {{ color:var(--text); font-weight:600; }}
.co-dot {{ width:7px; height:7px; border-radius:50%; background:var(--positive); box-shadow:0 0 8px var(--positive); }}

/* ---------- Cards (containers com key card_*) ---------- */
div[class*="st-key-card_"], div[class*="st-key-kpi_"], div[class*="st-key-filtros"] {{
  background:{rgba(SURFACE, .85)}; backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border:1px solid var(--border); border-radius:16px; padding:16px 18px 10px 18px;
  transition: box-shadow .2s ease, border-color .2s ease, transform .2s ease;
  animation: coFade .55s cubic-bezier(.22,.61,.36,1) both;
}}
div[class*="st-key-card_"]:hover, div[class*="st-key-kpi_"]:hover {{
  box-shadow: 0 0 0 1px {ORANGE}55, 0 8px 32px {ORANGE}22; border-color:{ORANGE}55;
}}
div[class*="st-key-filtros"] {{ padding:12px 16px 4px 16px; }}
@keyframes coFade {{ from {{ opacity:0; transform: translateY(12px); }} to {{ opacity:1; transform:none; }} }}

.card-title {{ font-family:{FONT_BODY}; font-size:13px; font-weight:600; letter-spacing:.08em;
  text-transform:uppercase; color:var(--text-muted); margin:0; }}
.card-sub {{ font-size:12px; color:{rgba(TEXT, .55)}; margin:2px 0 0 0; }}

/* ---------- KPI ---------- */
.kpi {{ position:relative; container-type:inline-size; }}
.kpi-top {{ display:flex; align-items:center; gap:8px; }}
.kpi-label {{ font-size:12px; font-weight:600; letter-spacing:.08em; text-transform:uppercase; color:var(--text-muted); flex:1; }}
.kpi-info {{ color:var(--text-muted); font-size:12px; cursor:help; border:1px solid var(--border); border-radius:50%;
  width:18px; height:18px; display:inline-flex; align-items:center; justify-content:center; }}
.kpi-value {{ font-family:{FONT_TITLE}; font-weight:700; font-size:clamp(16px, 14.5cqi, 36px); line-height:1.15; margin-top:6px;
  font-variant-numeric: tabular-nums; color:var(--text); white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
  animation: coCount .8s cubic-bezier(.22,.61,.36,1) both; }}
.kpi-value.hl {{ color: var(--brand-yellow); }}
.kpi-value.warn {{ color: var(--brand-yellow); }}
.kpi-value.crit {{ color: var(--critical); }}
@keyframes coCount {{ from {{ opacity:0; letter-spacing:.12em; filter: blur(4px); }} to {{ opacity:1; letter-spacing:0; filter:none; }} }}
.kpi-delta {{ font-size:12px; margin-top:2px; color:var(--text-muted); min-height:18px; }}
.kpi-delta .up {{ color:var(--positive); font-weight:600; }}
.kpi-delta .down {{ color:var(--critical); font-weight:600; }}
.kpi-spark {{ margin-top:6px; height:34px; }}

/* card inteiro clicável: link esticado sobre o container */
div[class*="st-key-kpi_"], div[class*="st-key-nav_"] {{ position:relative; }}
div[class*="st-key-kpi_"] [data-testid="stPageLink"], div[class*="st-key-nav_"] [data-testid="stPageLink"] {{
  position:absolute; inset:0; z-index:5; margin:0;
}}
div[class*="st-key-kpi_"] [data-testid="stElementContainer"]:has([data-testid="stPageLink"]),
div[class*="st-key-nav_"] [data-testid="stElementContainer"]:has([data-testid="stPageLink"]) {{
  position:static !important; height:0; margin:0;
}}
div[class*="st-key-kpi_"] [data-testid="stPageLink"] > div, div[class*="st-key-nav_"] [data-testid="stPageLink"] > div {{
  width:100%; height:100%;
}}
div[class*="st-key-kpi_"] [data-testid="stPageLink"] a, div[class*="st-key-nav_"] [data-testid="stPageLink"] a {{
  width:100%; height:100%; opacity:0; display:block; max-width:none;
}}

/* ---------- Chips de filtro ---------- */
div[class*="st-key-chip_"] button {{
  border-radius:999px !important; border:1px solid {ORANGE}66 !important; background:{rgba(ORANGE, .12)} !important;
  color:var(--text) !important; font-size:12px !important; padding:2px 12px !important; min-height:28px !important;
}}
div[class*="st-key-chip_"] button:hover {{ background:{rgba(ORANGE, .25)} !important; }}
div[class*="st-key-chip_cross"] button {{ border-color:{YELLOW}88 !important; background:{rgba(YELLOW, .10)} !important; }}

/* ---------- Widgets ---------- */
[data-testid="stBaseButton-primary"] {{ background:{ORANGE} !important; border:none !important; color:{BG} !important; font-weight:600; }}
[data-testid="stBaseButton-secondary"] {{ background:transparent !important; border:1px solid var(--border) !important; color:var(--text) !important; }}
[data-testid="stBaseButton-secondary"]:hover {{ border-color:{ORANGE} !important; color:{ORANGE} !important; }}
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div {{ background:{SURFACE2} !important; border-color:var(--border) !important; }}
span[data-baseweb="tag"] {{ background:{rgba(ORANGE, .2)} !important; }}
[data-testid="stWidgetLabel"] p {{ font-size:12px !important; color:var(--text-muted) !important; }}
[data-testid="stDataFrame"] {{ border-radius:10px; }}

/* ---------- Estado vazio ---------- */
.empty {{ display:flex; flex-direction:column; align-items:center; justify-content:center; gap:8px; padding:40px 0;
  color:var(--text-muted); font-size:13px; }}

/* ---------- Pílulas / tabelas HTML ---------- */
.pill {{ display:inline-block; padding:2px 9px; border-radius:999px; font-size:11.5px; font-weight:600; }}
.pill.pos {{ color:{POS}; background:{rgba(POS, .14)}; }}
.pill.warn {{ color:{YELLOW}; background:{rgba(YELLOW, .12)}; }}
.pill.crit {{ color:{CRIT}; background:{rgba(CRIT, .14)}; }}
.pill.info {{ color:{INFO}; background:{rgba(INFO, .14)}; }}

/* ---------- Alertas (Inteligência) ---------- */
.alert-card {{ display:flex; flex-direction:column; gap:6px; }}
.alert-num {{ font-family:{FONT_TITLE}; font-weight:700; font-size:30px; line-height:1.1; }}
.alert-txt {{ font-size:13px; color:var(--text-muted); min-height:38px; }}

/* ---------- Insights ---------- */
.insight {{ display:flex; gap:10px; align-items:flex-start; padding:10px 0; border-bottom:1px solid var(--border); font-size:14px; }}
.insight:last-child {{ border-bottom:none; }}
.insight b {{ color: var(--brand-yellow); font-weight:600; }}

/* ---------- Clientes em risco ---------- */
.risk {{ display:flex; align-items:center; gap:10px; padding:9px 0; border-bottom:1px solid var(--border); }}
.risk:last-child {{ border-bottom:none; }}
.risk-name {{ font-weight:600; font-size:13px; }}
.risk-meta {{ font-size:11.5px; color:var(--text-muted); }}
.risk-btn {{ margin-left:auto; display:inline-flex; gap:5px; align-items:center; font-size:12px; color:{ORANGE};
  border:1px solid {ORANGE}66; border-radius:999px; padding:3px 10px; white-space:nowrap; }}

/* ---------- Rodapé ---------- */
.co-footer {{ text-align:center; color:var(--text-muted); font-size:12px; opacity:.75; margin-top:28px; }}

/* ---------- Modo apresentação ---------- */
body.co-present [data-testid="stSidebar"], body.co-present [data-testid="stSidebarCollapsedControl"] {{ display:none; }}

@media (max-width: 1024px) {{ .kpi-value {{ font-size:26px; }} }}
</style>
"""
