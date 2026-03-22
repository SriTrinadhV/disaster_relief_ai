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


def assess_region(region_record) -> RegionAssessment:
    """Build a simple disaster assessment from a selected dataset row."""
    risk_level = str(region_record["risk_level"])
    disaster_type = str(region_record["disaster_type"])
    population = int(region_record["population"])
    risk_score = RISK_SCORE_MAP[risk_level]
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
    return (
        "RESQnet ALERT\n\n"
        f"Disaster: {assessment.disaster_type}\n"
        f"Location: {assessment.region}\n"
        f"Risk Level: {assessment.risk_level.upper()}\n\n"
        "Severe conditions expected\n\n"
        f"Safe Zone: {assessment.safe_zone_type}\n"
        "Route: Move towards safest nearby zone\n\n"
        "Stay safe. - RESQnet"
    )
