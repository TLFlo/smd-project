"""Calculs de KPIs pour le dataset client unique."""

import numpy as np


def global_kpis(df) -> dict:
    n = len(df)
    if n == 0:
        return {"n_customers": 0, "total_ca": 0.0, "avg_ca": 0.0, "response_rate": 0.0}
    return {
        "n_customers": n,
        "total_ca": df["Total_Spent"].sum(),
        "avg_ca": df["Total_Spent"].mean(),
        "response_rate": df["Response"].mean() * 100,
    }


def fmt_k(value: float) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.1f} M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f} K"
    return f"{value:,.0f}"
