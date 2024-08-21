import os

import numpy as np
import requests
from PIL import Image
import io
import random
import json

import folder_paths

class SendToWebhook:
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {
                        "images": ("IMAGE", ),
                        "webhook_name": ("STRING", {"default": "ComfyUI"}),
                        "webhook_url": ("STRING", {"default": "https://discord.com/api/webhooks/YOUR_WEBHOOK_HASH"}),
                    },
                    "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }
    
    RETURN_TYPES = ()
    OUTPUT_NODE = True

    CATEGORY = "image"
    FUNCTION = "save_images"

    def post(self, image_paths, metadata, webhook_url: str, name: str = "ComfyUI"):
        try:
            msg_content = f"```{metadata}```"
            files = {}
            for i, image in enumerate(image_paths):
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='PNG', compress_level=self.compress_level)
                image_bytes.seek(0)
                files[f"image{i+1}"] = (f"image{i+1}.png", image_bytes, 'image/png')

            payload_data = {
                'content': msg_content,
                'username': name,
            }

            response = requests.post(webhook_url, files=files, data=payload_data)
            if response.status_code == 200:
                return True
            else:
                return False

        except Exception as err:
            print(err)
            return False

    def save_images(self, images, webhook_name, webhook_url, prompt=None, extra_pnginfo=None):
        metadata = None
        container = []

        if prompt is not None:
            metadata = json.dumps(prompt)

        for image in images:
            array = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(array, 0, 255).astype(np.uint8))
            container.append(img)

        try_post = self.post(container, metadata, webhook_url, webhook_name)
        if try_post:
            print(f"Image sent to discord")
            return ("Yay! You did it!", )

        return ("Failed :(", )

# Add this new node to the dictionary of all nodes
NODE_CLASS_MAPPINGS = {
    "SendToWebhook": SendToWebhook,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SendToWebhook": "Send Generated Image To Discord Webhook",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']