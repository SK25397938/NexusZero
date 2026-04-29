import osmnx as ox
import networkx as nx

def get_road_route(start_lat, start_lng, end_lat, end_lng):
    try:
        margin = 0.05

        north = max(start_lat, end_lat) + margin
        south = min(start_lat, end_lat) - margin
        east = max(start_lng, end_lng) + margin
        west = min(start_lng, end_lng) - margin

        if (north - south) > 2 or (east - west) > 2:
            return None

        G = ox.graph_from_bbox(
            (north, south, east, west),
            network_type="drive"
        )

        orig = ox.nearest_nodes(G, start_lng, start_lat)
        dest = ox.nearest_nodes(G, end_lng, end_lat)

        route = nx.shortest_path(G, orig, dest, weight="length")

        coords = []
        for node in route:
            coords.append([G.nodes[node]['y'], G.nodes[node]['x']])

        distance = nx.shortest_path_length(G, orig, dest, weight="length") / 1000

        return {
            "coords": coords,
            "distance": distance
        }

    except Exception as e:
        print("Road error:", e)
        return None