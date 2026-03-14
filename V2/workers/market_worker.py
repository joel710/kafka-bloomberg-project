import asyncio
import time
import random
import yfinance as yf
from loguru import logger
from V2.config import settings
from V2.services.kafka_producer import kafka_service

async def market_worker(broadcast_fn):
    logger.info("📈 Démarrage du Market Worker V2 (Multi-Assets)")
    
    # Cache local pour les derniers prix
    prices = {name: 0.0 for name in settings.ASSETS.values()}

    while True:
        for ticker, name in settings.ASSETS.items():
            try:
                # Récupération asynchrone simulée (yfinance n'est pas natif async)
                loop = asyncio.get_event_loop()
                stock = yf.Ticker(ticker)
                real_p = await loop.run_in_executor(None, lambda: stock.fast_info['last_price'])
                
                if real_p > 0:
                    prices[name] = real_p
                
                # Ajout d'un petit jitter pour le "live"
                jitter = random.uniform(-0.0001, 0.0001) * prices[name]
                display_price = round(prices[name] + jitter, 4 if "EUR" in name else 2)
                
                msg = {
                    "topic": "market-data",
                    "asset": name,
                    "price": display_price,
                    "timestamp": int(time.time())
                }
                
                # Envoi Kafka + Broadcast WS
                await kafka_service.send("market-data", msg)
                await broadcast_fn(msg)
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur fetch {ticker}: {e}")
            
            await asyncio.sleep(0.5) # Intervalle entre chaque asset
        
        await asyncio.sleep(1)
