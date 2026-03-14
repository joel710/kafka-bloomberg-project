import asyncio
import json
import os
import threading
import time
import socket
import random
from contextlib import asynccontextmanager

from dotenv import load_dotenv
import yfinance as yf
import feedparser
from google import genai
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from kafka import KafkaConsumer, KafkaProducer
from pymongo import MongoClient

load_dotenv()

# --- CONFIGURATION ---
KAFKA_HOST = "kafka-4238954-kafka-2c1f.h.aivencloud.com"
KAFKA_PORT = 17498
KAFKA_URI = f"{KAFKA_HOST}:{KAFKA_PORT}"
KAFKA_FOLDER = "./"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MONGO_URI = os.getenv("MONGO_URI") or "mongodb+srv://jelise710_db_user:msi2025@dji.pzrvgeg.mongodb.net/?appName=dji"

ws_clients = []
KAFKA_CONNECTED = False
main_loop = None
last_intelligence = None 

def get_kafka_ip():
    try: return socket.gethostbyname(KAFKA_HOST)
    except: return KAFKA_HOST

def get_producer():
    global KAFKA_CONNECTED
    # Les fichiers sont présents dans le repo
    if not os.path.exists("ca.pem"):
        return None
    ip = get_kafka_ip()
    target = f"{ip}:{KAFKA_PORT}"
    try:
        p = KafkaProducer(
            bootstrap_servers=target,
            security_protocol="SSL",
            ssl_cafile="ca.pem",
            ssl_certfile="service.cert",
            ssl_keyfile="service.key",
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=5000,
            connection_timeout_ms=5000
        )
        KAFKA_CONNECTED = True
        print("✅ Kafka Connecté")
        return p
    except:
        KAFKA_CONNECTED = False
        return None

def send_to_ws(data):
    if main_loop and ws_clients:
        for client in ws_clients:
            try:
                asyncio.run_coroutine_threadsafe(client.send_json(data), main_loop)
            except: pass

# --- MOCK IA ---
def get_mock_analysis(headline):
    h = headline.lower()
    res = {"impact_gold": "NEUTRAL", "impact_eur": "NEUTRAL", "recommendation": "ATTENDRE", "reason": "Analyse technique standard.", "forecast": "Consolidation."}
    if any(w in h for w in ["fed", "rate", "inflation", "dollar", "usd"]):
        res = {"impact_gold": "BEARISH", "impact_eur": "BULLISH", "recommendation": "VENTE OR", "reason": "Renforcement du Dollar.", "forecast": "Pression sur l'Or."}
    elif any(w in h for w in ["war", "crisis", "conflict"]):
        res = {"impact_gold": "BULLISH", "impact_eur": "NEUTRAL", "recommendation": "ACHETER OR", "reason": "Valeur refuge.", "forecast": "Volatilité haussière."}
    return res

# --- WORKER MARKET ---
def market_worker():
    producer = get_producer()
    assets = {"GC=F": "XAU/USD", "EURUSD=X": "EUR/USD"}
    prices = {"XAU/USD": 2350.0, "EUR/USD": 1.0850}
    while True:
        for ticker, name in assets.items():
            try:
                t = yf.Ticker(ticker); real_p = t.fast_info['last_price']
                if real_p > 0: prices[name] = real_p
            except: pass
            jitter = random.uniform(-0.0008, 0.0008) if "EUR" in name else random.uniform(-0.4, 0.4)
            display_price = round(prices[name] + jitter, 4)
            msg = {"topic": "market-data", "asset": name, "price": display_price, "timestamp": int(time.time())}
            if KAFKA_CONNECTED and producer:
                try: producer.send("market-data", value=msg)
                except: pass
            send_to_ws(msg)
        if KAFKA_CONNECTED and producer: producer.flush()
        time.sleep(1)

# --- WORKER NEWS + AI ---
def ai_news_worker():
    global last_intelligence
    if not GOOGLE_API_KEY: return
    producer = get_producer()
    client = genai.Client(api_key=GOOGLE_API_KEY)
    model_id = "gemini-2.0-flash"
    RSS_SOURCES = ["https://www.cnbc.com/id/10000664/device/rss/rss.html", "https://www.yahoo.com/news/rss/finance"]
    seen = set()
    while True:
        for url in RSS_SOURCES:
            try:
                feed = feedparser.parse(url)
                if feed.entries:
                    entry = feed.entries[0]
                    if entry.title not in seen:
                        try:
                            prompt = f"Expert Macro. Analyse: '{entry.title}'. JSON: {{'impact_gold': 'B/B/N', 'impact_eur': 'B/B/N', 'recommendation': 'A/V/A', 'reason': 'short', 'forecast': 'sentiment'}}"
                            response = client.models.generate_content(model=model_id, contents=prompt)
                            txt = response.text.strip()
                            if "```json" in txt: txt = txt.split("```json")[1].split("```")[0]
                            analysis = json.loads(txt)
                        except:
                            analysis = get_mock_analysis(entry.title)
                        msg = {"topic": "analyzed-news", "headline": entry.title, "source": "Expert Flow", **analysis}
                        last_intelligence = msg
                        if KAFKA_CONNECTED and producer:
                            try: producer.send("analyzed-news", value=msg); producer.flush()
                            except: pass
                        send_to_ws(msg)
                        seen.add(entry.title)
                        time.sleep(90)
                        break
            except: continue
        time.sleep(30)

# --- WORKER DB ---
def db_worker():
    if not MONGO_URI: return
    try:
        client = MongoClient(MONGO_URI)
        db = client['dji']
        if KAFKA_CONNECTED:
            consumer = KafkaConsumer("market-data", "analyzed-news", bootstrap_servers=KAFKA_URI, security_protocol="SSL", 
                                     ssl_cafile="ca.pem", ssl_certfile="service.cert", 
                                     ssl_keyfile="service.key", value_deserializer=lambda x: json.loads(x.decode('utf-8')))
            for message in consumer:
                coll = db['market_history'] if message.topic == "market-data" else db['news_history']
                coll.insert_one(message.value)
    except: pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    global main_loop
    main_loop = asyncio.get_running_loop()
    threading.Thread(target=market_worker, daemon=True).start()
    threading.Thread(target=ai_news_worker, daemon=True).start()
    threading.Thread(target=db_worker, daemon=True).start()
    yield

app = FastAPI(title="Forex Sentinel", lifespan=lifespan)

@app.get("/")
async def get_dashboard():
    return FileResponse("index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_clients.append(websocket)
    if last_intelligence: await websocket.send_json(last_intelligence)
    try:
        while True: await websocket.receive_text()
    except: pass
    finally:
        if websocket in ws_clients: ws_clients.remove(websocket)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
