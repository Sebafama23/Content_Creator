import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class LocalContentGenerator:
    def __init__(self):
        self.ollama_url = f"{os.getenv('OLLAMA_BASE_URL')}/api/generate"
        self.model = os.getenv("OLLAMA_MODEL")

    def _call_ollama(self, prompt):
        try:
            response = requests.post(self.ollama_url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }, timeout=120)  # ✅ 120s — modelos locales pueden ser lentos
            response.raise_for_status()
            
            result = response.json().get('response', '').strip()
            
            if not result:
                raise ValueError("Ollama devolvió una respuesta vacía.")
            
            return result
        
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"No se pudo conectar a Ollama en {self.ollama_url}. ¿Está corriendo?")
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama tardó más de 120 segundos. Intentá con un modelo más liviano.")
        except Exception as e:
            raise RuntimeError(f"Error al llamar a Ollama: {e}")

    def generate_full_content(self, raw_data):
        print(f"--- Generando contenido localmente con {self.model} ---")
        
        master_prompt = f"""Sos un profesional de MLOps e IA Industrial escribiendo en LinkedIn.
Analizá estos datos: {raw_data}

Escribí un post de LinkedIn en español, directamente, sin títulos, sin etiquetas, sin explicaciones previas ni frases introductorias como "Aquí tienes", "Claro que sí" o "Por supuesto".

El post debe:
- Arrancar directo con el hook, sin preámbulo de ningún tipo.
- Sonar como escrito por un humano, no por una IA.
- Tono profesional, directo y resolutivo.
- Gancho inicial potente en la primera línea.
- Desarrollo con contexto real de automatización e IA industrial.
- Cierre con una pregunta o llamada a la acción concreta.
- Terminar con exactamente 3 hashtags relevantes.
- Máximo 1300 caracteres en total.

Escribí solo el post. Nada más. Sin comentarios, sin explicaciones al final."""
        
        return self._call_ollama(master_prompt)

    def refine_content(self, previous_post, user_feedback, trends):
        """Método separado para refinamiento — contexto más claro para el modelo."""
        print(f"--- Refinando contenido con {self.model} ---")
        
        refine_prompt = f"""Sos un profesional de MLOps e IA Industrial editando un post de LinkedIn.

Post actual:
{previous_post}

Correcciones solicitadas:
{user_feedback}

Contexto de tendencias (para mantener relevancia):
{trends}

Aplicá las correcciones manteniendo el tono humano y profesional.
Devolvé solo el post corregido. Sin explicaciones, sin comentarios."""

        return self._call_ollama(refine_prompt)

if __name__ == "__main__":
    trends_path = "data/latest_trends.json"
    if not os.path.exists(trends_path):
        print("Error: No se encontró el archivo de tendencias.")
        exit()

    with open(trends_path, "r") as f:
        trends = json.load(f)
    
    gen = LocalContentGenerator()
    final_post = gen.generate_full_content(trends)
    
    with open("data/final_post.txt", "w", encoding="utf-8") as f:
        f.write(final_post)
    
    print("\n✅ Post generado localmente en data/final_post.txt")