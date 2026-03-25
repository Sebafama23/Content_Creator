import urllib.request
import urllib.parse
import json
import time
import os
import asyncio

class ComfyUIClient:
    def __init__(self, server_address="http://comfyui:8188"):
        # Usamos la conexión interna del docker-compose (el contenedor se llama 'comfyui')
        self.server_address = server_address
        self.client_id = "content_creator_bot"

    async def generate_image(self, positive_prompt, negative_prompt="text, watermark, ugly, deformed, blurry, worst quality, low resolution", filename_prefix="linkedin_post"):
        # Plantilla API Workflow estandarizada para SDXL en ComfyUI
        workflow = {
          "3": {
            "class_type": "KSampler",
            "inputs": {
              "seed": int(time.time()),
              "steps": 25,
              "cfg": 7,
              "sampler_name": "euler",
              "scheduler": "normal",
              "denoise": 1,
              "model": ["4", 0],
              "positive": ["6", 0],
              "negative": ["7", 0],
              "latent_image": ["5", 0]
            }
          },
          "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
              "ckpt_name": "sd_xl_base_1.0.safetensors"
            }
          },
          "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
              "width": 1024,
              "height": 1024,
              "batch_size": 1
            }
          },
          "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
              "text": positive_prompt,
              "clip": ["4", 1]
            }
          },
          "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
              "text": negative_prompt,
              "clip": ["4", 1]
            }
          },
          "8": {
            "class_type": "VAEDecode",
            "inputs": {
              "samples": ["3", 0],
              "vae": ["4", 2]
            }
          },
          "9": {
            "class_type": "SaveImage",
            "inputs": {
              "filename_prefix": filename_prefix,
              "images": ["8", 0]
            }
          }
        }

        p = {"prompt": workflow, "client_id": self.client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(f"{self.server_address}/prompt", data=data)
        
        try:
            response = urllib.request.urlopen(req)
            result = json.loads(response.read())
            prompt_id = result.get("prompt_id")
            
            print(f"🎨 Generando imagen (Prompt ID: {prompt_id})...")
            
            # La imagen aparecerá finalmente en la carpeta compartida data/comfyui/output
            expected_folder = "data/comfyui/output"
            
            # Polling / Espera activa interactuando con la API de History de forma asíncrona
            for _ in range(60): # Timeout de 5 minutos (60 * 5s)
                await asyncio.sleep(5)
                hist_req = urllib.request.Request(f"{self.server_address}/history/{prompt_id}")
                try:
                    hist_res = urllib.request.urlopen(hist_req)
                    hist_data = json.loads(hist_res.read())
                    if prompt_id in hist_data: # ComfyUI lo agrega a la historia cuando finaliza
                        outputs = hist_data[prompt_id].get("outputs", {})
                        for node_id, output_data in outputs.items():
                            if "images" in output_data:
                                img_filename = output_data["images"][0]["filename"]
                                final_path = os.path.join(expected_folder, img_filename)
                                if os.path.exists(final_path):
                                    return final_path
                except Exception:
                    pass
                
            raise TimeoutError("Se agotó el tiempo esperando la renderización de la tarjeta.")
            
        except Exception as e:
            raise RuntimeError(f"Error programático comunicándose con ComfyUI: {e}")
