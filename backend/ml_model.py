from sklearn.ensemble import RandomForestRegressor
import numpy as np

X = [
    [50, 50, 50, 0],
    [80, 10, 10, 0],
    [10, 80, 10, 0],
    [10, 10, 80, 0],
    [40, 30, 30, 1],
    [30, 40, 30, 1],
    [30, 30, 40, 1]
]

y = [
    [50, 50, 50],
    [80, 10, 10],
    [10, 80, 10],
    [10, 10, 80],
    [20, 20, 60],
    [30, 50, 20],
    [40, 30, 30]
]

model = RandomForestRegressor(random_state=42)
model.fit(X, y)


def predict_weights(speed, cost, carbon, storm):
    pred = model.predict([[speed, cost, carbon, int(storm)]])[0]

    s, c, co = np.maximum(pred, 0)

    total = s + c + co

    if total == 0:
        return 33.3, 33.3, 33.4

    s = (s / total) * 100
    c = (c / total) * 100
    co = (co / total) * 100

    return round(s, 1), round(c, 1), round(co, 1)