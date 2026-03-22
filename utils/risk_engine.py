from dataclasses import dataclass


MAX_RAINFALL = 250
MAX_POPULATION_DENSITY = 5000
MAX_RIVER_LEVEL = 8
MAX_VULNERABILITY = 100


@dataclass
class RiskResult:
    risk_score: float
    risk_category: str
    affected_population: int
    affected_percentage: float
    factor_scores: dict


def normalize(value: float, maximum: float) -> float:
    """Convert a raw value to a 0-1 scale and keep it in bounds."""
    return max(0.0, min(value / maximum, 1.0))


def classify_risk(score: float) -> str:
    """Map a numeric score to a human-readable risk label."""
    if score >= 70:
        return "High Risk"
    if score >= 40:
        return "Medium Risk"
    return "Low Risk"


def estimate_affected_population(population: int, risk_category: str, risk_score: float) -> tuple[int, float]:
    """Estimate how many people may be affected using deterministic ranges."""
    if risk_category == "High Risk":
        affected_percentage = 0.30 + ((risk_score - 70) / 30) * 0.20
    elif risk_category == "Medium Risk":
        affected_percentage = 0.10 + ((risk_score - 40) / 30) * 0.15
    else:
        affected_percentage = 0.02 + (risk_score / 40) * 0.06

    affected_percentage = max(0.02, min(affected_percentage, 0.50))
    affected_population = round(population * affected_percentage)
    return affected_population, affected_percentage


def calculate_flood_risk(
    rainfall_mm: float,
    population_density: float,
    river_level_m: float,
    vulnerability_index: float,
    total_population: int,
) -> RiskResult:
    """Calculate flood risk using a weighted, explainable scoring model."""
    normalized_rainfall = normalize(rainfall_mm, MAX_RAINFALL)
    normalized_population_density = normalize(population_density, MAX_POPULATION_DENSITY)
    normalized_river_level = normalize(river_level_m, MAX_RIVER_LEVEL)
    normalized_vulnerability = normalize(vulnerability_index, MAX_VULNERABILITY)

    risk_score = (
        normalized_rainfall * 0.40
        + normalized_population_density * 0.20
        + normalized_river_level * 0.25
        + normalized_vulnerability * 0.15
    ) * 100

    risk_score = round(risk_score, 1)
    risk_category = classify_risk(risk_score)
    affected_population, affected_percentage = estimate_affected_population(
        total_population, risk_category, risk_score
    )

    factor_scores = {
        "Rainfall": round(normalized_rainfall * 100, 1),
        "Population Density": round(normalized_population_density * 100, 1),
        "River Level": round(normalized_river_level * 100, 1),
        "Vulnerability": round(normalized_vulnerability * 100, 1),
    }

    return RiskResult(
        risk_score=risk_score,
        risk_category=risk_category,
        affected_population=affected_population,
        affected_percentage=affected_percentage,
        factor_scores=factor_scores,
    )
