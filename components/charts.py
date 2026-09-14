"""Graphiques Plotly stylés uniformément (fonction style_chart partagée).

Les axes/légendes/infobulles utilisent automatiquement utils/labels.py
(DISPLAY_LABELS). Pour surcharger ponctuellement, passe un dict
`labels={"nom_colonne_reel": "Libelle Affiche"}` explicite à n'importe
laquelle de ces fonctions — il prendra le dessus sur le dictionnaire
central pour cet appel précis.
"""

import plotly.express as px
import plotly.graph_objects as go

from utils.labels import DISPLAY_LABELS

NAVY = "#16233F"
AMBER = "#C6862E"
SAGE = "#5B7F5E"
BRICK = "#A8452F"
MUTED = "#738096"
LINE = "#EDF0F4"

SEQUENTIAL = [NAVY, AMBER, SAGE, "#7A8CA6", "#D9B071", BRICK]


def _effective_labels(labels):
    """Fusionne les libellés centraux avec une éventuelle surcharge locale."""
    merged = dict(DISPLAY_LABELS)
    if labels:
        merged.update(labels)
    return merged


def style_chart(fig, show_legend: bool = False):
    """Fonction de style globale appliquée à tous les graphiques."""
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=NAVY,
        font_family="Inter, Segoe UI, Arial, sans-serif",
        margin=dict(l=6, r=6, t=6, b=6),
        showlegend=show_legend,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25),
        height=280,
    )
    fig.update_xaxes(showgrid=False, showline=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=LINE, showline=False, zeroline=False)
    return fig


def line_chart(df, x, y, color=None, labels=None):
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=SEQUENTIAL, labels=_effective_labels(labels))
    fig.update_traces(line=dict(width=3), fill="tozeroy", fillcolor="rgba(22,35,63,0.05)")
    return style_chart(fig, show_legend=bool(color))


def bar_chart(df, x, y, color=None, horizontal=False, labels=None):
    eff_labels = _effective_labels(labels)
    if horizontal:
        fig = px.bar(df, x=y, y=x, color=color, orientation="h", color_discrete_sequence=SEQUENTIAL, labels=eff_labels)
    else:
        fig = px.bar(df, x=x, y=y, color=color, color_discrete_sequence=SEQUENTIAL, labels=eff_labels)
    fig.update_traces(marker_line_width=0)
    return style_chart(fig, show_legend=bool(color))


def donut_chart(labels_values, values, name_map=None):
    """name_map : dict optionnel {"valeur_reelle": "Libelle Affiche"} appliqué aux labels du donut."""
    display_labels = [name_map.get(str(l), str(l)) for l in labels_values] if name_map else labels_values
    fig = go.Figure(data=[go.Pie(labels=display_labels, values=values, hole=0.55, marker=dict(colors=SEQUENTIAL))])
    return style_chart(fig, show_legend=True)


def scatter_chart(df, x, y, color=None, hover_data=None, labels=None):
    fig = px.scatter(df, x=x, y=y, color=color, hover_data=hover_data, color_discrete_sequence=SEQUENTIAL, labels=_effective_labels(labels))
    fig.update_traces(marker=dict(size=9, opacity=0.85, line=dict(width=0)))
    fig.update_layout(height=380)
    return style_chart(fig, show_legend=bool(color))
