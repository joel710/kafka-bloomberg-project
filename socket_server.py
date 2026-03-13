import asyncio
import json
from fastapi import FastAPI, WebSocket
from kafka import KafkaConsumer
import threading

app = FastAPI()

# Configuration Kafka
folder = "./"
service_uri = "kafka-4238954-kafka-2c1f.h.aivencloud.com:17498"
topics = ["market-data", "analyzed-news"]

# Liste des clients WebSocket connectés
clients = []

def kafka_worker():
    """Consomme Kafka dans un thread séparé et envoie aux clients via asyncio"""
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=service_uri,
        security_protocol="SSL",
        ssl_cafile=folder + "ca.pem",
        ssl_certfile=folder + "service.cert",
        ssl_keyfile=folder + "service.key",
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest'
    )
    
    # On utilise une boucle d'événement pour communiquer avec FastAPI
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    for message in consumer:
        data = message.value
        data["topic"] = message.topic
        
        # Envoyer à tous les clients connectés
        for client in clients:
            try:
                # On utilise run_coroutine_threadsafe car on est dans un thread
                asyncio.run_coroutine_threadsafe(client.send_json(data), loop)
            except:
                clients.remove(client)

@app.on_event("startup")
async def startup_event():
    # Lancer Kafka dans un thread pour ne pas bloquer FastAPI
    thread = threading.Thread(target=kafka_worker, daemon=True)
    thread.start()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            # Maintenir la connexion ouverte
            await websocket.receive_text()
    except:
        clients.remove(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
