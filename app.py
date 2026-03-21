import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.alert_engine import generate_alert
from utils.data_loader import get_region_names, get_region_record, load_region_data
from utils.recommendation_engine import calculate_resource_recommendations
from utils.risk_engine import calculate_flood_risk


st.set_page_config(
    page_title="Sentinel AI",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded",
)


THEMES = {
    "Dark": {
        "background_gradient": "linear-gradient(180deg, #001d31 0%, #003049 100%)",
        "surface": "#01263c",
        "surface_alt": "#0a3d5b",
        "sidebar": "linear-gradient(180deg, #00253c 0%, #003049 100%)",
        "text": "#ffffff",
        "muted_text": "#c7d6e2",
        "border": "#1f4f6b",
        "header_bg": "rgba(0, 48, 73, 0.96)",
        "button_bg": "#ffffff",
        "button_text": "#003049",
        "button_hover": "#dbe8f1",
        "metric_shadow": "0 14px 28px rgba(0, 17, 28, 0.28)",
        "chart_template": "plotly_dark",
        "chart_plot_bg": "#01263c",
        "chart_scale": ["#5d88a3", "#9fc3da", "#ffffff"],
        "gauge_low": "#24475d",
        "gauge_mid": "#4d7894",
        "gauge_high": "#90b7cf",
        "gauge_bar": "#ffffff",
        "alert_styles": {
            "error": {"background": "#e8f1f7", "text": "#003049"},
            "warning": {"background": "#0a3d5b", "text": "#ffffff"},
            "info": {"background": "#01263c", "text": "#ffffff"},
            "success": {"background": "#003049", "text": "#ffffff"},
        },
        "risk_styles": {
            "High Risk": {"background": "#ffffff", "text": "#003049"},
            "Medium Risk": {"background": "#7ba2bc", "text": "#00253c"},
            "Low Risk": {"background": "#0a3d5b", "text": "#ffffff"},
        },
        "table_header_bg": "#003049",
        "table_header_text": "#ffffff",
        "table_row_bg": "#01263c",
        "table_row_alt_bg": "#0a3049",
        "table_text": "#ffffff",
        "slider_track": "rgba(255, 255, 255, 0.28)",
        "slider_fill": "#ffffff",
        "slider_thumb": "#ffffff",
    },
    "Light": {
        "background_gradient": "linear-gradient(180deg, #ffffff 0%, #eef5f9 100%)",
        "surface": "#ffffff",
        "surface_alt": "#f5f9fc",
        "sidebar": "linear-gradient(180deg, #ffffff 0%, #eef5f9 100%)",
        "text": "#003049",
        "muted_text": "#49667a",
        "border": "#bdd0dd",
        "header_bg": "rgba(255, 255, 255, 0.97)",
        "button_bg": "#003049",
        "button_text": "#ffffff",
        "button_hover": "#0a3d5b",
        "metric_shadow": "0 12px 24px rgba(0, 48, 73, 0.08)",
        "chart_template": "simple_white",
        "chart_plot_bg": "#ffffff",
        "chart_scale": ["#d8e8f2", "#7ba2bc", "#003049"],
        "gauge_low": "#dfeaf1",
        "gauge_mid": "#93b6cc",
        "gauge_high": "#4d7894",
        "gauge_bar": "#003049",
        "alert_styles": {
            "error": {"background": "#003049", "text": "#ffffff"},
            "warning": {"background": "#eaf3f8", "text": "#003049"},
            "info": {"background": "#f5f9fc", "text": "#003049"},
            "success": {"background": "#ffffff", "text": "#003049"},
        },
        "risk_styles": {
            "High Risk": {"background": "#003049", "text": "#ffffff"},
            "Medium Risk": {"background": "#9fc3da", "text": "#003049"},
            "Low Risk": {"background": "#eaf3f8", "text": "#003049"},
        },
        "table_header_bg": "#003049",
        "table_header_text": "#ffffff",
        "table_row_bg": "#ffffff",
        "table_row_alt_bg": "#f6fafc",
        "table_text": "#003049",
        "slider_track": "#b9cedc",
        "slider_fill": "#003049",
        "slider_thumb": "#003049",
    },
}


@st.cache_data
def load_data_cached() -> pd.DataFrame:
    """Cache dataset loading so the app stays responsive."""
    return load_region_data()


def get_theme_colors(theme_mode: str) -> dict:
    """Return the active theme palette."""
    return THEMES.get(theme_mode, THEMES["Dark"])


def apply_custom_theme(colors: dict) -> None:
    """Inject CSS that adapts the app to the selected theme."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {colors["background_gradient"]};
            color: {colors["text"]};
        }}
        html, body, [class*="css"] {{
            font-family: "Trebuchet MS", Verdana, sans-serif;
            color: {colors["text"]};
        }}
        h1, h2, h3, h4, h5, h6, p, span, label, div {{
            color: inherit;
        }}
        h1, h2, h3, h4 {{
            color: {colors["text"]} !important;
            letter-spacing: -0.02em;
        }}
        @keyframes fadeUp {{
            from {{
                opacity: 0;
                transform: translateY(12px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        [data-testid="stAppViewContainer"] > .main {{
            padding-top: 0.75rem;
        }}
        [data-testid="stSidebar"] {{
            background: {colors["sidebar"]};
            border-right: 1px solid {colors["border"]};
        }}
        [data-testid="stSidebar"] * {{
            color: {colors["text"]};
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="base-input"] > div {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            color: {colors["text"]};
            border-radius: 14px;
        }}
        [data-testid="stSidebar"] div[data-baseweb="slider"] > div > div {{
            background: {colors["slider_track"]} !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="slider"] div[style*="background"] {{
            background: {colors["slider_fill"]} !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="slider"] [role="slider"] {{
            background: {colors["slider_thumb"]} !important;
            box-shadow: 0 0 0 2px {colors["slider_thumb"]} !important;
            border: none !important;
        }}
        [data-testid="stSidebar"] .stButton button,
        [data-testid="stPopover"] button {{
            background: {colors["button_bg"]};
            color: {colors["button_text"]};
            border: 1px solid {colors["border"]};
            border-radius: 14px;
            font-weight: 700;
            opacity: 1 !important;
            visibility: visible !important;
            transition: all 0.2s ease;
        }}
        [data-testid="stSidebar"] .stButton button:hover,
        [data-testid="stPopover"] button:hover {{
            background: {colors["button_hover"]};
            border-color: {colors["button_hover"]};
            transform: translateY(-1px);
        }}
        [data-testid="stSidebar"] .stButton button *,
        [data-testid="stSidebar"] .stButton button span,
        [data-testid="stSidebar"] .stButton button div,
        [data-testid="stPopover"] button *,
        [data-testid="stPopover"] button span,
        [data-testid="stPopover"] button div {{
            color: {colors["button_text"]} !important;
            fill: {colors["button_text"]} !important;
            opacity: 1 !important;
        }}
        [data-testid="stRadio"] label,
        [data-testid="stMarkdownContainer"],
        .stCaption,
        .stSubheader,
        .stText,
        .stMarkdown,
        .stSelectbox label,
        .stSlider label {{
            color: {colors["text"]} !important;
        }}
        div[data-testid="metric-container"] {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem 1rem;
            box-shadow: {colors["metric_shadow"]};
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            animation: fadeUp 0.45s ease;
        }}
        div[data-testid="metric-container"]:hover {{
            transform: translateY(-4px);
            box-shadow: 0 16px 30px rgba(0, 0, 0, 0.14);
        }}
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] div {{
            color: {colors["text"]} !important;
        }}
        .sticky-header {{
            position: sticky;
            top: 0;
            z-index: 999;
            background: {colors["header_bg"]};
            backdrop-filter: blur(12px);
            border-bottom: 1px solid {colors["border"]};
            padding: 0.9rem 1.4rem;
            margin-bottom: 1rem;
            border-radius: 0 0 18px 18px;
        }}
        .sticky-header-inner {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .brand-title {{
            font-size: 2rem;
            font-weight: 900;
            letter-spacing: -0.05em;
            color: {colors["text"]};
        }}
        .brand-subtitle {{
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: {colors["muted_text"]};
            font-weight: 700;
        }}
        .hero-box {{
            background: {colors["surface"]};
            padding: 1.35rem 1.5rem;
            border-radius: 22px;
            border: 1px solid {colors["border"]};
            margin-bottom: 1rem;
            box-shadow: {colors["metric_shadow"]};
            animation: fadeUp 0.5s ease;
        }}
        .intro-copy {{
            color: {colors["muted_text"]};
            margin: 0;
            font-size: 1.02rem;
        }}
        .risk-card {{
            padding: 1rem 1.2rem;
            border-radius: 16px;
            text-align: center;
            font-weight: 800;
            margin-top: 0.3rem;
            margin-bottom: 0.8rem;
            border: 1px solid {colors["border"]};
            animation: fadeUp 0.55s ease;
        }}
        .alert-box {{
            border-radius: 18px;
            padding: 1rem 1.15rem;
            border: 1px solid {colors["border"]};
            box-shadow: {colors["metric_shadow"]};
            animation: fadeUp 0.45s ease;
            margin-bottom: 0.5rem;
        }}
        .alert-title {{
            font-size: 1rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
        }}
        .panel-box {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 18px;
            padding: 1rem 1.1rem;
            box-shadow: {colors["metric_shadow"]};
            animation: fadeUp 0.55s ease;
        }}
        .table-shell {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 20px;
            padding: 0.5rem;
            overflow-x: auto;
            box-shadow: {colors["metric_shadow"]};
            animation: fadeUp 0.6s ease;
        }}
        .custom-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            color: {colors["table_text"]};
        }}
        .custom-table thead th {{
            background: {colors["table_header_bg"]};
            color: {colors["table_header_text"]};
            text-align: left;
            padding: 0.9rem 0.75rem;
            border-bottom: 1px solid {colors["border"]};
            font-weight: 700;
        }}
        .custom-table thead th:first-child {{
            border-top-left-radius: 14px;
        }}
        .custom-table thead th:last-child {{
            border-top-right-radius: 14px;
        }}
        .custom-table tbody tr:nth-child(odd) {{
            background: {colors["table_row_bg"]};
        }}
        .custom-table tbody tr:nth-child(even) {{
            background: {colors["table_row_alt_bg"]};
        }}
        .custom-table td {{
            padding: 0.85rem 0.75rem;
            border-bottom: 1px solid {colors["border"]};
            color: {colors["table_text"]};
        }}
        .custom-table tbody tr:last-child td {{
            border-bottom: none;
        }}
        [data-testid="stPopover"] {{
            z-index: 20;
        }}
        [data-testid="stPopoverContent"] {{
            background: {colors["surface"]} !important;
            border: 1px solid {colors["border"]} !important;
            color: {colors["text"]} !important;
        }}
        details[data-testid="stExpander"] {{
            background: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 18px;
            box-shadow: {colors["metric_shadow"]};
            overflow: hidden;
            margin-top: 0.5rem;
        }}
        details[data-testid="stExpander"] summary {{
            background: {colors["surface"]};
            color: {colors["text"]};
            padding: 0.85rem 1rem;
            border-bottom: 1px solid {colors["border"]};
        }}
        details[data-testid="stExpander"][open] summary {{
            margin-bottom: 0;
        }}
        details[data-testid="stExpander"] div[role="button"] p,
        details[data-testid="stExpander"] summary p,
        details[data-testid="stExpander"] p,
        details[data-testid="stExpander"] div {{
            color: {colors["text"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sticky_header(colors: dict, theme_mode: str) -> None:
    """Render a brand bar that stays visible while scrolling."""
    st.markdown(
        f"""
        <div class="sticky-header">
            <div class="sticky-header-inner">
                <div>
                    <div class="brand-title">SENTINEL AI</div>
                    <div class="brand-subtitle">Prediction And Response System</div>
                </div>
                <div class="brand-subtitle">Theme: {theme_mode}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert_box(alert_details: dict, colors: dict) -> None:
    """Render a monochrome alert panel without Streamlit's default colors."""
    style = colors["alert_styles"].get(alert_details["severity"], colors["alert_styles"]["info"])
    st.markdown(
        (
            f"<div class='alert-box' style='background:{style['background']}; color:{style['text']};'>"
            f"<div class='alert-title'>{alert_details['title']}</div>"
            f"<div>{alert_details['message']}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_html_table(dataframe: pd.DataFrame, colors: dict) -> None:
    """Render a theme-aware HTML table for consistent light and dark styling."""
    html_table = dataframe.to_html(index=False, classes="custom-table", border=0)
    st.markdown(f"<div class='table-shell'>{html_table}</div>", unsafe_allow_html=True)


def build_gauge_chart(risk_score: float, colors: dict) -> go.Figure:
    """Create a simple gauge chart for the risk score."""
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_score,
            number={"suffix": "/100", "font": {"size": 34}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": colors["gauge_bar"]},
                "steps": [
                    {"range": [0, 40], "color": colors["gauge_low"]},
                    {"range": [40, 70], "color": colors["gauge_mid"]},
                    {"range": [70, 100], "color": colors["gauge_high"]},
                ],
                "threshold": {
                    "line": {"color": colors["text"], "width": 4},
                    "thickness": 0.8,
                    "value": risk_score,
                },
            },
        )
    )
    figure.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": colors["text"], "family": "Trebuchet MS, Verdana, sans-serif"},
    )
    return figure


def build_region_comparison_chart(dataframe: pd.DataFrame, colors: dict) -> go.Figure:
    """Compare baseline regional risk using the dataset values."""
    chart_data = dataframe.copy()
    chart_data["baseline_risk_score"] = chart_data.apply(
        lambda row: calculate_flood_risk(
            rainfall_mm=row["rainfall_mm"],
            population_density=row["population_density"],
            river_level_m=row["river_level_m"],
            vulnerability_index=row["vulnerability_index"],
            total_population=row["population"],
        ).risk_score,
        axis=1,
    )

    figure = px.bar(
        chart_data.sort_values("baseline_risk_score", ascending=False),
        x="region",
        y="baseline_risk_score",
        color="baseline_risk_score",
        color_continuous_scale=colors["chart_scale"],
        labels={"region": "Region", "baseline_risk_score": "Risk Score"},
        title="Regional Flood Risk Comparison",
    )
    figure.update_layout(
        height=380,
        coloraxis_showscale=False,
        xaxis_tickangle=-20,
        template=colors["chart_template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=colors["chart_plot_bg"],
        font={"color": colors["text"], "family": "Trebuchet MS, Verdana, sans-serif"},
        title_font={"size": 24},
    )
    return figure


def build_factor_chart(factor_scores: dict, colors: dict) -> go.Figure:
    """Show the contribution of each factor to the final risk."""
    factor_frame = pd.DataFrame(
        {"Factor": list(factor_scores.keys()), "Normalized Score": list(factor_scores.values())}
    )
    figure = px.bar(
        factor_frame,
        x="Factor",
        y="Normalized Score",
        color="Normalized Score",
        color_continuous_scale=colors["chart_scale"],
        title="Risk Factor Breakdown",
    )
    figure.update_layout(
        height=320,
        coloraxis_showscale=False,
        template=colors["chart_template"],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=colors["chart_plot_bg"],
        font={"color": colors["text"], "family": "Trebuchet MS, Verdana, sans-serif"},
        title_font={"size": 24},
    )
    return figure


def main() -> None:
    """Render the Streamlit dashboard."""
    dataframe = load_data_cached()

    with st.sidebar:
        st.header("Input Controls")
        theme_mode = st.radio("Theme Mode", options=["Dark", "Light"], index=0, horizontal=True)
        colors = get_theme_colors(theme_mode)

    apply_custom_theme(colors)
    render_sticky_header(colors, theme_mode)

    st.markdown(
        """
        <div class="hero-box">
            <p class="intro-copy">
                A simple monochrome dashboard for flood prediction, affected population estimation, and response planning with a clean dark and light viewing mode.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        region_names = get_region_names(dataframe)
        selected_region = st.selectbox("Select Region", options=region_names)
        disaster_type = st.selectbox(
            "Disaster Type",
            options=["Flood", "Earthquake (Coming Soon)", "Wildfire (Coming Soon)", "Cyclone (Coming Soon)"],
            index=0,
        )

        region_record = get_region_record(dataframe, selected_region)

        st.caption("Adjust live field conditions before running the analysis.")
        rainfall_mm = st.slider("Rainfall (mm)", min_value=0, max_value=250, value=int(region_record["rainfall_mm"]))
        population_density = st.slider(
            "Population Density (people/km^2)",
            min_value=100,
            max_value=5000,
            value=int(region_record["population_density"]),
            step=50,
        )
        river_level_m = st.slider(
            "River Level (m)",
            min_value=0.0,
            max_value=8.0,
            value=float(region_record["river_level_m"]),
            step=0.1,
        )
        vulnerability_index = st.slider(
            "Infrastructure Vulnerability",
            min_value=0,
            max_value=100,
            value=int(region_record["vulnerability_index"]),
        )

        analyze_clicked = st.button("Analyze Risk", type="primary", use_container_width=True)

    selected_disaster_type = disaster_type.split(" ")[0].lower()
    risk_result = calculate_flood_risk(
        rainfall_mm=rainfall_mm,
        population_density=population_density,
        river_level_m=river_level_m,
        vulnerability_index=vulnerability_index,
        total_population=int(region_record["population"]),
    )
    recommendations = calculate_resource_recommendations(risk_result.affected_population)
    alert_details = generate_alert(
        disaster_type=selected_disaster_type,
        rainfall_mm=rainfall_mm,
        river_level_m=river_level_m,
        risk_category=risk_result.risk_category,
    )

    if analyze_clicked:
        st.toast(f"Analysis updated for {selected_region}")

    risk_style = colors["risk_styles"][risk_result.risk_category]

    top_left, top_mid, top_right = st.columns([1.1, 1, 1])
    with top_left:
        st.subheader("Risk Summary")
        st.markdown(
            (
                "<div class='risk-card' "
                f"style='background:{risk_style['background']}; color:{risk_style['text']};'>"
                f"{risk_result.risk_category}</div>"
            ),
            unsafe_allow_html=True,
        )
        st.metric("Risk Score", f"{risk_result.risk_score}/100")
        st.metric("Estimated Affected Population", f"{risk_result.affected_population:,}")
    with top_mid:
        st.subheader("Response Snapshot")
        st.metric("Rescue Teams", recommendations["rescue_teams"])
        st.metric("Food Packets / Day", f"{recommendations['food_packets']:,}")
    with top_right:
        st.subheader("Medical Support")
        st.metric("Medical Kits", f"{recommendations['medical_kits']:,}")
        st.metric("Temporary Shelters", recommendations["temporary_shelters"])

    st.subheader("Early Warning System")
    render_alert_box(alert_details, colors)

    gauge_col, impact_col = st.columns([1.15, 0.85])
    with gauge_col:
        st.plotly_chart(build_gauge_chart(risk_result.risk_score, colors), use_container_width=True)
    with impact_col:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("### Impact Estimate")
        st.write(f"**Region:** {selected_region}")
        st.write(f"**Population:** {int(region_record['population']):,}")
        st.write(f"**Estimated affected share:** {risk_result.affected_percentage * 100:.1f}%")
        st.write(f"**Current rainfall:** {rainfall_mm} mm")
        st.write(f"**Current river level:** {river_level_m:.1f} m")
        st.write(f"**Vulnerability index:** {vulnerability_index}/100")
        with st.popover("Open quick insight"):
            st.write(f"Risk category: {risk_result.risk_category}")
            st.write(f"Affected population: {risk_result.affected_population:,}")
            st.write(f"Rescue teams suggested: {recommendations['rescue_teams']}")
            st.write("This panel is designed as a fast judge-friendly summary.")
        st.markdown("</div>", unsafe_allow_html=True)

    rec_col, factor_col = st.columns(2)
    with rec_col:
        st.subheader("Recommended Resource Allocation")
        recommendation_frame = pd.DataFrame(
            {
                "Resource": ["Rescue Teams", "Food Packets", "Medical Kits", "Temporary Shelters"],
                "Recommended Quantity": [
                    recommendations["rescue_teams"],
                    recommendations["food_packets"],
                    recommendations["medical_kits"],
                    recommendations["temporary_shelters"],
                ],
            }
        )
        render_html_table(recommendation_frame, colors)
    with factor_col:
        st.plotly_chart(build_factor_chart(risk_result.factor_scores, colors), use_container_width=True)

    st.plotly_chart(build_region_comparison_chart(dataframe, colors), use_container_width=True)

    st.subheader("Dataset Preview")
    render_html_table(dataframe, colors)

    with st.expander("See scoring logic used in this demo"):
        st.write(
            "Risk score = (Rainfall x 0.40) + (Population Density x 0.20) + (River Level x 0.25) + (Vulnerability x 0.15) after normalization to a 0-100 scale."
        )
        st.write("High Risk: 70+, Medium Risk: 40-69.9, Low Risk: below 40")
        st.write(
            "Affected population is estimated using fixed percentage bands so the result stays deterministic, simple, and easy to explain during a live pitch."
        )


if __name__ == "__main__":
    main()
