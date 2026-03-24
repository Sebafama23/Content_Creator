import os
import pandas as pd
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv()

DEFAULT_QUERY = "industrial process automation local LLMs 2026 Ollama Gemini"

class Researcher:
    def __init__(self):
        self.api_key = os.getenv("SERPAPI_KEY")

    def fetch_trends(self, topic: str = None):
        # Si no se pasa tema, usa el query por defecto
        query = topic if topic else DEFAULT_QUERY
        print(f"Investigando: {query}...")

        search = GoogleSearch({
            "q": query,
            "api_key": self.api_key,
            "num": 5,
            "tbs": "qdr:w"
        })
        results = search.get_dict()
        organic = results.get("organic_results", [])

        if not organic:
            raise ValueError(f"No se encontraron resultados para: {query}")

        data = [
            {
                "title": r.get("title"),
                "link": r.get("link"),
                "snippet": r.get("snippet")
            } for r in organic
        ]
        return pd.DataFrame(data)


if __name__ == "__main__":
    import sys
    researcher = Researcher()
    # Permite pasar tema por argumento: python researcher.py "mi tema"
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    df = researcher.fetch_trends(topic)
    if not df.empty:
        print("\n--- Resultados de Investigación ---")
        print(df[['title']].to_string())
        df.to_json("data/latest_trends.json", orient="records")
    else:
        print("No se encontraron tendencias nuevas.")