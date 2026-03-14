import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from loguru import logger

from V2.config import settings
from V2.services.kafka_producer import kafka_service
from V2.workers.market_worker import market_worker
from V2.workers.news_worker import ai_news_worker

app = FastAPI(title="Forex & Tech Sentinel V2", debug=settings.DEBUG)

# Servir les fichiers statiques (UI)
app.mount("/static", StaticFiles(directory="V2/static"), name="static")

class AppState:
    def __init__(self):
        self.ws_clients = set()

state = AppState()

async def broadcast(message: dict):
    """Envoie un message à tous les clients WebSocket connectés."""
    if not state.ws_clients:
        return
    
    disconnected = set()
    for client in state.ws_clients:
        try:
            await client.send_json(message)
        except Exception:
            disconnected.add(client)
    
    for client in disconnected:
        state.ws_clients.remove(client)

@app.get("/")
async def get_index():
    return FileResponse("V2/static/index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.ws_clients.add(websocket)
    logger.info(f"🔌 Nouveau client WS connecté. Total : {len(state.ws_clients)}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        state.ws_clients.remove(websocket)
        logger.info(f"🔌 Client déconnecté. Total : {len(state.ws_clients)}")

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Démarrage de Forex & Tech Sentinel V2...")
    
    # 1. Démarrer Kafka
    await kafka_service.start()
    
    # 2. Lancer les workers en arrière-plan
    asyncio.create_task(market_worker(broadcast))
    asyncio.create_task(ai_news_worker(broadcast))
    
    logger.info("✅ Workers initialisés en arrière-plan.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Arrêt des services...")
    await kafka_service.stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
