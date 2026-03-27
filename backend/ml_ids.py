import numpy as np
from sklearn.ensemble import IsolationForest

# store traffic features
traffic_data = []

# train anomaly detector
model = IsolationForest(contamination=0.02)

trained = False


def add_packet_feature(packet_size, protocol, port):

    global trained

    feature = [
        packet_size,
        protocol,
        port
    ]

    traffic_data.append(feature)

    if len(traffic_data) > 100 and not trained:
        model.fit(traffic_data)
        trained = True


def detect_anomaly(packet_size, protocol, port):

    if not trained:
        return False

    sample = np.array([[packet_size, protocol, port]])

    prediction = model.predict(sample)

    if prediction[0] == -1:
        return True

    return False