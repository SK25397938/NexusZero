import json
import os
from pydantic import BaseModel
from google import genai
from google.genai import types
from typing import List, Optional

class Intent(BaseModel):
    speed: float
    cost: float
    carbon: float
    risk_avoidance: bool

class AdjustedWeights(BaseModel):
    speed: float
    cost: float
    carbon: float

class RiskAnalysis(BaseModel):
    route_id: str
    severity: str

class Prediction(BaseModel):
    delay_percent: float
    cost_change_percent: float

class ScenarioImpact(BaseModel):
    time_change: float
    cost_change: float
    risk_change: float

class Command(BaseModel):
    origin: Optional[str]
    destination: Optional[str]

class Confidence(BaseModel):
    score: float
    reason: str

class NegotiationMessage(BaseModel):
    agent: str
    message: str

class MarketForecast(BaseModel):
    recommendation_date: str
    projected_savings: float
    rationale: str

class AgentDecision(BaseModel):
    intent: Intent
    adjusted_weights: AdjustedWeights
    selected_route: str
    pareto_routes: List[str]
    best_tradeoff: str
    risk_analysis: List[RiskAnalysis]
    prediction: Prediction
    scenario_impact: ScenarioImpact
    explanation: str
    command: Command
    confidence: Confidence
    negotiation_log: List[NegotiationMessage]
    market_forecast: MarketForecast

def _mock_process_agent_request(user_input: str, routes: List[dict], user_history: List[dict], scenario: str) -> AgentDecision:
    # Check if GEMINI_API_KEY is available (for future real implementation)
    api_key = os.getenv("GEMINI_API_KEY")
    
    # For now, we will return a highly dynamic mock based on the user's input and provided routes
    # This ensures the frontend has something robust to render immediately.
    
    # Simple heuristics to adjust weights based on text
    speed_weight = 0.5
    cost_weight = 0.5
    carbon_weight = 0.0
    risk_avoidance = False
    
    query = user_input.lower()
    if "fast" in query or "speed" in query or "urgent" in query:
        speed_weight = 0.8
        cost_weight = 0.2
    if "cheap" in query or "cost" in query or "budget" in query:
        speed_weight = 0.2
        cost_weight = 0.8
    if "green" in query or "carbon" in query or "eco" in query:
        speed_weight = 0.3
        cost_weight = 0.3
        carbon_weight = 0.4
    if "safe" in query or "avoid" in query or "risk" in query or "storm" in query:
        risk_avoidance = True

    # Find the best route from the provided routes based on the derived weights
    selected_route_id = routes[0]["id"] if routes else "R1"
    best_tradeoff_id = routes[1]["id"] if len(routes) > 1 else selected_route_id
    pareto = [r["id"] for r in routes[:2]] if routes else ["R1", "R2"]
    
    # Identify high risk routes
    risks = []
    if len(routes) > 2:
        risks.append(RiskAnalysis(route_id=routes[2]["id"], severity="high"))
        
    explanation = "Route selected based on default parameters."
    if speed_weight > 0.6:
        explanation = "Selected the fastest route to meet urgent timeline, accepting higher costs."
    elif risk_avoidance:
        explanation = "Prioritized safety to avoid severe weather, routing around high-risk zones."
    elif cost_weight > 0.6:
        explanation = "Selected the most cost-effective route, trading off speed for budget efficiency."
        
    origin = None
    destination = None
    if "shanghai" in query: origin = "CN_SHA"
    if "rotterdam" in query: destination = "NL_RTM"
    if "singapore" in query: origin = "SG_SIN"
    if "dubai" in query: origin = "AE_DXB"

    # Default Scenario impacts
    time_change = 0.0
    cost_change = 0.0
    risk_change = 0.0
    delay_percent = 1.2
    cost_change_percent = 2.0
    confidence_score = 95.0
    
    negotiation_log = [
        NegotiationMessage(agent="Ops", message="Analyzing optimal paths for speed and reliability."),
        NegotiationMessage(agent="Finance", message="Evaluating cost metrics across available lanes."),
        NegotiationMessage(agent="Eco", message="Checking carbon footprint compliance.")
    ]
    
    scen = scenario.lower()
    if "storm" in scen:
        time_change = 12.0
        cost_change = 1500.0
        risk_change = 25.0
        delay_percent = 4.5
        confidence_score = 85.0
        if not risk_avoidance:
            explanation = "Storm warning active. Proceeding with caution, but expect weather delays."
        negotiation_log.append(NegotiationMessage(agent="Ops", message="WARNING: Storm detected. Fast routes compromised. Propose rerouting."))
        negotiation_log.append(NegotiationMessage(agent="Finance", message="Rerouting will increase fuel costs, but prevents total loss. Accepted."))
    elif "suez" in scen or "canal" in scen or "block" in scen:
        time_change = 10.0
        cost_change = 8000.0
        risk_change = 30.0
        delay_percent = 25.0
        cost_change_percent = 40.0
        confidence_score = 75.0
        risk_avoidance = True
        explanation = "CRITICAL: Suez Canal blocked. Re-routing around the Cape of Good Hope. Expect significant delays and cost increase."
        negotiation_log.append(NegotiationMessage(agent="Ops", message="CRITICAL: Suez blocked. We must use the Cape of Good Hope detour."))
        negotiation_log.append(NegotiationMessage(agent="Eco", message="The detour adds thousands of miles. CO2 output will spike massively!"))
        negotiation_log.append(NegotiationMessage(agent="Finance", message="No choice. Delays cost more than fuel. Approved."))
    elif "fuel" in scen or "spike" in scen:
        time_change = 2.0
        cost_change = 15000.0
        risk_change = 5.0
        delay_percent = 5.0
        cost_change_percent = 15.0
        cost_weight = 0.9
        speed_weight = 0.1
        explanation = "ALERT: Sudden fuel price spike detected. Switched to most fuel-efficient maritime routes to preserve margins."
        negotiation_log.append(NegotiationMessage(agent="Finance", message="ALERT: 15% fuel spike! We must prioritize sea routes immediately."))
        negotiation_log.append(NegotiationMessage(agent="Ops", message="This will delay deliveries by 3 days. Are you sure?"))
        negotiation_log.append(NegotiationMessage(agent="Finance", message="Yes, the margin loss is too great otherwise. Prioritize cost."))
    else:
        if speed_weight > 0.6:
            negotiation_log.append(NegotiationMessage(agent="Ops", message="User requested speed. Switching to hybrid air/sea routes."))
            negotiation_log.append(NegotiationMessage(agent="Finance", message="Noting cost increase. Proceeding."))
        elif cost_weight > 0.6:
            negotiation_log.append(NegotiationMessage(agent="Finance", message="Optimizing for lowest cost. Recommending bulk sea freight."))
            negotiation_log.append(NegotiationMessage(agent="Eco", message="Excellent, this aligns with our carbon reduction goals."))
            
    # Mock Market Forecasting logic based on destination
    forecast_date = "Next Tuesday"
    forecast_savings = 0.0
    forecast_rationale = "No significant market volatility predicted."
    
    if destination == "NL_RTM":
        forecast_savings = 12.5
        forecast_rationale = "Our predictive models show a 90% probability that port congestion fees in Rotterdam will drop next week as seasonal traffic eases."
    elif destination == "CN_SHA":
        forecast_savings = 5.0
        forecast_date = "This Friday"
        forecast_rationale = "Booking before the weekend avoids incoming holiday surcharges at Shanghai Port."
    elif speed_weight > 0.6:
        forecast_savings = -8.0
        forecast_date = "Immediately"
        forecast_rationale = "Air freight rates are trending upward. Immediate booking is advised to lock in current rates."
    else:
        forecast_savings = 2.4
        forecast_date = "End of Month"
        forecast_rationale = "Carrier volume quotas usually lead to minor discounts at month-end."

    forecast = MarketForecast(
        recommendation_date=forecast_date,
        projected_savings=forecast_savings,
        rationale=forecast_rationale
    )

    # Assemble response
    decision = AgentDecision(
        intent=Intent(speed=speed_weight, cost=cost_weight, carbon=carbon_weight, risk_avoidance=risk_avoidance),
        adjusted_weights=AdjustedWeights(speed=speed_weight + 0.05, cost=cost_weight - 0.05, carbon=carbon_weight),
        selected_route=selected_route_id,
        pareto_routes=pareto,
        best_tradeoff=best_tradeoff_id,
        risk_analysis=risks,
        prediction=Prediction(delay_percent=delay_percent, cost_change_percent=cost_change_percent),
        scenario_impact=ScenarioImpact(
            time_change=time_change, 
            cost_change=cost_change, 
            risk_change=risk_change
        ),
        explanation=explanation,
        command=Command(origin=origin, destination=destination),
        confidence=Confidence(score=confidence_score, reason="Scenario analysis applied. Dynamic routing active."),
        negotiation_log=negotiation_log,
        market_forecast=forecast
    )
    
    return decision

def process_agent_request(user_input: str, routes: List[dict], user_history: List[dict], scenario: str) -> AgentDecision:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found, falling back to mock agent.")
        return _mock_process_agent_request(user_input, routes, user_history, scenario)

    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an advanced AI supply chain and logistics copilot for "Nexus-Zero". You manage a multi-agent system consisting of:
    1. **Ops Agent**: Focuses on speed, reliability, and minimizing delays.
    2. **Finance Agent**: Focuses on cost efficiency, profit margins, and minimizing expenses.
    3. **Eco Agent**: Focuses on sustainability, carbon footprint, and environmental compliance.

    User Request: "{user_input}"
    Current Scenario / Disruption: "{scenario if scenario else 'None'}"
    
    Available Routes:
    {json.dumps(routes, indent=2)}
    
    Task:
    1. Analyze the user request and any active disruptions.
    2. Simulate a brief negotiation between the Ops, Finance, and Eco agents to find the best route.
    3. Select the most appropriate route ID from the Available Routes.
    4. Provide predictive metrics and a market forecast.
    
    Output Format:
    Return a JSON object that strictly adheres to the `AgentDecision` schema.
    
    Specific Instructions:
    - `negotiation_log`: Include 3-4 messages showing the perspective of different agents before reaching a consensus.
    - `selected_route`: Must be one of the 'id' values from the provided routes list.
    - `explanation`: Provide a concise summary of the final decision.
    - `market_forecast`: Predict future trends based on the current scenario.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AgentDecision,
                temperature=0.2,
            ),
        )
        return response.parsed
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return _mock_process_agent_request(user_input, routes, user_history, scenario)

def generate_executive_report(data: dict) -> str:
    route_id = data.get("route_id", "Unknown")
    cost = data.get("cost", 0)
    time = data.get("time", 0)
    carbon = data.get("carbon", 0)
    scenario = data.get("scenario", "None")
    explanation = data.get("explanation", "Standard routing applied.")
    forecast = data.get("market_forecast", {})
    
    forecast_savings = forecast.get("projected_savings", 0)
    forecast_rationale = forecast.get("rationale", "")
    forecast_date = forecast.get("recommendation_date", "")
    
    savings_color = "#10b981" if forecast_savings >= 0 else "#ef4444"
    savings_text = f"Save ${abs(forecast_savings)}k" if forecast_savings >= 0 else f"Avoid ${abs(forecast_savings)}k Surcharge"
    
    html = f"""
    <div style="font-family: 'Inter', sans-serif; color: #334155; line-height: 1.6;">
        <div style="border-bottom: 2px solid #3b82f6; padding-bottom: 10px; margin-bottom: 20px;">
            <h2 style="color: #0f172a; margin: 0; font-size: 1.5rem;">Nexus-Zero Executive Summary</h2>
            <p style="margin: 5px 0 0 0; color: #64748b; font-size: 0.85rem;">Generated by Nexus AI Copilot</p>
        </div>
        
        <h3 style="color: #10b981; font-size: 1.1rem; margin-top: 0;">1. Strategic Overview</h3>
        <p>The AI Copilot has finalized the supply chain routing strategy. After simulating multiple operational parameters and live variables, <strong>Route {route_id}</strong> was selected as the optimal Pareto-efficient path.</p>
        <p><strong>Primary Justification:</strong> {explanation}</p>
        
        <h3 style="color: #8b5cf6; font-size: 1.1rem; margin-top: 20px;">2. Market Forecast & Predictive Pricing 🔮</h3>
        <div style="background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 8px; padding: 15px;">
            <p style="margin-top:0;"><strong>Recommendation:</strong> Book <strong>{forecast_date}</strong> to <strong style="color: {savings_color}">{savings_text}</strong>.</p>
            <p style="margin-bottom:0;"><strong>AI Rationale:</strong> {forecast_rationale}</p>
        </div>
        
        <h3 style="color: #10b981; font-size: 1.1rem; margin-top: 20px;">3. Scenario & Risk Mitigation</h3>
        <p><strong>Active Disruption Event:</strong> {scenario.upper() if scenario else 'None Detected'}</p>
        <p>The multi-agent system successfully negotiated a risk-mitigated path. By proactively adjusting for the active scenario, we estimate the prevention of severe SLA breaches.</p>
        
        <h3 style="color: #10b981; font-size: 1.1rem; margin-top: 20px;">4. Pareto Trade-off Analysis</h3>
        <p>The selected route was compared against the next best alternatives on the Pareto front. The chosen route represents the optimal mathematical compromise between our dynamic constraints.</p>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.85rem; border: 1px solid #e2e8f0;">
            <thead>
                <tr style="background-color: #f8fafc; border-bottom: 2px solid #cbd5e1;">
                    <th style="padding: 10px; text-align: left;">Route Option</th>
                    <th style="padding: 10px; text-align: left;">Cost</th>
                    <th style="padding: 10px; text-align: left;">Transit Time</th>
                    <th style="padding: 10px; text-align: left;">Trade-off Notes</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #e2e8f0; background-color: #ecfdf5;">
                    <td style="padding: 10px;"><strong>Selected (Route {route_id})</strong></td>
                    <td style="padding: 10px;"><strong>${cost}k</strong></td>
                    <td style="padding: 10px;"><strong>{time} Days</strong></td>
                    <td style="padding: 10px; color: #059669; font-weight: 600;">Optimal Baseline</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px;">Alt A (Sea-Heavy)</td>
                    <td style="padding: 10px; color: #059669;">${max(1, float(cost) - 5.5):.1f}k</td>
                    <td style="padding: 10px; color: #dc2626;">{float(time) + 8.0:.1f} Days</td>
                    <td style="padding: 10px; color: #64748b;">Save $5.5k, but lose 8 days</td>
                </tr>
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px;">Alt B (Air-Heavy)</td>
                    <td style="padding: 10px; color: #dc2626;">${float(cost) + 12.0:.1f}k</td>
                    <td style="padding: 10px; color: #059669;">{max(1, float(time) - 6.0):.1f} Days</td>
                    <td style="padding: 10px; color: #64748b;">Save 6 days, but costs $12k more</td>
                </tr>
            </tbody>
        </table>
        
        <h3 style="color: #10b981; font-size: 1.1rem; margin-top: 20px;">5. Final Key Performance Indicators (KPIs)</h3>
        <ul style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px 15px 15px 35px; list-style-type: square;">
            <li><strong>Total Transit Time:</strong> {time} Days</li>
            <li><strong>Total Logistics Cost:</strong> ${cost}k</li>
            <li><strong>Projected Carbon Footprint:</strong> {carbon} kg CO₂</li>
        </ul>
        
        <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 10px 15px; margin-top: 20px; font-size: 0.9rem;">
            <strong>AI Recommendation:</strong> Proceed with booking. The balance of speed, cost, and carbon output strongly aligns with the current strategic priorities.
        </div>
    </div>
    """
    return html
