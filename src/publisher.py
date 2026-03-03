import os
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1' # Agregamos esta línea para silenciar el warning del scope
import json
import re # Para limpiar el texto
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv

load_dotenv()

class LinkedInPublisher:
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        # Esta URL debe estar cargada en tu App de LinkedIn Developer
        self.redirect_uri = "https://oauth.pstmn.io/v1/browser-callback" 
        self.auth_url = "https://www.linkedin.com/oauth/v2/authorization"
        self.token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.token_file = "data/linkedin_token.json"
        self.scope = ['w_member_social', 'openid', 'profile']

    def clean_content(self, text):
        """Lógica resolutiva para limpiar el post antes de publicar."""
        # 1. Separamos el post de las notas de explicación usando los divisores
        # Buscamos '---', '**Explicación' o 'Explicación de las decisiones'
        parts = re.split(r'---|\*\*Explicación|Explicación de las decisiones', text)
        clean_text = parts[0].strip()
        
        # 2. Borramos específicamente las citas tipo 
        # Usamos r'\' para que sea un raw string seguro
        clean_text = re.sub(r'\\', '', clean_text)
        
        # 3. Limpiamos espacios en blanco extra
        return clean_text.strip()

    def get_session(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                token = json.load(f)
            return OAuth2Session(self.client_id, token=token)
        
        linkedin = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.scope)
        authorization_url, _ = linkedin.authorization_url(self.auth_url)
        
        print(f"\n1. Autoriza aquí: {authorization_url}")
        redirect_response = input("2. Pega la URL completa de redirección: ")
        
        # CANJE DE TOKEN
        token = linkedin.fetch_token(
            self.token_url, 
            client_secret=self.client_secret, 
            authorization_response=redirect_response,
            include_client_id=True 
        )
        
        # FORZAMOS LA CREACIÓN DE LA CARPETA DATA SI NO EXISTE
        os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
        
        with open(self.token_file, 'w') as f:
            json.dump(token, f)
            
        print(f"✅ Token guardado correctamente en {self.token_file}")
        return linkedin

    def publish(self, raw_text):
        text = self.clean_content(raw_text)
        session = self.get_session()
        
        # Obtener URN del perfil
        user_info = session.get('https://api.linkedin.com/v2/userinfo').json()
        user_urn = f"urn:li:person:{user_info['sub']}"
        
        post_data = {
            "author": user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
        
        response = session.post('https://api.linkedin.com/v2/ugcPosts', json=post_data)
        return response.status_code, response.text

if __name__ == "__main__":
    with open("data/final_post.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    pub = LinkedInPublisher()
    status, msg = pub.publish(content)
    if status in [200, 201]:
        print("\n🚀 ¡Post publicado con éxito!")
    else:
        print(f"\n❌ Error {status}: {msg}")