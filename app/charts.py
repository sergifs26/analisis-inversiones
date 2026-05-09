import plotly.graph_objects as go
from engine.models import AnalysisResult
from engine.calculator import get_value, EBIT_KEYS


def revenue_chart(result: AnalysisResult) -> go.Figure:
    years  = [str(d.year) for d in result.years]
    values = [get_value(result.income, ["Total Revenue", "TotalRevenue"], d)
              for d in result.years]
    fig = go.Figure()
    fig.add_bar(x=years, y=values, marker_color="#2563EB", name="Revenue")
    fig.update_layout(
        title="Revenue histórico",
        xaxis_title="Año",
        yaxis_title=f"({result.currency})",
        plot_bgcolor="white",
        height=350,
    )
    return fig


def margins_chart(result: AnalysisResult) -> go.Figure:
    years = [str(d.year) for d in result.years]
    ebit_margins, net_margins = [], []
    for d in result.years:
        rev  = get_value(result.income, ["Total Revenue", "TotalRevenue"], d)
        ebit = get_value(result.income, EBIT_KEYS, d)
        ni   = get_value(result.income, ["Net Income", "NetIncome"], d)
        ebit_margins.append(round(ebit / rev * 100, 1) if rev and ebit else None)
        net_margins.append(round(ni / rev * 100, 1)   if rev and ni   else None)

    fig = go.Figure()
    fig.add_scatter(x=years, y=ebit_margins, mode="lines+markers",
                    name="Margen EBIT %", line=dict(color="#2563EB", width=2))
    fig.add_scatter(x=years, y=net_margins, mode="lines+markers",
                    name="Margen Neto %", line=dict(color="#16A34A", width=2))
    fig.update_layout(
        title="Márgenes históricos",
        xaxis_title="Año",
        yaxis_title="%",
        plot_bgcolor="white",
        height=350,
    )
    return fig


def scenarios_chart(result: AnalysisResult) -> go.Figure:
    s = result.scenarios
    price = result.assumptions.price
    categories = ["Precio actual", "Bear 3Y", "Mid 3Y", "Bull 3Y",
                  "Bear 5Y", "Mid 5Y", "Bull 5Y"]
    values = [price, s.bear_3y, s.mid_3y, s.bull_3y,
              s.bear_5y, s.mid_5y, s.bull_5y]
    colors = ["#6B7280", "#DC2626", "#2563EB", "#16A34A",
              "#DC2626", "#2563EB", "#16A34A"]
    fig = go.Figure()
    fig.add_bar(x=categories, y=values, marker_color=colors)
    fig.update_layout(
        title="Escenarios de precio (3Y / 5Y)",
        yaxis_title=result.currency,
        plot_bgcolor="white",
        height=350,
    )
    return fig


def multiples_table(result: AnalysisResult) -> go.Figure:
    m = result.multiples
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["Múltiplo", "Mediana histórica"],
            fill_color="#2563EB",
            font=dict(color="white", size=13),
            align="left",
        ),
        cells=dict(
            values=[
                ["PER", "P/FCF", "EV/EBITDA", "EV/EBIT"],
                [
                    f"{m.per}x"       if m.per       else "N/D",
                    f"{m.pfcf}x"      if m.pfcf      else "N/D",
                    f"{m.ev_ebitda}x" if m.ev_ebitda else "N/D",
                    f"{m.ev_ebit}x"   if m.ev_ebit   else "N/D",
                ],
            ],
            fill_color="white",
            align="left",
            font=dict(size=13),
            height=30,
        ),
    )])
    fig.update_layout(height=220, margin=dict(l=0, r=0, t=0, b=0))
    return fig
