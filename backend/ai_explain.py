import os
import json
from google import genai
from google.genai import types

def explain_route(route, weights, start_node=None, end_node=None):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback_explain(route, weights)

    client = genai.Client(api_key=api_key)
    
    speed, cost, carbon = weights
    
    prompt = f"""
    You are an expert logistics analyst at "Nexus-Zero".
    Provide a professional and concise explanation for why this specific route was selected.
    
    Route Details:
    - Origin: {start_node}
    - Destination: {end_node}
    - Transit Time: {route['totalTime']} days
    - Cost: ${route['totalCost']}k
    - Carbon Emissions: {route['totalCarbon']} kg
    
    User Priority Weights (0-100):
    - Speed: {speed}%
    - Cost: {cost}%
    - Carbon: {carbon}%
    
    Task:
    Provide 2-3 concise bullet points explaining the strategic rationale for this selection based on the weights.
    Focus on the trade-offs made (e.g., "Prioritized speed over cost due to high urgency").
    Return ONLY a JSON list of strings.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error calling Gemini in ai_explain: {e}")
        return _fallback_explain(route, weights)

def _fallback_explain(route, weights):
    reasons = []
    if weights[0] > weights[1] and weights[0] > weights[2]:
        reasons.append("AI prioritized speed")
    if weights[1] > weights[0] and weights[1] > weights[2]:
        reasons.append("AI prioritized cost efficiency")
    if weights[2] > weights[0] and weights[2] > weights[1]:
        reasons.append("AI minimized carbon footprint")
    if route["totalTime"] < 10:
        reasons.append("Fast route selected")
    if route["totalCarbon"] < 400:
        reasons.append("Eco-friendly route")
    return reasons