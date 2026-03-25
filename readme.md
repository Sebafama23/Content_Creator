# 🚀 AI Content Factory (Human-in-the-Loop)
Sistema automatizado e interactivo de creación de contenido técnico y visual para LinkedIn. Orquestado con Docker, potenciado por Modelos Multimodales Locales (Gemma 3 + Qwen2.5-VL + SDXL en ComfyUI) y controlado dinámicamente mediante Telegram.

## 🛠️ Arquitectura y Flujo
El sistema sigue un flujo agentico interactivo diseñado para la excelencia visual y textual:

1- Analyzer (Vision): OCR Multimodal con Qwen2.5-VL para extraer contexto semántico profundo de fotografías aportadas por el usuario.

2- Researcher: Scraping dinámico (SerpApi) enfocado en Google News para inyectar tendencias de última hora a los prompts.

3- Generator: Redacción y Prompt Engineering fotográfico usando Gemma 3, impulsado por un Sistema de Tonos inyectable (`data/tones.json`).

4- Image Creator: Renderizado de arte fotográfico local delegando prompts técnicos en la API de ComfyUI (SDXL).

5- Editor: Limpieza estricta basada en expresiones regulares para erradicar sesgos y muletillas robóticas ("anti-IA").

6- HITL (Human-in-the-loop): Máquina de estados en Telegram. El usuario puede iniciar, iterar infinitamente versiones de texto/imagen o abortar flujos en tiempo real.

7- Publisher: Empaque y publicación final paralela (Texto + Imágenes Binarias UGC) nativa en LinkedIn mediante API (OAuth2).

####################################################################################################

## 📋 Requisitos Previos
- Docker & Docker Compose instalados.
- Ollama corriendo localmente con los modelos descargados: `gemma3:4b` y `qwen2.5vl:3b`.
- Modelos SDXL: El checkpoint `sd_xl_base_1.0.safetensors` descargado en la carpeta de models de ComfyUI.

Credenciales:
- Telegram: TOKEN y CHAT_ID (vía @BotFather).
- LinkedIn: Client ID y Client Secret (vía LinkedIn Developers).
- SerpApi: Clave de API para búsqueda dinámica en internet.

####################################################################################################

## ⚙️ Configuración del Entorno
Crea un archivo .env en la raíz con el siguiente formato:

--> Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=gemma3:4b
OLLAMA_VISION_MODEL=qwen2.5vl:3b

--> APIs Externas
SERPAPI_KEY=tu_api_key

--> Telegram
TELEGRAM_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_id

--> LinkedIn
LINKEDIN_CLIENT_ID=tu_id
LINKEDIN_CLIENT_SECRET=tu_secret

####################################################################################################

## 🚀 Guía de Instalación y Uso
1. Despliegue con Docker Compose
El entorno incluye Capping de RAM y `--lowvram` multiplexing entre los modelos para evitar caídas.
Desde la terminal en la raíz del proyecto, levanta los servicios (Orquestador + ComfyUI):
`docker-compose up -d --build`

2. Ejecución del Orquestador (Consola de Telegram)
El bot de Telegram inicia como orquestador pasivo (`run_polling`). Solo ábrelo y mándale comandos:
- `/command1`: Envía una imagen para que el modelo de visión la interprete y genere un post.
- `/command2 [tema]`: Busca noticias y publica un post de texto.
- `/command3 [tema]`: Busca noticias, inventa un prompt de SDXL local, genera la imagen y redacta el post final.

3. Máquina de Estados (Iteración)
Tras cualquier comando, el Capitán Morgan (Bot) te contactará:
- Para publicar/avanzar: Responde sencillamente la palabra `confirmado`.
- Para ajustar: Escribe directamente el texto con quejas/direcciones (ej: "hacelo de noche" o "hazlo más profesional"). El bot iterará la pieza visual o el post y devolverá la nueva versión.
- Para abortar: escribe `/command4` (o invoca `/ayuda`).

####################################################################################################

## 📁 Estructura de Datos
`src/`: Módulos especializados de análisis, edición, generación de imagen y publicación.
`data/comfyui/`: Persistencia de Modelos (>6.5GB) e Historial de imágenes del renderizador.
`data/tones.json`: Configurador de Personalidad inyectable para el LocalContentGenerator.
`files/`: Caché aislado de fotografías subidas temporalmente por el usuario para OCR.
`data/linkedin_token.json`: Persistencia de autenticación OAuth2 (ignorado en Git).

####################################################################################################

## 🛡️ Seguridad y Optimización
Este repositorio cuenta con un `.gitignore` y un `.dockerignore` blindados:
❌ Evita fugas de .env, tokens o historiales privados.
❌ Protege la indexación de Git y el Build-Context de Docker vetando el peso excesivo de la carpeta `data/comfyui/` (evita subir modelos de 6GB a la nube o colapsar el daemon).