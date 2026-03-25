import os
import re
from datetime import datetime

class ContentEditor:
    def __init__(self, base_path="data/posts"):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def clean_draft(self, raw_text):
        if not raw_text or raw_text.startswith("Error"):
            raise ValueError(f"Contenido inválido recibido del generador: {raw_text}")
        
        # Gemma a veces antepone una intro conversacional antes del post real
        # El contenido útil arranca después del primer "---"
        parts = re.split(r'\n---+\n', raw_text)
        
        if len(parts) >= 3:
            # Estructura: [intro] --- [post] --- [explicacion]
            clean_text = parts[1]
        elif len(parts) == 2:
            # Estructura: [intro] --- [post]
            clean_text = parts[1]
        else:
            # Sin separadores: tomar todo (Gemma respondió directo)
            clean_text = parts[0]
        
        # Eliminar notas finales si las hay
        clean_text = re.split(r'\*\*Explicación|\nExplicación|\nNota:', clean_text)[0]
        
        # Filtros estrictos anti-IA y formato
        # Remover prefijos conversacionales de IA
        clean_text = re.sub(r'^(Aquí tienes|Aquí tiene|Claro|Por supuesto|Este es|Te presento).*?\n', '', clean_text, flags=re.IGNORECASE).strip()
        # Remover sufijos o preguntas genéricas de IA
        clean_text = re.sub(r'(Espero que.*?sirva|¡Avísame si.*?|Dime si .*?)\.?$', '', clean_text, flags=re.IGNORECASE).strip()
        
        # Eliminar asteriscos de markdown y comillas
        clean_text = clean_text.replace('**', '').replace('"', '').replace("'", "")
        # Eliminar bloques de código markdown residuales
        clean_text = re.sub(r'```[a-zA-Z]*\n?', '', clean_text)
        clean_text = clean_text.replace('```', '')
        
        return clean_text.strip()

    def save_versioned_post(self, text, flow_id):
        """Guarda el archivo con el formato: post_DD_MM_AAAA_{flow_id}_vN.txt"""
        today_str = datetime.now().strftime("%d_%m_%Y")
        version = 1
        
        # Lógica de búsqueda de versión existente para ese flujo y día
        while True:
            filename = f"post_{today_str}_{flow_id}_v{version}.txt"
            filepath = os.path.join(self.base_path, filename)
            if not os.path.exists(filepath):
                break
            version += 1
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        return filepath, version

if __name__ == "__main__":
    # Prueba rápida del componente
    with open("data/final_post.txt", "r", encoding="utf-8") as f:
        draft = f.read()
    
    editor = ContentEditor()
    clean_post = editor.clean_draft(draft)
    path, v = editor.save_versioned_post(clean_post, "testflow")
    print(f"✅ Versión {v} generada en: {path}")