import streamlit as st

from utils.data_loader import get_disaster_subset, get_disaster_types, get_region_names, get_region_record, load_region_data
from utils.recommendation_engine import calculate_resource_recommendations
from utils.resqnet_engine import assess_region


st.set_page_config(page_title="RESQnet", page_icon="R", layout="wide")


@st.cache_data
def load_data_cached():
    return load_region_data()


def main() -> None:
    dataframe = load_data_cached()

    st.title("RESQnet")
    st.caption("Predict. Protect.")

    with st.sidebar:
        st.header("Inputs")
        disaster_types = get_disaster_types(dataframe)
        selected_disaster = st.selectbox("Disaster Type", options=disaster_types)
        disaster_regions = get_region_names(get_disaster_subset(dataframe, selected_disaster))
        selected_region = st.selectbox("Location", options=disaster_regions)
        st.button("Analyze Risk", type="primary", use_container_width=True)

    selected_record = get_region_record(dataframe, selected_region)
    assessment = assess_region(selected_record)
    recommendations = calculate_resource_recommendations(assessment.affected_population)

    st.subheader("Risk Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Risk Level", assessment.risk_level)
        st.metric("Risk Score", f"{assessment.risk_score}/100")
    with col2:
        st.metric("Population", f"{assessment.population:,}")
        st.metric("Estimated Affected People", f"{assessment.affected_population:,}")
    with col3:
        st.metric("Rescue Teams", recommendations["rescue_teams"])
        st.metric("Medical Kits", f"{recommendations['medical_kits']:,}")

    st.subheader("Early Warning")
    st.write(assessment.warning_title)
    st.write(assessment.warning_message)

    st.subheader("Recommendations")
    st.write(f"Food Packets: {recommendations['food_packets']:,}")
    st.write(f"Temporary Shelters: {recommendations['temporary_shelters']}")
    st.write(f"Safe Zone: {assessment.safe_zone_type}")


if __name__ == "__main__":
    main()
