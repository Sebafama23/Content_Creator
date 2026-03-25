import os
import requests
from dotenv import load_dotenv

load_dotenv()

class VisionAnalyzer:
    def __init__(self):
        self.ollama_url = f"{os.getenv('OLLAMA_BASE_URL')}/api/generate"
        self.model = os.getenv("OLLAMA_VISION_MODEL", "qwen2.5")

    def analyze_image(self, base64_image: str) -> str:
        """
        Envía la imagen en base64 al modelo de visión para extraer el texto y el contexto.
        """
        print(f"--- Analizando imagen con {self.model} ---")
        
        prompt = """Sos un experto creador de contenido en IA Industrial.
Analiza detenidamente esta imagen.
Extrae todo el texto visible (OCR) cuidando la precisión y comprende el contexto estructural (tablas, gráficos, esquemas).
A partir de todo este análisis, REDACTA UN BORRADOR COMPLETO para un post de LinkedIn explicando de manera profunda y enriquecedora el valor o concepto técnico que se muestra en la imagen.
Da el máximo detalle técnico posible y escribe directamente tu post borrador. No incluyas saludos, muletillas como 'Aquí tienes' o descripciones periféricas, comienza directamente con el cuerpo del texto."""

        try:
            response = requests.post(self.ollama_url, json={
                "model": self.model,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False
            }, timeout=300) # Alta tolerancia porque los modelos de visión tardan
            
            # Si el código es 4xx o 5xx, extraemos el mensaje de la API para saber si falta el modelo.
            if not response.ok:
                raise ValueError(f"Ollama devolvió un error (HTTP {response.status_code}): {response.text}")
                
            response.raise_for_status()
            
            result = response.json().get('response', '').strip()
            
            if not result:
                raise ValueError(f"{self.model} devolvió un análisis vacío.")
                
            return result
            
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"No se pudo conectar a Ollama en {self.ollama_url}. ¿Está corriendo?")
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Ollama tardó más de 300 segundos procesando la foto.")
        except Exception as e:
            raise RuntimeError(f"Error al analizar imagen: {e}")
