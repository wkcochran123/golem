import time
import numpy as np
from concept_net import ConceptNet

model = ConceptNet(5120,152000)

import requests

def get_mood():
    try:
        response = requests.get("http://192.168.68.79:8000/mood", timeout=2)
        response.raise_for_status()
        vals = response.text.strip().split(",")
        return int (mood),int(mood_id)
    except Exception as e:
        print(f"Error fetching mood: {e}")
        return (0,-1)  # fallback mood

def flush_last_prompt(mood):
    for neuron in neurons:
        model.backprop_reward(neuron,mood)

def apply_row(data,mood):
    token = data["token"]
    print (token)
    vector = np.array(data["vector"], dtype=np.float32).reshape(1, -1)
    neurons.append(vector)
    model.predict(vector)[0].tofile("/Users/williamcochran/Code/golem/python/logits.data")


log_path = "/Users/williamcochran/Code/golem/concept_nodes.log"
neurons=[]

with open(log_path, "r") as f:
    f.seek(0, 2)  # Seek to end

    mood = 0
    mood_id = -1
    ctr = 0

    while True:
        ctr = ctr + 1
        if ctr == 1000:
            ctr = 0
            old_mood_id = mood_id
            mood,mood_id = get_mood()
            if old_mood_id != mood_id:
                flush_last_promp(mood)
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue

        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        token = parts[0]
        try:
            vector = [float(x) for x in parts[1:]]
            apply_row({"token": token, "vector": vector},mood)
        except ValueError:
            print("Parse error:", line)


