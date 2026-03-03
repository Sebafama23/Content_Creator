# 🚀 AI Content Factory (Human-in-the-Loop)
Sistema automatizado de creación de contenido técnico para LinkedIn, orquestado con Docker, Gemma 3 (Ollama) y validación humana mediante Telegram.

## 🛠️ Arquitectura y Flujo
El sistema sigue un flujo agentico diseñado para la eficiencia:

1- Researcher: Scraping de tendencias y noticias técnicas.

2- Generator: Redacción de posts con Gemma 3 (Local LLM).

3- Editor: Limpieza de texto y versionado automático (publicacion_v1.txt, v2.txt, etc.).

4- HITL (Human-in-the-loop): Envío de propuesta a Telegram para aprobación o feedback.

5- Publisher: Publicación final en LinkedIn mediante API (OAuth2).

####################################################################################################

## 📋 Requisitos Previos
Docker & Docker Compose instalados.

Ollama corriendo localmente con el modelo gemma3 descargado. Se puede utilizar otro modelo, pero para esto se debe modificar el modelo en el .env. 

Credenciales:
- Telegram: TOKEN y CHAT_ID (vía @BotFather).
- LinkedIn: Client ID y Client Secret (vía LinkedIn Developers).

####################################################################################################

## ⚙️ Configuración del Entorno
Crea un archivo .env en la raíz con el siguiente formato:
--> Ollama
OLLAMA_BASE_URL=http://host.docker.internal:11434

--> Telegram
TELEGRAM_TOKEN=tu_token
TELEGRAM_CHAT_ID=tu_id

--> LinkedIn
LINKEDIN_CLIENT_ID=tu_id
LINKEDIN_CLIENT_SECRET=tu_secret

####################################################################################################

## 🚀 Guía de Instalación y Uso
1. Despliegue con Docker Compose
Desde la terminal en la raíz del proyecto, buildea y levanta el servicio:
docker-compose up --build -d

2. Ejecución del Orquestador
Para iniciar un nuevo ciclo de creación de contenido:
docker exec -it Content_creator python main.py

3. Ciclo de Aprobación (Telegram)
Una vez iniciado el script, el Capitán Morgan (Bot) te contactará:
- Para publicar: Responde confirmado.
- Para ajustar: Escribe tus comentarios (ej: "Hacelo más corto"). El sistema generará una nueva versión automáticamente.
- Para cancelar: escribe /cancelar

####################################################################################################

## 📁 Estructura de Datos
src/: Lógica modular de los agentes.

data/posts/: Historial de publicaciones generadas con su respectivo versionado.

data/linkedin_token.json: Persistencia de autenticación OAuth2 (ignorado en Git).

####################################################################################################

## 🛡️ Seguridad
Este repositorio utiliza un .gitignore estricto para asegurar que:

❌ No se filtren credenciales (.env).

❌ No se suban tokens de acceso (linkedin_token.json).

❌ No se cargue historial de posts privados.