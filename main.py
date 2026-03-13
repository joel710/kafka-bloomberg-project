import asyncio
import json
import os
import threading
import time
import socket
import random
from contextlib import asynccontextmanager

import yfinance as yf
import feedparser
import google.generativeai as genai
import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from kafka import KafkaConsumer, KafkaProducer

# --- CONFIGURATION ---
KAFKA_HOST = "kafka-4238954-kafka-2c1f.h.aivencloud.com"
KAFKA_PORT = 17498
KAFKA_URI = f"{KAFKA_HOST}:{KAFKA_PORT}"
KAFKA_FOLDER = "./"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or "AIzaSyA9KxuYHEIHQx6jiciu7PA6g-EDwqPg_Gg"

ws_clients = []
KAFKA_CONNECTED = False
main_loop = None

# Message par défaut ultra-pro
last_intelligence = {
    "topic": "analyzed-news",
    "headline": "Connexion au flux financier établie",
    "source": "System",
    "impact_gold": "NEUTRAL",
    "impact_eur": "NEUTRAL",
    "reason": "En attente de la prochaine news majeure...",
    "forecast": "Analyse temps-réel activée."
}

def get_kafka_ip():
    try: return socket.gethostbyname(KAFKA_HOST)
    except: return KAFKA_HOST

def get_producer():
    global KAFKA_CONNECTED
    ip = get_kafka_ip()
    target = f"{ip}:{KAFKA_PORT}"
    try:
        p = KafkaProducer(
            bootstrap_servers=target,
            security_protocol="SSL",
            ssl_cafile=KAFKA_FOLDER + "ca.pem",
            ssl_certfile=KAFKA_FOLDER + "service.cert",
            ssl_keyfile=KAFKA_FOLDER + "service.key",
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            request_timeout_ms=5000,
            connection_timeout_ms=5000
        )
        KAFKA_CONNECTED = True
        return p
    except Exception as e:
        KAFKA_CONNECTED = False
        return None

def send_to_ws(data):
    if main_loop and ws_clients:
        for client in ws_clients:
            try:
                asyncio.run_coroutine_threadsafe(client.send_json(data), main_loop)
            except: pass

# --- WORKER MARKET ---
def market_worker():
    producer = get_producer()
    assets = {"GC=F": "XAU/USD", "EURUSD=X": "EUR/USD"}
    prices = {"XAU/USD": 2350.0, "EUR/USD": 1.0850}

    while True:
        for ticker, name in assets.items():
            try:
                t = yf.Ticker(ticker)
                real_p = t.fast_info['last_price']
                if real_p and real_p > 0: prices[name] = real_p
            except: pass
            
            jitter = random.uniform(-0.001, 0.001) if "EUR" in name else random.uniform(-0.4, 0.4)
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
    print("🧠 Worker AI & News: Start")
    producer = get_producer()
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Liste de flux RSS très robustes
    RSS_SOURCES = [
        "https://www.cnbc.com/id/10000664/device/rss/rss.html", # CNBC Finance
        "http://feeds.marketwatch.com/marketwatch/topstories/", # MarketWatch
        "https://www.yahoo.com/news/rss/finance" # Yahoo Finance
    ]
    
    seen = set()
    while True:
        news_found = False
        for url in RSS_SOURCES:
            try:
                feed = feedparser.parse(url)
                if feed.entries:
                    latest_entry = feed.entries[0]
                    
                    if latest_entry.title not in seen:
                        print(f"🔥 Analyse IA : {latest_entry.title[:60]}...")
                        
                        analysis = {"impact_gold": "NEUTRAL", "impact_eur": "NEUTRAL", "reason": "Analyse technique", "forecast": "Prudence recommandée."}
                        try:
                            prompt = f"Analyse l'impact financier (XAU et EUR) pour ce titre: {latest_entry.title}. Réponds en format JSON strict comme ceci: {{'impact_gold':'BULLISH/BEARISH/NEUTRAL', 'impact_eur':'BULLISH/BEARISH/NEUTRAL', 'reason':'une phrase courte', 'forecast':'une prévision courte'}}"
                            resp = model.generate_content(prompt)
                            analysis = json.loads(resp.text.strip().replace("```json", "").replace("```", ""))
                        except: pass
                        
                        msg = {"topic": "analyzed-news", "headline": latest_entry.title, "source": url.split('.')[1], **analysis}
                        last_intelligence = msg
                        
                        if KAFKA_CONNECTED and producer:
                            try: producer.send("analyzed-news", value=msg); producer.flush()
                            except: pass
                        
                        send_to_ws(msg)
                        seen.add(latest_entry.title)
                        news_found = True
                        break # On a trouvé une news, on arrête pour ce tour
            except: continue
            
        if not news_found:
            print("📡 Pas de nouvelle news, scan en cours...")
            
        time.sleep(20)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global main_loop
    main_loop = asyncio.get_running_loop()
    threading.Thread(target=market_worker, daemon=True).start()
    threading.Thread(target=ai_news_worker, daemon=True).start()
    yield

app = FastAPI(title="Forex Sentinel", lifespan=lifespan)

@app.get("/")
async def get_dashboard():
    return FileResponse("index.html")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_clients.append(websocket)
    if last_intelligence:
        await websocket.send_json(last_intelligence)
    try:
        while True:
            await websocket.receive_text()
    except: pass
    finally:
        if websocket in ws_clients: ws_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
