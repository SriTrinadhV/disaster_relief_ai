import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.alert_engine import generate_alert
from utils.data_loader import get_region_names, get_region_record, load_region_data
from utils.recommendation_engine import calculate_resource_recommendations
from utils.risk_engine import calculate_flood_risk


st.set_page_config(
    page_title="DisasterRelief AI",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)


RISK_COLORS = {
    "High Risk": "#d62828",
    "Medium Risk": "#f4a261",
    "Low Risk": "#2a9d8f",
}


@st.cache_data
def load_data_cached() -> pd.DataFrame:
    """Cache dataset loading so the app stays responsive."""
    return load_region_data()


def build_gauge_chart(risk_score: float) -> go.Figure:
    """Create a simple gauge chart for the risk score."""
    figure = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_score,
            number={"suffix": "/100", "font": {"size": 34}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#1d3557"},
                "steps": [
                    {"range": [0, 40], "color": "#b7e4c7"},
                    {"range": [40, 70], "color": "#ffe8a1"},
                    {"range": [70, 100], "color": "#f4a3a3"},
                ],
                "threshold": {
                    "line": {"color": "#d62828", "width": 4},
                    "thickness": 0.8,
                    "value": risk_score,
                },
            },
        )
    )
    figure.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=280)
    return figure


def build_region_comparison_chart(dataframe: pd.DataFrame) -> go.Figure:
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
        color_continuous_scale=["#2a9d8f", "#f4a261", "#d62828"],
        labels={"region": "Region", "baseline_risk_score": "Risk Score"},
        title="Regional Flood Risk Comparison",
    )
    figure.update_layout(height=380, coloraxis_showscale=False, xaxis_tickangle=-20)
    return figure


def build_factor_chart(factor_scores: dict) -> go.Figure:
    """Show the contribution of each factor to the final risk."""
    factor_frame = pd.DataFrame(
        {"Factor": list(factor_scores.keys()), "Normalized Score": list(factor_scores.values())}
    )
    figure = px.bar(
        factor_frame,
        x="Factor",
        y="Normalized Score",
        color="Normalized Score",
        color_continuous_scale=["#cdeae5", "#f4a261", "#d62828"],
        title="Risk Factor Breakdown",
    )
    figure.update_layout(height=320, coloraxis_showscale=False)
    return figure


def show_alert(alert_details: dict) -> None:
    """Display alert messages using Streamlit status banners."""
    severity = alert_details["severity"]
    title = alert_details["title"]
    message = alert_details["message"]

    if severity == "error":
        st.error(f"{title}: {message}")
    elif severity == "warning":
        st.warning(f"{title}: {message}")
    elif severity == "info":
        st.info(f"{title}: {message}")
    else:
        st.success(f"{title}: {message}")


def main() -> None:
    """Render the Streamlit dashboard."""
    dataframe = load_data_cached()

    st.markdown(
        """
        <style>
        .hero-box {
            background: linear-gradient(135deg, #e0f2fe, #f8fafc 55%, #dbeafe);
            padding: 1.4rem 1.6rem;
            border-radius: 18px;
            border: 1px solid #d7e3f4;
            margin-bottom: 1rem;
        }
        .risk-card {
            padding: 1rem 1.2rem;
            border-radius: 16px;
            color: white;
            text-align: center;
            font-weight: 600;
            margin-top: 0.3rem;
            margin-bottom: 0.8rem;
        }
        .panel-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1rem 1.1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-box">
            <h1 style="margin-bottom:0.3rem;">🌊 DisasterRelief AI</h1>
            <p style="font-size:1.05rem; margin-bottom:0.2rem;">
                Prediction & Response System for fast, explainable flood risk analysis.
            </p>
            <p style="margin:0; color:#475569;">
                Designed for hackathon demos: select a region, adjust live conditions, and generate response recommendations in seconds.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Input Controls")
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

    if not analyze_clicked:
        st.info("Select a region, adjust the inputs, and click Analyze Risk to generate a live disaster response summary.")
        analyze_clicked = True

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

    risk_color = RISK_COLORS[risk_result.risk_category]

    top_left, top_mid, top_right = st.columns([1.1, 1, 1])
    with top_left:
        st.subheader("Risk Summary")
        st.markdown(
            f"<div class='risk-card' style='background:{risk_color};'>{risk_result.risk_category}</div>",
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
    show_alert(alert_details)

    gauge_col, impact_col = st.columns([1.15, 0.85])
    with gauge_col:
        st.plotly_chart(build_gauge_chart(risk_result.risk_score), use_container_width=True)
    with impact_col:
        st.markdown("<div class='panel-box'>", unsafe_allow_html=True)
        st.markdown("### Impact Estimate")
        st.write(f"**Region:** {selected_region}")
        st.write(f"**Population:** {int(region_record['population']):,}")
        st.write(f"**Estimated affected share:** {risk_result.affected_percentage * 100:.1f}%")
        st.write(f"**Current rainfall:** {rainfall_mm} mm")
        st.write(f"**Current river level:** {river_level_m:.1f} m")
        st.write(f"**Vulnerability index:** {vulnerability_index}/100")
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
        st.dataframe(recommendation_frame, use_container_width=True, hide_index=True)
    with factor_col:
        st.plotly_chart(build_factor_chart(risk_result.factor_scores), use_container_width=True)

    st.plotly_chart(build_region_comparison_chart(dataframe), use_container_width=True)

    st.subheader("Dataset Preview")
    st.dataframe(dataframe, use_container_width=True, hide_index=True)

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
