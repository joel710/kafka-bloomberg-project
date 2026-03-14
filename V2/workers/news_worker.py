import asyncio
import json
import feedparser
from loguru import logger
from google import genai
from V2.config import settings
from V2.services.kafka_producer import kafka_service

async def ai_news_worker(broadcast_fn):
    logger.info("🧠 Worker IA Sentinel V2 Actif (Tech & Macro focus)")
    
    if not settings.GOOGLE_API_KEY:
        logger.error("❌ Pas de clé Google API. Arrêt du News Worker.")
        return

    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    model_id = "gemini-2.0-flash"
    
    seen_headlines = set()

    while True:
        for url in settings.RSS_SOURCES:
            try:
                # Utilisation d'un exécuteur pour feedparser (qui est bloquant)
                loop = asyncio.get_event_loop()
                feed = await loop.run_in_executor(None, lambda: feedparser.parse(url))
                
                if feed.entries:
                    entry = feed.entries[0]
                    if entry.title not in seen_headlines:
                        logger.info(f"✨ Nouvelle analyse : {entry.title[:60]}...")
                        
                        prompt = f"""
                        Expert Marchés & Tech. Analyse cette news: '{entry.title}'.
                        Considère l'impact sur l'IA (NVDA, MSFT) et le Forex (EUR/USD).
                        Réponds UNIQUEMENT en JSON: 
                        {{
                            'recommendation': 'ACHETER NVDA|VENTE NVDA|ATTENDRE|LONG EUR|SHORT EUR', 
                            'reason': 'explication courte', 
                            'impact_tech': 'BULLISH|BEARISH|NEUTRAL'
                        }}
                        """
                        
                        try:
                            response = await loop.run_in_executor(None, lambda: client.models.generate_content(model=model_id, contents=prompt))
                            txt = response.text.strip()
                            if "```json" in txt: txt = txt.split("```json")[1].split("```")[0]
                            analysis = json.loads(txt)
                        except Exception as e:
                            logger.warning(f"⚠️ Erreur Gemini (Mode secours): {e}")
                            analysis = {"recommendation": "OBSERVATION", "reason": "Analyse technique standard nécessaire.", "impact_tech": "NEUTRAL"}
                        
                        msg = {
                            "topic": "analyzed-news",
                            "headline": entry.title,
                            "source": url.split('.')[1] if '.' in url else "RSS",
                            **analysis
                        }
                        
                        await kafka_service.send("analyzed-news", msg)
                        await broadcast_fn(msg)
                        seen_headlines.add(entry.title)
                        
                        if len(seen_headlines) > 100: seen_headlines.pop() # Gestion de mémoire
                        
            except Exception as e:
                logger.error(f"⚠️ Erreur News Worker (RSS {url}): {e}")
            
            await asyncio.sleep(10) # Pause entre les sources RSS
        
        await asyncio.sleep(60) # Rafraîchissement global toutes les minutes
