# DisasterRelief AI - Prediction & Response System

DisasterRelief AI is a simple, hackathon-ready Streamlit application for flood risk prediction and disaster response planning. It uses a clear rule-based scoring engine instead of complex machine learning so it is easy to build, explain, and demo in 24-48 hours.

## Features
- Flood-focused early warning and risk assessment dashboard
- Region-based analysis with editable live input conditions
- Risk score and risk category output: High, Medium, or Low
- Estimated affected population calculation
- Response recommendations for rescue teams, food packets, medical kits, and temporary shelters
- Visual dashboard with metrics, warning banners, charts, and dataset preview
- Modular code structure that can be extended later to support earthquakes, wildfire, and cyclones

## Tech Stack
- Python
- Streamlit
- Pandas
- Plotly

## Folder Structure
```text
disaster_relief_ai/
|-- app.py
|-- data/
|   `-- sample_regions.csv
|-- utils/
|   |-- __init__.py
|   |-- alert_engine.py
|   |-- data_loader.py
|   |-- recommendation_engine.py
|   `-- risk_engine.py
|-- README.md
`-- requirements.txt
```

## Installation
1. Make sure Python 3.10+ is installed.
2. Open a terminal in the project folder:
   ```bash
   cd disaster_relief_ai
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run
Start the Streamlit app:

```bash
streamlit run app.py
```

Streamlit will open a local browser tab automatically. If it does not, copy the local URL from the terminal and open it manually.

## Demo Flow
1. Launch the app.
2. Select a region such as `Delta Zone` or `Coastal City`.
3. Adjust rainfall, river level, and vulnerability to simulate changing field conditions.
4. Click `Analyze Risk`.
5. Show the risk score, warning message, estimated affected population, and recommended resource allocation.
6. Use the regional comparison chart to explain how different areas compare.
7. Open the scoring logic expander to show the judges that the model is transparent and explainable.

## How Judges Should View This
- This project is built for practical disaster response, not academic complexity.
- The AI logic is intentionally explainable so emergency teams can trust the output.
- The real demo value is fast situational awareness: one screen shows risk, impact, alert level, and response needs.
- The app is designed to be extended with live weather APIs, SMS alerts, and more disaster types after the hackathon.

## Example Pitch Script
"DisasterRelief AI helps emergency teams understand flood risk in seconds. We combine rainfall, river level, population density, and infrastructure vulnerability into a transparent risk score. Then the system estimates how many people may be affected and recommends how many rescue teams, food packets, and medical kits should be deployed. The result is a simple dashboard that decision-makers can understand in under a minute."

## Scoring Logic
The flood risk score uses a weighted rule-based formula:

- Rainfall contribution: 40%
- Population density contribution: 20%
- River level contribution: 25%
- Vulnerability contribution: 15%

After normalization, the final score is mapped to:
- `70+` = High Risk
- `40-69.9` = Medium Risk
- `<40` = Low Risk

Affected population is estimated using deterministic percentage bands:
- High Risk: 30% to 50%
- Medium Risk: 10% to 25%
- Low Risk: 2% to 8%

## Future Improvements
- Add support for earthquakes, wildfires, and cyclones with dedicated scoring rules
- Connect to live rainfall and river sensor APIs
- Add GIS map visualization for hotspots
- Add evacuation route planning
- Export response plans as PDF or CSV
- Add SMS/email alert integration for local authorities

## Beginner Notes
- Start reading from `app.py` to understand the app flow.
- The `utils` folder contains the logic modules used by the app.
- The dataset is stored locally in `data/sample_regions.csv`, so there is no database setup.
- The formulas are intentionally simple and safe for a hackathon demo.
