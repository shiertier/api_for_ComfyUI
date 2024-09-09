from comfy.cli_args import args
import os
import json
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import folder_paths
import hashlib

class ApiSaveImage:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "save_folder": ("STRING", {"default": "", "tooltip": "If it starts with a slash (/), it is an absolute path; otherwise, it is a relative path (ComfyUI/ouput)."}),
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "api"
    DESCRIPTION = "save iamge for api"

    def save_images(self, images, save_folder="", prompt=None, extra_pnginfo=None):
        
        if save_folder.startswith('/'):
            full_output_folder = save_folder
        else:
            full_output_folder = os.path.join(self.output_dir, save_folder)        
        
        if not os.path.exists(full_output_folder):
            os.makedirs(full_output_folder)
        
        if not os.access(full_output_folder, os.W_OK):
            raise PermissionError(f"Cannot write to {full_output_folder}")

        results = list()
  
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            hasher = hashlib.md5()
            img_bytes = image.tobytes()
            hasher.update(img_bytes)
 
            file_name = hasher.hexdigest() + '.png'
            
            save_path = os.path.join(full_output_folder, file_name)
            
            if not os.path.exists(save_path):
                metadata = None
                if not args.disable_metadata:
                    metadata = PngInfo()
                    if prompt is not None:
                        metadata.add_text("prompt", json.dumps(prompt))
                    if extra_pnginfo is not None:
                        for x in extra_pnginfo:
                            metadata.add_text(x, json.dumps(extra_pnginfo[x]))
                    metadata.add_text("comfyui_api", json.dumps("True"))
                
                img.save(save_path, pnginfo=metadata, compress_level=self.compress_level)

            results.append({
                "filename": file_name,
                "subfolder": full_output_folder,
                "type": self.type
            })

        return { "ui": { "images": results } }

NODE_CLASS_MAPPINGS = {
    "ApiSaveImage": ApiSaveImage,
}
