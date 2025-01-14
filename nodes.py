import os
import numpy as np
import torch
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer, BlendMode


def convert_to_pil(image: torch.Tensor) -> Image.Image:
    if isinstance(image, Image.Image):
        return image
    if isinstance(image, np.ndarray):
        return Image.fromarray(np.clip(255. * image.squeeze(), 0, 255).astype(np.uint8))
    if isinstance(image, torch.Tensor):
        return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))
    raise ValueError(f"Unknown image type: {type(image)}")


def convert_to_tensor(image: Image.Image) -> torch.Tensor:
    if isinstance(image, torch.Tensor):
        return image
    if isinstance(image, np.ndarray):
        return torch.from_numpy(image.astype(np.float32) / 255.0).unsqueeze(0)
    if isinstance(image, Image.Image):
        return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)


class PSDData:
    class _Layer:
        def __init__(self, image:Image, name:str, opacity:float, blend_mode:BlendMode):
            if isinstance(image, torch.Tensor):
                self.image = convert_to_pil(image)
            elif isinstance(image, Image.Image):
                self.image = image.convert("RGBA")
            self.name = name
            self.blend_mode = blend_mode
            self.opacity = opacity

    def __init__(self):
        self.layers = []
    
    def append(self, image:Image, name:str, opacity:float, blend_mode:BlendMode):
        self.layers.append(self._Layer(image, name, opacity, blend_mode))
    
    def create_psd(self):
        max_width = 0
        max_height = 0
        for layer in self.layers:
            layer_width = layer.image.size[0]
            layer_height = layer.image.size[1]
            if layer_width > max_width:
                max_width = layer_width
            if layer_height > max_height:
                max_height = layer_height

        psd = PSDImage.new(size=(max_width, max_height), mode='RGBA')

        for layer in self.layers:
            add_layer = PixelLayer.frompil(layer.image, psd, layer.name)
            add_layer.blend_mode = layer.blend_mode
            add_layer.opacity = min(max(int(255 * layer.opacity), 0), 255)
            psd.append(add_layer)
        
        return psd

    def save(self, path):
        psd = self.create_psd()
        psd.save(path)


class PSDSave:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "PSD": ("PSD",),
                "dir": ("STRING", { "default": "ComfyUI/output" }),
                "filename": ("STRING", { "default": "output" }),
            },
            "optional": {
                "overwrite": ("BOOLEAN", { "default": False }),
            }
        }
    
    RETURN_TYPES = ()

    FUNCTION = "save"
    OUTPUT_NODE = True

    CATEGORY = "image"

    def save(self, PSD:PSDData, dir="ComfyUI/output", filename="output", overwrite=False):
        if not os.path.exists(dir):
            print(f"Creating directory {dir}")
            os.makedirs(dir)

        save_path = f"{dir}/{filename}.psd"
        if not overwrite:
            i = 1
            while os.path.exists(save_path):
                save_path = f"{dir}/{filename}_{i}.psd"
                i += 1
        
        PSD.save(save_path)

        return ()


class PSDLayer:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        blend_modes = [x.name for x in BlendMode]
        return {
            "required": {
                "image": ("IMAGE",),
                "name": ("STRING",),
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01}),
                "blend_mode": (blend_modes, { "default": BlendMode.NORMAL.name }),
            },
            "optional": {
                "PSD": ("PSD", {"default": None}),
            }
        }
    
    RETURN_TYPES = ("PSD",)

    FUNCTION = "create_layer"
    OUTPUT_NODE = False

    CATEGORY = "image"

    def create_layer(self, image, name, opacity, blend_mode=BlendMode.NORMAL.name, PSD=None):
        if PSD is None:
            PSD = PSDData()
        
        blend_mode_data = BlendMode.NORMAL
        for mode in BlendMode:
            if mode.name == blend_mode:
                blend_mode_data = mode
                break

        PSD.append(image, name, opacity, blend_mode_data)

        return (PSD,)


class PSDConvert:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "PSD": ("PSD",),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)

    FUNCTION = "preview"
    OUTPUT_NODE = True

    CATEGORY = "image"

    def preview(self, PSD:PSDData):
        img = PSD.create_psd().composite(alpha=0.0)
        tensor = convert_to_tensor(img)
        return (tensor,)


NODE_CLASS_MAPPINGS = {
    "PSDLayer": PSDLayer,
    "Save PSD": PSDSave,
    "Convert PSD to Image": PSDConvert
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PSDLayer": "PSDLayer",
    "PSDSave": "PSDSave",
    "PSDConvert": "PSDConvert"
}


def simple_test():
    from PIL import Image
    image = Image.new("RGB", (100, 100), (255, 0, 0))

    psdlayer1 = PSDLayer()
    psd = psdlayer1.tag(image, "test1", blend_mode="NORMAL")

    psdlayer2 = PSDLayer()
    psd = psdlayer2.tag(Image.open("test01.png"), "test2", psd=psd[0], blend_mode="NORMAL")

    psdlayer3 = PSDLayer()
    psd = psdlayer3.tag(Image.open("test02.png"), "test3", psd=psd[0], blend_mode="SCREEN")

    psd[0].save("output.psd")


#if __name__ == "__main__":
#    simple_test()
