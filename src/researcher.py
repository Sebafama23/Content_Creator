import os
import pandas as pd
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Carga de credenciales
load_dotenv()

class Researcher:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")
        # Definimos el nicho técnico acordado
        self.query = "industrial process automation local LLMs 2026 Ollama Gemini"

    def fetch_trends(self):
        print(f"Investigando: {self.query}...")
        search = GoogleSearch({
            "q": self.query,
            "api_key": self.api_key,
            "num": 5,
            "tbs": "qdr:w"  # Filtro de última semana para máxima frescura
        })
        
        results = search.get_dict()
        organic = results.get("organic_results", [])
        
        # Estructuramos con Pandas para trazabilidad
        data = [
            {
                "title": r.get("title"),
                "link": r.get("link"),
                "snippet": r.get("snippet")
            } for r in organic
        ]
        
        return pd.DataFrame(data)

if __name__ == "__main__":
    researcher = Researcher()
    df = researcher.fetch_trends()
    
    if not df.empty:
        print("\n--- Resultados de Investigación ---")
        print(df[['title']].to_string())
        # Guardamos un backup temporal en el volumen
        df.to_json("data/latest_trends.json", orient="records")
    else:
        print("No se encontraron tendencias nuevas.")