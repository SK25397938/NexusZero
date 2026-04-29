import math
import json
import os

nodes = {}
edges = []

dataset_path = os.path.join(os.path.dirname(__file__), "network_dataset.json")
if os.path.exists(dataset_path):
    with open(dataset_path, "r") as f:
        data = json.load(f)
        for n in data.get("nodes", []):
            nodes[n["id"]] = {"lat": n["lat"], "lng": n["lon"], "name": n["name"]}
        for e in data.get("edges", []):
            edges.append({
                "from": e["source"],
                "to": e["target"],
                "mode": e["mode"],
                "risk": e["risk_factor"],
                "cost": e.get("cost_index", 0.5) * 100,
                "co2": e.get("carbon_index", 0.5) * 100
            })
else:
    nodes = {
        "SHANGHAI": {"lat":31.2304,"lng":121.4737, "name": "Shanghai"},
        "SINGAPORE": {"lat":1.3521,"lng":103.8198, "name": "Singapore"},
        "DUBAI": {"lat":25.2048,"lng":55.2708, "name": "Dubai"},
        "ROTTERDAM": {"lat":51.9225,"lng":4.47917, "name": "Rotterdam"},
        "LONDON": {"lat":51.5074,"lng":-0.1278, "name": "London"},
        "HAMBURG": {"lat":53.5511,"lng":9.9937, "name": "Hamburg"},
        "NEWYORK": {"lat":40.7128,"lng":-74.0060, "name": "New York"},
        "CAPETOWN": {"lat":-33.9249,"lng":18.4241, "name": "Cape Town"},
        "COLON": {"lat":9.3542,"lng":-79.8993, "name": "Colon (Panama)"}
    }
    edges = [
        {"from":"SHANGHAI","to":"SINGAPORE","mode":"sea","risk":0.1},
        {"from":"SINGAPORE","to":"DUBAI","mode":"sea","risk":0.1},
        {"from":"DUBAI","to":"ROTTERDAM","mode":"sea","risk":0.1},
        {"from":"SHANGHAI","to":"CAPETOWN","mode":"sea","risk":0.3},
        {"from":"CAPETOWN","to":"ROTTERDAM","mode":"sea","risk":0.3},
        {"from":"NEWYORK","to":"ROTTERDAM","mode":"sea","risk":0.1},
        {"from":"COLON","to":"SINGAPORE","mode":"sea","risk":0.2},
        {"from":"SHANGHAI","to":"SINGAPORE","mode":"air","risk":0.1},
        {"from":"SHANGHAI","to":"NEWYORK","mode":"air","risk":0.2},
        {"from":"SHANGHAI","to":"CAPETOWN","mode":"air","risk":0.3},
        {"from":"SINGAPORE","to":"DUBAI","mode":"air","risk":0.1},
        {"from":"SINGAPORE","to":"CAPETOWN","mode":"air","risk":0.3},
        {"from":"DUBAI","to":"ROTTERDAM","mode":"air","risk":0.1},
        {"from":"DUBAI","to":"CAPETOWN","mode":"air","risk":0.3},
        {"from":"CAPETOWN","to":"ROTTERDAM","mode":"air","risk":0.3},
        {"from":"CAPETOWN","to":"NEWYORK","mode":"air","risk":0.3},
        {"from":"NEWYORK","to":"ROTTERDAM","mode":"air","risk":0.1},
        {"from":"NEWYORK","to":"COLON","mode":"air","risk":0.2},
        {"from":"COLON","to":"SHANGHAI","mode":"air","risk":0.2},
        {"from":"ROTTERDAM","to":"HAMBURG","mode":"air","risk":0.0},
        {"from":"ROTTERDAM","to":"LONDON","mode":"air","risk":0.0}
    ]


MAX_COST = 200
MAX_CO2 = 500
MAX_TIME = 30


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon/2)**2
    )
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def weighted_score(edge, w_speed, w_cost, w_carbon, storm):
    from_node = nodes[edge["from"]]
    to_node = nodes[edge["to"]]

    distance = haversine(
        from_node["lat"], from_node["lng"],
        to_node["lat"], to_node["lng"]
    )

    if edge["mode"] == "air":
        time = distance / 800
        cost = distance * 0.02
        co2 = distance * 0.09

    elif edge["mode"] == "sea":
        time = distance / 35
        cost = distance * 0.008
        co2 = distance * 0.02

    else:
        time = distance / 80
        cost = distance * 0.015
        co2 = distance * 0.05

    risk = edge["risk"]

    if storm:
        if edge["mode"] == "sea":
            risk *= 2.5
        if edge["from"] in ["DUBAI", "COLON"]:
            risk *= 3 

    score = (
        (cost / MAX_COST) * (w_cost / 100) +
        (co2 / MAX_CO2) * (w_carbon / 100) +
        (time / MAX_TIME) * (w_speed / 100)
    )

    return score * (1 + risk)


def find_route(start, end, w_speed, w_cost, w_carbon, storm):
    if start not in nodes or end not in nodes:
        return {"path": [], "totalCost": 0, "totalTime": 0, "totalCarbon": 0}

    dist = {node: float('inf') for node in nodes}
    prev = {n: None for n in nodes}
    visited = set()

    dist[start] = 0

    while True:
        curr = None
        curr_dist = float("inf")

        for n in nodes:
            if n not in visited and dist[n] < curr_dist:
                curr = n
                curr_dist = dist[n]

        if curr is None or curr == end:
            break

        visited.add(curr)

        for e in edges:
            if e["from"] == curr:
                neighbor = e["to"]
            elif e["to"] == curr:
                neighbor = e["from"]
            else:
                continue 

            if neighbor in visited:
                continue

            extra_cost = weighted_score(e, w_speed, w_cost, w_carbon, storm)
            alt = dist[curr] + extra_cost

            if alt < dist[neighbor]:
                dist[neighbor] = alt
                prev[neighbor] = (curr, e)

    path = []
    total_cost = total_time = total_carbon = 0
    node = end

    while prev[node]:
        p, e = prev[node]
        path.insert(0, {"from": e["from"], "to": e["to"], "mode": e["mode"]})

        from_node = nodes[e["from"]]
        to_node = nodes[e["to"]]

        distance = haversine(
            from_node["lat"], from_node["lng"],
            to_node["lat"], to_node["lng"]
        )

        if e["mode"] == "air":
            total_time += distance / 800
            total_cost += distance * 0.02
            total_carbon += distance * 0.09

        elif e["mode"] == "sea":
            total_time += distance / 35
            total_cost += distance * 0.008
            total_carbon += distance * 0.02

        else:
            total_time += distance / 80
            total_cost += distance * 0.015
            total_carbon += distance * 0.05

        node = p

    return {
        "path": path,
        "totalCost": round(total_cost, 2),
        "totalTime": round(total_time, 2),
        "totalCarbon": round(total_carbon, 2)
    }