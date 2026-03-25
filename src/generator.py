import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class LocalContentGenerator:
    def __init__(self):
        self.ollama_url = f"{os.getenv('OLLAMA_BASE_URL')}/api/generate"
        self.model = os.getenv("OLLAMA_MODEL")
        self.tone = self._load_tone()

    def _load_tone(self):
        tone_path = "data/tones.json"
        if os.path.exists(tone_path):
            try:
                with open(tone_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    active = data.get("active_tone")
                    if active:
                        return data.get("tones", {}).get(active, "")
            except Exception as e:
                print(f"Error cargando tonos: {e}")
        return ""

    def _get_tone_instruction(self):
        if self.tone:
            return f"\n\nInstrucción de Tono de Voz Obligatoria:\nAplica estrictamente este modo de comunicación en tu redacción final: '{self.tone}'."
        return ""

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

Escribí solo el post. Nada más. Sin comentarios, sin explicaciones al final.{self._get_tone_instruction()}"""
        
        return self._call_ollama(master_prompt)

    def generate_from_image_context(self, image_context):
        print(f"--- Generando contenido a partir de imagen localmente con {self.model} ---")
        
        master_prompt = f"""Sos un profesional de MLOps e IA Industrial escribiendo en LinkedIn.
Analizá esta información extraída de una imagen técnica:
{image_context}

Escribí un post de LinkedIn en español, directamente, sin títulos, sin etiquetas ni introducciones.

El post debe:
- Arrancar directo con el hook.
- Sonar humano y profesional, no como robot.
- Explicar o debatir el valor del contenido de la imagen.
- Cierre con llamada a la acción o pregunta.
- Terminar con exactamente 3 hashtags relevantes.
- Máximo 1300 caracteres en total.

Escribí solo el post. Nada más.{self._get_tone_instruction()}"""
        
        return self._call_ollama(master_prompt)

    def generate_image_prompt(self, idea, trends_context=None):
        print(f"--- Generando Prompt de Imagen localmente con {self.model} ---")
        
        trends_injection = ""
        if trends_context:
            trends_injection = f'''
Aquí tienes un resumen de las TENDENCIAS Y NOTICIAS ACTUALES sobre el tema sacadas de internet:
{trends_context}

TÚ DEBER: Integra inteligente y orgánicamente algunos conceptos visuales relevantes de estas tendencias dentro del escenario de la imagen. 
OJO: No listes palabras a lo bruto. Si una tendencia es "IA en medicina", agrega sutilmente "holographic medical interface" o "glowing DNA strands" a la composición fotográfica global.
'''

        master_prompt = f"""Sos un experto en arte digital y prompt engineering para Stable Diffusion XL.
Tu trabajo es tomar esta idea base del usuario: "{idea}" y convertirla en un prompt descriptivo, visualmente espectacular y súper técnico en INGLÉS puro (para la IA fotográfica).
{trends_injection}
Reglas del Prompt:
- Solo escribe el texto en inglés, sin preámbulos, descripciones, anotaciones ni explicaciones previas o posteriores.
- Usa palabras clave pesadas sobre iluminación, encuadre y texturas (ej: cinematic lighting, award winning, masterpiece, highly detailed, 8k, sharp focus).
- Separa las sub-ideas o descriptores fuertes con comitas (,).
- Limítate a las especificaciones conceptuales, descarta contexto inútil.

Escribí solo el prompt técnico final en inglés. Nada más."""
        
        return self._call_ollama(master_prompt)

    def refine_image_prompt(self, previous_prompt, feedback):
        print(f"--- Refinando Prompt Visual con {self.model} ---")
        prompt = f"""Sos un experto en prompt engineering para Stable Diffusion XL.
Tu trabajo es ajustar un prompt fotográfico existente basándote en el feedback del director de arte.

PROMPT ACTUAL:
"{previous_prompt}"

FEEDBACK DEL DIRECTOR DE ARTE:
"{feedback}"

TÚ MISIÓN: Modifica el PROMPT ACTUAL para incorporar o quitar lo que pide el feedback.
Reglas:
- Devuelve SOLO el nuevo prompt en INGLÉS puro, separado por comas.
- No incluyas explicaciones, ni contexto extra, solo las etiquetas técnicas de la imagen en inglés."""
        return self._call_ollama(prompt)

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

Aplicá las correcciones.
Devolvé solo el post corregido. Sin explicaciones, sin comentarios.{self._get_tone_instruction()}"""

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