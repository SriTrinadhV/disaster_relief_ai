import math


def calculate_resource_recommendations(affected_population: int) -> dict:
    """Return simple, demo-friendly resource recommendations."""
    rescue_teams = max(1, math.ceil(affected_population / 5000))
    food_packets = math.ceil(affected_population * 1.0)
    medical_kits = max(1, math.ceil(affected_population / 20))
    temporary_shelters = max(1, math.ceil(affected_population / 250))

    return {
        "rescue_teams": rescue_teams,
        "food_packets": food_packets,
        "medical_kits": medical_kits,
        "temporary_shelters": temporary_shelters,
    }
