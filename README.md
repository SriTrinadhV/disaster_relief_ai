# RESQnet

RESQnet is a Streamlit disaster management dashboard built for hackathon demos. It helps teams review disaster risk, inspect safe zones, compare impacted regions on a map, and simulate emergency SMS alerts.

## Highlights
- Disaster selector for flood, earthquake, wildfire, and cyclone scenarios
- Regional risk summary with affected population estimates
- Safe-zone aware disaster map using Plotly Mapbox
- Simulated RESQnet emergency alert panel for high-risk regions
- Beginner-friendly modular Python structure

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure
```text
disaster_relief_ai/
|-- app.py
|-- data/
|   `-- sample_regions.csv
|-- utils/
|   |-- alert_engine.py
|   |-- data_loader.py
|   |-- recommendation_engine.py
|   |-- resqnet_engine.py
|   `-- risk_engine.py
|-- README.md
`-- requirements.txt
```

## Commit Story For Judges
This branch was intentionally organized into small commits to show the project build-up:
- setup
- data
- logic
- core UI
- map and alert features
- docs and theme polish
