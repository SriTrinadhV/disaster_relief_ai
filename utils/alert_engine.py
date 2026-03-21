
def generate_alert(disaster_type: str, rainfall_mm: float, river_level_m: float, risk_category: str) -> dict:
    """Generate a simple early warning message based on current inputs."""
    disaster_label = disaster_type.title()

    if disaster_type.lower() != "flood":
        return {
            "severity": "info",
            "title": f"{disaster_label} support coming soon",
            "message": "This demo is optimized for flood analysis. Other disasters are placeholders for future expansion.",
        }

    if rainfall_mm >= 170 and river_level_m >= 5.8:
        return {
            "severity": "error",
            "title": "High flood risk in next 24 hours",
            "message": "Heavy rainfall and dangerous river conditions suggest immediate preparedness, evacuation planning, and response team activation.",
        }

    if risk_category == "High Risk":
        return {
            "severity": "error",
            "title": "Severe conditions detected",
            "message": "Overall flood indicators are elevated. Local authorities should prepare rapid response resources and notify vulnerable communities.",
        }

    if rainfall_mm >= 120 or river_level_m >= 4.8 or risk_category == "Medium Risk":
        return {
            "severity": "warning",
            "title": "Moderate flood conditions detected",
            "message": "Water levels and rainfall trends should be monitored closely. Standby teams and medical support are recommended.",
        }

    return {
        "severity": "success",
        "title": "No immediate severe flood threat detected",
        "message": "Current inputs suggest manageable conditions, but routine monitoring should continue.",
    }
