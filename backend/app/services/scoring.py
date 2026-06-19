"""Startup viability scoring engine."""

from typing import Any

from app.models.schemas import ScoreBreakdown


class ScoringEngine:
    """Evaluate startup viability across multiple dimensions."""

    def score(self, blueprint_data: dict[str, Any]) -> ScoreBreakdown:
        market = self._score_market(blueprint_data.get("market_research", {}))
        revenue = self._score_revenue(blueprint_data.get("business_strategy", {}))
        technical = self._score_technical(blueprint_data.get("technical_architecture", {}))
        scalability = self._score_scalability(blueprint_data.get("technical_architecture", {}))
        competition = self._score_competition(blueprint_data.get("competitor_analysis", {}))

        weights = {
            "market": 0.25,
            "revenue": 0.20,
            "technical": 0.20,
            "scalability": 0.15,
            "competition": 0.20,
        }
        competition_score = 100 - competition
        overall = (
            market * weights["market"]
            + revenue * weights["revenue"]
            + technical * weights["technical"]
            + scalability * weights["scalability"]
            + competition_score * weights["competition"]
        )

        return ScoreBreakdown(
            market_potential=round(market, 1),
            revenue_potential=round(revenue, 1),
            technical_feasibility=round(technical, 1),
            scalability=round(scalability, 1),
            competition_intensity=round(competition, 1),
            overall=round(overall, 1),
        )

    def _score_market(self, data: dict) -> float:
        content = data.get("content", {})
        score = 60.0
        if content.get("tam"):
            score += 10
        if content.get("sam"):
            score += 5
        if content.get("som"):
            score += 5
        if content.get("growth_rate"):
            score += 10
        if len(content.get("pain_points", [])) >= 3:
            score += 10
        return min(100, score)

    def _score_revenue(self, data: dict) -> float:
        content = data.get("content", {})
        score = 55.0
        if content.get("revenue_model"):
            score += 15
        if content.get("pricing_strategy"):
            score += 10
        if content.get("projected_arr_year1"):
            score += 10
        if content.get("unit_economics"):
            score += 10
        return min(100, score)

    def _score_technical(self, data: dict) -> float:
        content = data.get("content", {})
        score = 65.0
        if content.get("tech_stack"):
            score += 10
        if content.get("architecture"):
            score += 10
        if content.get("mvp_scope"):
            score += 10
        if content.get("deployment_strategy"):
            score += 5
        return min(100, score)

    def _score_scalability(self, data: dict) -> float:
        content = data.get("content", {})
        score = 60.0
        infra = content.get("infrastructure", {})
        if infra.get("cloud_provider"):
            score += 10
        if infra.get("scaling_strategy"):
            score += 15
        if content.get("architecture", {}).get("pattern") in ("microservices", "serverless", "event-driven"):
            score += 15
        return min(100, score)

    def _score_competition(self, data: dict) -> float:
        content = data.get("content", {})
        competitors = content.get("competitors", [])
        intensity = min(100, 30 + len(competitors) * 8)
        if content.get("differentiation"):
            intensity -= 15
        if content.get("market_gaps"):
            intensity -= 10
        return max(10, min(100, intensity))

    def compare_ideas(self, blueprints: list[dict[str, Any]]) -> list[dict]:
        comparisons = []
        for bp in blueprints:
            score = bp.get("score", {})
            comparisons.append({
                "id": bp.get("id"),
                "idea": bp.get("idea"),
                "overall_score": score.get("overall", 0) if isinstance(score, dict) else getattr(score, "overall", 0),
                "market_potential": score.get("market_potential", 0) if isinstance(score, dict) else getattr(score, "market_potential", 0),
                "revenue_potential": score.get("revenue_potential", 0) if isinstance(score, dict) else getattr(score, "revenue_potential", 0),
                "competition": score.get("competition_intensity", 0) if isinstance(score, dict) else getattr(score, "competition_intensity", 0),
                "technical_feasibility": score.get("technical_feasibility", 0) if isinstance(score, dict) else getattr(score, "technical_feasibility", 0),
                "build_difficulty": 100 - (score.get("technical_feasibility", 50) if isinstance(score, dict) else 50),
            })
        comparisons.sort(key=lambda x: x["overall_score"], reverse=True)
        return comparisons


scoring_engine = ScoringEngine()
