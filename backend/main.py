import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from ml_model import predict_weights
from graph import find_route, nodes, edges
from weather import check_storm
from ai_explain import explain_route
from agent import process_agent_request, generate_executive_report

load_dotenv()


def generate_routes(start, end, storm):
    weight_sets = [
        (100, 0, 0),
        (0, 100, 0),
        (0, 0, 100),
        (50, 50, 0),
        (50, 0, 50),
        (0, 50, 50),
        (33, 33, 34),
        (70, 20, 10),
        (20, 70, 10),
        (20, 10, 70)
    ]

    routes = []

    for w in weight_sets:
        r = find_route(start, end, w[0], w[1], w[2], storm)
        if r["path"]:
            routes.append(r)

    return routes


def pareto_filter(routes):
    pareto = []

    for r in routes:
        dominated = False
        for other in routes:
            if (
                other["totalCost"] <= r["totalCost"] and
                other["totalTime"] <= r["totalTime"] and
                other["totalCarbon"] <= r["totalCarbon"] and
                other != r
            ):
                if (
                    other["totalCost"] < r["totalCost"] or
                    other["totalTime"] < r["totalTime"] or
                    other["totalCarbon"] < r["totalCarbon"]
                ):
                    dominated = True
                    break
        if not dominated:
            pareto.append(r)

    return pareto


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RouteRequest(BaseModel):
    start: str
    end: str
    speed: int
    cost: int
    carbon: int
    storm: bool

class AgentRequest(BaseModel):
    user_input: str
    start: str
    end: str
    storm: bool
    disruption_event: str = ""

class ReportRequest(BaseModel):
    route_id: str
    cost: float
    time: float
    carbon: float
    scenario: str
    explanation: str
    market_forecast: dict = {}


@app.get("/graph_data")
def get_graph_data():
    return {
        "nodes": nodes,
        "edges": edges
    }

@app.post("/optimize")
def optimize(req: RouteRequest):
    storm_detected = check_storm(25.2, 55.2)
    storm = req.storm or storm_detected

    routes = generate_routes(req.start, req.end, storm)
    pareto = pareto_filter(routes)

    s, c, co = predict_weights(
        req.speed,
        req.cost,
        req.carbon,
        storm
    )

    selected = find_route(
        req.start,
        req.end,
        s,
        c,
        co,
        storm
    )

    explanation = explain_route(selected, (s, c, co), req.start, req.end)

    return {
        "selected": selected,
        "pareto": pareto,
        "all": routes,
        "explanation": explanation,
        "aiWeights": {
            "speed": round(s, 1),
            "cost": round(c, 1),
            "carbon": round(co, 1)
        },
        "stormDetected": storm_detected
    }

@app.post("/agent_decision")
def agent_decision(req: AgentRequest):
    storm_detected = check_storm(25.2, 55.2)
    storm = req.storm or storm_detected

    routes = generate_routes(req.start, req.end, storm)
    
    # Format routes for the agent
    agent_routes = []
    for i, r in enumerate(routes):
        agent_routes.append({
            "id": f"R{i+1}",
            "time": r["totalTime"],
            "cost": r["totalCost"],
            "carbon": r["totalCarbon"],
            "risk": r["totalRisk"] if "totalRisk" in r else 0.5
        })

    decision = process_agent_request(
        user_input=req.user_input,
        routes=agent_routes,
        user_history=[{"speed": 0.5, "cost": 0.5, "carbon": 0.0}],
        scenario=req.disruption_event if req.disruption_event else ("storm" if storm else "none")
    )
    
    # The selected route is returned by ID "R1", "R2", etc.
    # Map it back to the actual route object
    selected_idx = int(decision.selected_route[1:]) - 1 if decision.selected_route.startswith("R") and decision.selected_route[1:].isdigit() else 0
    if selected_idx >= len(routes): selected_idx = 0
    selected = routes[selected_idx]
    
    return {
        "agent_decision": decision.dict(),
        "selected": selected,
        "all": routes,
        "stormDetected": storm_detected
    }

@app.post("/generate_report")
def create_report(req: ReportRequest):
    html_report = generate_executive_report(req.dict())
    return {"html": html_report}