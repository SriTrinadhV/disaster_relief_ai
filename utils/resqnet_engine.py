from dataclasses import dataclass


RISK_SCORE_MAP = {
    "High": 88,
    "Medium": 61,
    "Low": 28,
}

RISK_SHARE_MAP = {
    "High": 0.34,
    "Medium": 0.17,
    "Low": 0.06,
}

WARNING_MESSAGES = {
    "Flood": {
        "High": "Severe flood impact expected. Move people away from low-lying areas and near-river settlements.",
        "Medium": "Flood-prone pockets should be monitored closely. Prepare pumps, relief teams, and shelter access.",
        "Low": "Conditions are currently manageable, but seasonal flooding indicators should still be watched.",
    },
    "Earthquake": {
        "High": "Strong seismic disruption is possible. Emergency teams should prepare open assembly areas and rapid rescue support.",
        "Medium": "Moderate seismic sensitivity detected. Buildings and evacuation plans should be reviewed carefully.",
        "Low": "No immediate severe seismic disruption is indicated, but readiness checks should continue.",
    },
    "Wildfire": {
        "High": "Rapid fire spread is possible. Keep evacuation corridors and open refuge areas ready for deployment.",
        "Medium": "Fire-prone zones should be monitored closely. Standby crews and community alerts are recommended.",
        "Low": "Current wildfire pressure is limited, though dry conditions should still be tracked.",
    },
    "Cyclone": {
        "High": "Severe coastal impact expected. Move people toward hardened shelters and protected inland zones.",
        "Medium": "Cyclone conditions may intensify. Prepare transport routes, relief stocks, and shelter access.",
        "Low": "Immediate cyclone threat is limited, but coastal readiness should continue.",
    },
}


@dataclass
class RegionAssessment:
    region: str
    disaster_type: str
    risk_level: str
    risk_score: int
    population: int
    affected_population: int
    safe_zone_type: str
    safe_zone_lat: float
    safe_zone_lon: float
    warning_title: str
    warning_message: str


def classify_risk_level(score: int) -> str:
    """Classify risk based on score thresholds."""
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def calculate_adjusted_score(base_score: int, disaster_type: str, rainfall_level: int) -> int:
    """Apply a simple rainfall/severity adjustment for live analysis and simulation."""
    multiplier_by_disaster = {
        "Flood": 0.45,
        "Cyclone": 0.35,
        "Wildfire": 0.20,
        "Earthquake": 0.10,
    }
    rainfall_offset = rainfall_level - 50
    adjusted_score = round(base_score + rainfall_offset * multiplier_by_disaster.get(disaster_type, 0.25))
    return max(0, min(100, adjusted_score))


def assess_region(region_record, rainfall_level: int = 50) -> RegionAssessment:
    """Build a simple disaster assessment from a selected dataset row."""
    risk_level = str(region_record["risk_level"])
    disaster_type = str(region_record["disaster_type"])
    population = int(region_record["population"])
    base_score = RISK_SCORE_MAP[risk_level]
    risk_score = calculate_adjusted_score(base_score, disaster_type, rainfall_level)
    risk_level = classify_risk_level(risk_score)
    affected_population = round(population * RISK_SHARE_MAP[risk_level])

    warning_title = f"{risk_level} {disaster_type} Risk"
    warning_message = WARNING_MESSAGES[disaster_type][risk_level]

    return RegionAssessment(
        region=str(region_record["region"]),
        disaster_type=disaster_type,
        risk_level=risk_level,
        risk_score=risk_score,
        population=population,
        affected_population=affected_population,
        safe_zone_type=str(region_record["safe_zone_type"]),
        safe_zone_lat=float(region_record["safe_zone_lat"]),
        safe_zone_lon=float(region_record["safe_zone_lon"]),
        warning_title=warning_title,
        warning_message=warning_message,
    )


def build_sms_alert(assessment: RegionAssessment) -> str:
    """Return the simulated RESQnet SMS alert text."""
    if assessment.risk_level == "Low":
        return "No alerts needed at this time."

    short_warning = {
        "High": "Severe conditions expected.",
        "Medium": "Standby conditions in effect.",
    }[assessment.risk_level]

    return (
        "RESQnet ALERT\n\n"
        f"Disaster: {assessment.disaster_type}\n"
        f"Location: {assessment.region}\n"
        f"Risk Level: {assessment.risk_level.upper()}\n\n"
        f"{short_warning}\n\n"
        f"Safe Zone: {assessment.safe_zone_type}\n"
        "Route: Move towards safest nearby zone\n\n"
        "Stay safe. - RESQnet"
    )


def simulate_disaster_progression(region_record, starting_rainfall: int, steps: int = 5) -> list[dict]:
    """Generate simple progression steps by increasing rainfall over time."""
    progression = []
    for step in range(steps):
        simulated_rainfall = min(100, starting_rainfall + step * 10)
        assessment = assess_region(region_record, rainfall_level=simulated_rainfall)
        progression.append(
            {
                "Step": step + 1,
                "Simulated Rainfall": simulated_rainfall,
                "Risk Score": assessment.risk_score,
                "Risk Level": assessment.risk_level,
            }
        )
    return progression


def estimate_notified_users(affected_population: int) -> int:
    """Estimate how many users receive the SMS alert."""
    return max(5000, round(affected_population * 0.6))
