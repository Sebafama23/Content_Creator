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
        
        return clean_text.strip()

    def save_versioned_post(self, text):
        """Guarda el archivo con el formato: publicacion_DD_MM_AAAA_vN.txt"""
        today_str = datetime.now().strftime("%d_%m_%Y")
        version = 1
        
        # Lógica de búsqueda de versión existente
        while True:
            filename = f"publicacion_{today_str}_v{version}.txt"
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
    path, v = editor.save_versioned_post(clean_post)
    print(f"✅ Versión {v} generada en: {path}")