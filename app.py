import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import (
    get_disaster_subset,
    get_disaster_types,
    get_region_names,
    get_region_record,
    load_region_data,
)
from utils.recommendation_engine import calculate_resource_recommendations
from utils.resqnet_engine import assess_region, build_sms_alert


st.set_page_config(
    page_title="RESQnet",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded",
)


COSMOS_BLUE = "#003049"
HIGH_RISK_COLOR = "#FF4B4B"
MEDIUM_RISK_COLOR = "#FFD93D"
LOW_RISK_COLOR = "#4CAF50"

COLOR_MAP = {
    "High": HIGH_RISK_COLOR,
    "Medium": MEDIUM_RISK_COLOR,
    "Low": LOW_RISK_COLOR,
}


@st.cache_data
def load_data_cached() -> pd.DataFrame:
    """Load and cache the dataset for fast dashboard interactions."""
    return load_region_data()


def apply_resqnet_theme() -> None:
    """Inject the RESQnet dark theme and header styling."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: #003049;
            color: #ffffff;
        }}
        html, body, [class*="css"] {{
            font-family: "Trebuchet MS", Verdana, sans-serif;
            color: #ffffff;
        }}
        h1, h2, h3, h4 {{
            color: #ffffff !important;
            letter-spacing: -0.02em;
        }}
        [data-testid="stAppViewContainer"] > .main {{
            padding-top: 4.8rem;
        }}
        .block-container {{
            padding-top: 1rem;
        }}
        [data-testid="stSidebar"] {{
            background: #003049;
            border-right: 1px solid #6ea0f1;
        }}
        [data-testid="stSidebar"] * {{
            color: #ffffff;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background: #0a347b;
            border: 1px solid #7aa8ef;
            color: #ffffff;
            border-radius: 14px;
        }}
        [data-testid="stSidebar"] .stRadio label {{
            color: #ffffff !important;
        }}
        div[data-testid="metric-container"] {{
            background: #003049;
            border: 1px solid #7aa8ef;
            border-radius: 18px;
            padding: 1rem;
            box-shadow: none;
        }}
        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] div {{
            color: #ffffff !important;
        }}
        .fixed-header {{
            position: fixed;
            top: 10px;
            left: 80px;
            z-index: 1002;
            background: #003049;
            border: 1px solid #7aa8ef;
            border-radius: 14px;
            padding: 0.55rem 0.9rem 0.6rem 0.9rem;
            box-shadow: none;
        }}
        .header-title {{
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 900;
            letter-spacing: -0.04em;
            line-height: 1;
        }}
        .header-subtitle {{
            color: #dbe8ff;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.68rem;
            font-weight: 700;
            margin-top: 0.2rem;
        }}
        [data-testid="stSidebar"] .stButton button,
        [data-testid="stPopover"] button {{
            background: #ffffff;
            color: #003049;
            border: 1px solid #ffffff;
            border-radius: 14px;
            font-weight: 800;
            transition: all 0.2s ease;
        }}
        [data-testid="stSidebar"] .stButton button *,
        [data-testid="stPopover"] button * {{
            color: #003049 !important;
            fill: #003049 !important;
        }}
        [data-testid="stSidebar"] .stButton button:hover,
        [data-testid="stPopover"] button:hover {{
            color: #ffffff;
            background: #dbe8ff;
            border-color: #dbe8ff;
            transform: none;
        }}
        [data-testid="stSidebar"] div[data-baseweb="slider"] > div > div:nth-child(1) {{
            background: #a7c5f2 !important;
            height: 0.35rem !important;
            border-radius: 999px !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="slider"] > div > div:nth-child(2) {{
            background: {COSMOS_BLUE} !important;
            height: 0.35rem !important;
            border-radius: 999px !important;
        }}
        [data-testid="stSidebar"] div[data-baseweb="slider"] [role="slider"] {{
            background: {COSMOS_BLUE} !important;
            border: 3px solid #ffffff !important;
            box-shadow: 0 0 0 2px {COSMOS_BLUE} !important;
        }}
        .resq-card {{
            background: #003049;
            border: 1px solid #7aa8ef;
            border-radius: 20px;
            padding: 1rem 1.15rem;
            box-shadow: none;
        }}
        .section-heading {{
            margin-top: 0.35rem;
        }}
        .risk-chip {{
            display: inline-block;
            padding: 0.75rem 1rem;
            border-radius: 16px;
            font-weight: 800;
            text-align: center;
            min-width: 160px;
            background: #003049;
            color: #ffffff;
            border: 1px solid #7aa8ef;
        }}
        .warning-box {{
            border-radius: 18px;
            padding: 1rem 1.1rem;
            color: #ffffff;
            border: 1px solid #7aa8ef;
            background: #003049;
        }}
        .sms-box {{
            background: #003049;
            color: #ffffff;
            border-left: 6px solid {COSMOS_BLUE};
            border-radius: 18px;
            padding: 1rem 1.15rem;
            white-space: pre-wrap;
            font-family: Consolas, "Courier New", monospace;
            box-shadow: none;
        }}
        .legend-row {{
            display: flex;
            gap: 1.2rem;
            flex-wrap: wrap;
            margin-top: 0.65rem;
            margin-bottom: 0.35rem;
        }}
        .legend-item {{
            font-weight: 700;
            color: #ffffff;
        }}
        .stDataFrame {{
            border: 1px solid #7aa8ef;
            border-radius: 12px;
            overflow: hidden;
        }}
        [data-testid="stInfo"], [data-testid="stWarning"] {{
            background: #003049;
            color: #ffffff;
            border: 1px solid #7aa8ef;
            box-shadow: none;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render the fixed RESQnet header."""
    st.markdown(
        """
        <div class="fixed-header">
            <div class="header-title">RESQnet</div>
            <div class="header-subtitle">Predict. Protect.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_warning_box(assessment, recommendations: dict) -> None:
    """Display a clean early warning panel."""
    st.markdown(
        f"""
        <div class="warning-box">
            <div style="font-size:1.05rem; font-weight:800; margin-bottom:0.35rem;">
                {assessment.warning_title}
            </div>
            <div style="margin-bottom:0.6rem;">{assessment.warning_message}</div>
            <div>Safe Zone: {assessment.safe_zone_type}</div>
            <div>Suggested Rescue Teams: {recommendations["rescue_teams"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_disaster_map(disaster_frame: pd.DataFrame, selected_region: str) -> go.Figure:
    """Create the disaster risk map with safe zones."""
    map_frame = disaster_frame.copy()
    map_frame["hover_text"] = map_frame.apply(
        lambda row: (
            f"<b>{row['region']}</b><br>"
            f"Disaster: {row['disaster_type']}<br>"
            f"Risk: {row['risk_level']}<br>"
            f"Population: {int(row['population']):,}<br>"
            f"Safe Zone: {row['safe_zone_type']}"
        ),
        axis=1,
    )

    figure = px.scatter_mapbox(
        map_frame,
        lat="latitude",
        lon="longitude",
        color="risk_level",
        color_discrete_map={
            "High": HIGH_RISK_COLOR,
            "Medium": MEDIUM_RISK_COLOR,
            "Low": LOW_RISK_COLOR,
        },
        hover_name="region",
        hover_data={
            "disaster_type": True,
            "risk_level": True,
            "population": True,
            "safe_zone_type": True,
            "latitude": False,
            "longitude": False,
        },
        size=[18 if region == selected_region else 12 for region in map_frame["region"]],
        size_max=18,
        zoom=2.6,
        height=520,
    )

    safe_zone_frame = map_frame.copy()
    figure.add_trace(
        go.Scattermapbox(
            lat=safe_zone_frame["safe_zone_lat"],
            lon=safe_zone_frame["safe_zone_lon"],
            mode="markers",
            marker=go.scattermapbox.Marker(size=14, color=COSMOS_BLUE, symbol="star"),
            name="Safe Zone",
            text=safe_zone_frame.apply(
                lambda row: f"{row['region']} Safe Zone - {row['safe_zone_type']}",
                axis=1,
            ),
            hovertemplate="%{text}<extra></extra>",
        )
    )

    figure.update_layout(
        mapbox_style="open-street-map",
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.0,
            font=dict(color="white"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )
    return figure


def render_table(dataframe: pd.DataFrame) -> None:
    """Render a theme-aware table preview."""
    styled = dataframe.to_html(index=False, border=0)
    st.markdown(
        f"""
        <div class="resq-card" style="overflow-x:auto;">
            {styled}
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Render the RESQnet dashboard."""
    dataframe = load_data_cached()
    apply_resqnet_theme()
    render_header()

    with st.sidebar:
        st.header("Inputs")
        disaster_types = get_disaster_types(dataframe)
        selected_disaster = st.selectbox("Disaster Type", options=disaster_types)
        disaster_regions = get_region_names(get_disaster_subset(dataframe, selected_disaster))
        selected_region = st.selectbox("Location", options=disaster_regions)
        analyze_clicked = st.button("Analyze Risk", type="primary", use_container_width=True)

    selected_record = get_region_record(dataframe, selected_region)
    assessment = assess_region(selected_record)
    recommendations = calculate_resource_recommendations(assessment.affected_population)
    disaster_map_frame = get_disaster_subset(dataframe, selected_disaster)

    if analyze_clicked:
        st.toast(f"RESQnet refreshed {selected_region}")

    st.subheader("Risk Summary")
    summary_left, summary_mid, summary_right = st.columns(3)
    with summary_left:
        st.markdown(
            f"<div class='risk-chip'>{assessment.risk_level} Risk</div>",
            unsafe_allow_html=True,
        )
        st.metric("Risk Score", f"{assessment.risk_score}/100")
        st.metric("Population", f"{assessment.population:,}")
    with summary_mid:
        st.metric("Estimated Affected People", f"{assessment.affected_population:,}")
        st.metric("Rescue Teams", recommendations["rescue_teams"])
        st.metric("Medical Kits", f"{recommendations['medical_kits']:,}")
    with summary_right:
        st.metric("Food Packets", f"{recommendations['food_packets']:,}")
        st.metric("Temporary Shelters", recommendations["temporary_shelters"])
        st.metric("Safe Zone", assessment.safe_zone_type)

    st.subheader("Early Warning")
    render_warning_box(assessment, recommendations)

    st.markdown("### Disaster Risk Map")
    st.plotly_chart(build_disaster_map(disaster_map_frame, selected_region), use_container_width=True)
    st.markdown(
        """
        <div class="legend-row">
            <div class="legend-item">High Risk</div>
            <div class="legend-item">Medium Risk</div>
            <div class="legend-item">Low Risk</div>
            <div class="legend-item">Safe Zone</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # DATASET PREVIEW RESTORED
    st.subheader("Dataset Preview")
    st.dataframe(disaster_map_frame, use_container_width=True, hide_index=True)

    st.subheader("RESQnet Emergency Alerts")
    if assessment.risk_level == "High":
        sms_message = build_sms_alert(assessment)
        st.markdown(
            f"""
            <div class="sms-box">
{sms_message}
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.warning("Sending alerts to affected users...")
    else:
        st.info("Mass SMS alerts are not triggered for this location right now. RESQnet continues active monitoring.")


if __name__ == "__main__":
    main()
