import time

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.ai_agent import get_gemini_response
from utils.data_loader import (
    get_disaster_subset,
    get_disaster_types,
    get_region_names,
    get_region_record,
    load_region_data,
)
from utils.recommendation_engine import calculate_resource_recommendations
from utils.resqnet_engine import (
    assess_region,
    build_sms_alert,
    estimate_notified_users,
    simulate_disaster_progression,
)


st.set_page_config(
    page_title="RESQnet",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded",
)


COSMOS_BLUE = "#003049"
LIGHT_BLUE = "#E6F0FF"
HIGH_RISK_COLOR = "#FF4B4B"
MEDIUM_RISK_COLOR = "#FFD93D"
LOW_RISK_COLOR = "#4CAF50"


@st.cache_data
def load_data_cached() -> pd.DataFrame:
    """Load and cache the dataset for fast dashboard interactions."""
    return load_region_data()


def initialize_state() -> None:
    """Create session state keys used by the dashboard flow."""
    defaults = {
        "analysis_ready": False,
        "analysis_state": None,
        "simulation_data": None,
        "simulation_label": "",
        "ai_answer": "",
        "sms_status": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def get_default_rainfall(risk_level: str) -> int:
    """Provide a simple starting rainfall/severity value for the slider."""
    defaults = {"High": 80, "Medium": 55, "Low": 30}
    return defaults.get(risk_level, 50)


def apply_resqnet_theme() -> None:
    """Inject the current RESQnet theme and simple header styling."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {COSMOS_BLUE};
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
            padding-bottom: 2rem;
        }}
        [data-testid="stSidebar"] {{
            background: {COSMOS_BLUE};
            border-right: 1px solid #8db4ef;
        }}
        [data-testid="stSidebar"] * {{
            color: #ffffff;
        }}
        [data-testid="stSidebar"] [data-baseweb="select"] > div {{
            background: #0b3f5f;
            border: 1px solid #8db4ef;
            color: #ffffff;
            border-radius: 12px;
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
            box-shadow: 0 0 0 2px #a7c5f2 !important;
        }}
        div[data-testid="metric-container"] {{
            background: {COSMOS_BLUE};
            border: 1px solid #8db4ef;
            border-radius: 14px;
            padding: 0.9rem;
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
            background: {COSMOS_BLUE};
            border: 1px solid #8db4ef;
            border-radius: 12px;
            padding: 0.55rem 0.9rem 0.6rem 0.9rem;
        }}
        .header-title {{
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 900;
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
        .resq-box {{
            background: {LIGHT_BLUE};
            color: #10263d;
            border: 1px solid #bfd4f3;
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-bottom: 1rem;
        }}
        [data-testid="stSidebar"] .stButton button,
        [data-testid="stButton"] > button,
        [data-testid="stPopover"] button {{
            background: #ffffff;
            color: {COSMOS_BLUE};
            border: 1px solid #ffffff;
            border-radius: 12px;
            font-weight: 700;
            box-shadow: none;
        }}
        [data-testid="stSidebar"] .stButton button *,
        [data-testid="stButton"] > button *,
        [data-testid="stPopover"] button * {{
            color: {COSMOS_BLUE} !important;
            fill: {COSMOS_BLUE} !important;
        }}
        [data-testid="stSidebar"] .stButton button:hover,
        [data-testid="stButton"] > button:hover,
        [data-testid="stPopover"] button:hover {{
            background: #f7fbff;
            color: {COSMOS_BLUE};
            border-color: #f7fbff;
        }}
        .legend-row {{
            display: flex;
            gap: 1.2rem;
            flex-wrap: wrap;
            margin-top: 0.65rem;
            margin-bottom: 0.6rem;
        }}
        .legend-item {{
            font-weight: 600;
            color: #ffffff;
        }}
        [data-testid="stInfo"], [data-testid="stWarning"], [data-testid="stSuccess"] {{
            background: {LIGHT_BLUE};
            color: #10263d;
            border: 1px solid #bfd4f3;
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


def render_neutral_box(title: str, body: str) -> None:
    """Render a simple neutral content box."""
    st.markdown(
        f"""
        <div class="resq-box">
            <div style="font-weight:700; margin-bottom:0.3rem;">{title}</div>
            <div>{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def create_map(disaster_frame: pd.DataFrame) -> go.Figure:
    """Create a centered disaster risk map that keeps all valid locations visible."""
    map_frame = disaster_frame.copy()
    map_frame = map_frame.dropna(subset=["latitude", "longitude"])
    map_frame = map_frame[
        map_frame["latitude"].between(-90, 90) & map_frame["longitude"].between(-180, 180)
    ]

    marker_sizes = [
        15 if risk == "High" else 10 if risk == "Medium" else 8 for risk in map_frame["risk_level"]
    ]

    figure = px.scatter_mapbox(
        map_frame,
        lat="latitude",
        lon="longitude",
        hover_name="region",
        hover_data=["risk_level", "disaster_type"],
        color="risk_level",
        color_discrete_map={
            "High": "#FF4B4B",
            "Medium": "#FFD93D",
            "Low": "#4CAF50",
        },
        size=marker_sizes,
        size_max=15,
        zoom=3,
        height=500,
    )

    figure.update_traces(marker={"symbol": "circle"})
    figure.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            center=dict(
                lat=map_frame["latitude"].mean(),
                lon=map_frame["longitude"].mean(),
            ),
            zoom=3,
        ),
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


def build_impact_message(assessment) -> str:
    """Create a short impact statement based on the current risk."""
    if assessment.risk_level == "High":
        return f"This could affect {assessment.affected_population:,} people and immediate action is required."
    if assessment.risk_level == "Medium":
        return f"This could affect {assessment.affected_population:,} people and preparedness measures are recommended."
    return "Estimated impact is limited at current conditions, but monitoring should continue."


def build_ai_context(assessment, recommendations: dict) -> dict:
    """Build the app context that will be sent to Gemini."""
    return {
        "Region": assessment.region,
        "Disaster Type": assessment.disaster_type,
        "Risk Score": assessment.risk_score,
        "Risk Level": assessment.risk_level,
        "Affected Population": f"{assessment.affected_population:,}",
        "Safe Zone": assessment.safe_zone_type,
        "Rescue Teams": recommendations["rescue_teams"],
        "Food Packets": recommendations["food_packets"],
        "Medical Kits": recommendations["medical_kits"],
        "Warning Message": assessment.warning_message,
    }


def main() -> None:
    """Render the RESQnet dashboard."""
    initialize_state()
    dataframe = load_data_cached()
    apply_resqnet_theme()
    render_header()

    with st.sidebar:
        st.header("Step 1: Inputs")
        disaster_types = get_disaster_types(dataframe)
        selected_disaster = st.selectbox("Disaster Type", options=disaster_types)
        disaster_subset = get_disaster_subset(dataframe, selected_disaster)
        disaster_regions = get_region_names(disaster_subset)
        selected_region = st.selectbox("Location", options=disaster_regions)
        slider_default = get_default_rainfall(get_region_record(disaster_subset, selected_region)["risk_level"])
        rainfall_input = st.slider("Rainfall / Severity Input", min_value=0, max_value=100, value=slider_default)

        st.header("Step 2: Analyze")
        analyze_clicked = st.button("Analyze Risk", type="primary", width="stretch")

    if analyze_clicked:
        st.session_state.analysis_ready = True
        st.session_state.analysis_state = {
            "disaster": selected_disaster,
            "region": selected_region,
            "rainfall": rainfall_input,
        }
        st.session_state.simulation_data = None
        st.session_state.simulation_label = ""
        st.session_state.ai_answer = ""
        st.session_state.sms_status = ""

    if not st.session_state.analysis_ready or not st.session_state.analysis_state:
        st.info("Complete the inputs and click Analyze Risk to view the full dashboard.")
        return

    analysis_state = st.session_state.analysis_state
    analyzed_subset = get_disaster_subset(dataframe, analysis_state["disaster"])
    analyzed_record = get_region_record(analyzed_subset, analysis_state["region"])
    assessment = assess_region(analyzed_record, rainfall_level=analysis_state["rainfall"])
    recommendations = calculate_resource_recommendations(assessment.affected_population)

    st.subheader("Step 3: Risk Summary")
    summary_left, summary_mid, summary_right = st.columns(3)
    with summary_left:
        st.metric("Risk Score", f"{assessment.risk_score}/100")
        st.metric("Population", f"{assessment.population:,}")
        st.metric("Risk Level", assessment.risk_level)
    with summary_mid:
        st.metric("Estimated Affected People", f"{assessment.affected_population:,}")
        st.metric("Rescue Teams", recommendations["rescue_teams"])
        st.metric("Medical Kits", f"{recommendations['medical_kits']:,}")
    with summary_right:
        st.metric("Food Packets", f"{recommendations['food_packets']:,}")
        st.metric("Temporary Shelters", recommendations["temporary_shelters"])
        st.metric("Safe Zone", assessment.safe_zone_type)

    st.subheader("Impact Message")
    render_neutral_box("Current Impact", build_impact_message(assessment))

    st.subheader("Early Warning")
    render_neutral_box(assessment.warning_title, assessment.warning_message)

    if st.button("Simulate Disaster Progression"):
        st.session_state.simulation_data = pd.DataFrame(
            simulate_disaster_progression(analyzed_record, analysis_state["rainfall"])
        )
        st.session_state.simulation_label = f"Simulation Progression for {assessment.region}"

    if st.session_state.simulation_data is not None:
        st.subheader("Simulation Progression")
        st.caption(st.session_state.simulation_label)
        st.dataframe(st.session_state.simulation_data, width="stretch", hide_index=True)
        simulation_chart = st.session_state.simulation_data.set_index("Step")[["Risk Score"]]
        st.line_chart(simulation_chart, width="stretch")

    st.subheader("Disaster Risk Map")
    st.write(analyzed_subset)
    st.plotly_chart(create_map(analyzed_subset), width="stretch")
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

    st.subheader("Recommendations")
    recommendation_df = pd.DataFrame(
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
    st.dataframe(recommendation_df, width="stretch", hide_index=True)

    st.subheader("Dataset Preview")
    st.dataframe(analyzed_subset, width="stretch", hide_index=True)

    st.subheader("RESQnet AI Assistant")
    ai_question = st.text_input("Ask RESQnet about the current situation")
    if st.button("Ask AI"):
        if not ai_question.strip():
            st.warning("Enter a question for the AI assistant.")
        else:
            try:
                with st.spinner("Generating AI response..."):
                    st.session_state.ai_answer = get_gemini_response(
                        ai_question,
                        build_ai_context(assessment, recommendations),
                    )
            except ValueError as error:
                st.info(str(error))
            except Exception:
                st.error("The AI assistant could not respond right now. Please try again.")

    if st.session_state.ai_answer:
        render_neutral_box("AI Response", st.session_state.ai_answer)

    st.subheader("RESQnet Emergency Alerts")
    sms_message = build_sms_alert(assessment)
    render_neutral_box("SMS Preview", sms_message)

    if st.button("Send Alerts"):
        if assessment.risk_level == "Low":
            st.session_state.sms_status = "No alerts needed at this time."
        else:
            with st.spinner("Sending alerts..."):
                time.sleep(1)
            st.session_state.sms_status = f"{estimate_notified_users(assessment.affected_population):,} users notified"

    if st.session_state.sms_status:
        if assessment.risk_level == "Low":
            st.info(st.session_state.sms_status)
        else:
            st.success(st.session_state.sms_status)


if __name__ == "__main__":
    main()
