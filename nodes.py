import os
import numpy as np
import torch
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer, BlendMode


def tensor_to_pil_image(tensor):
    # Ensure tensor is on CPU and detached from grad
    tensor = tensor.cpu().detach()
    
    # If tensor is NCHW format, take first image
    if len(tensor.shape) == 4:
        tensor = tensor[0]
    
    # Convert CHW to HWC format
    if tensor.shape[0] in [1, 3, 4]:  # if in CHW format
        tensor = tensor.permute(1, 2, 0)
    
    # Handle different channel cases
    if tensor.shape[-1] == 1:  # Grayscale
        # Repeat the single channel 3 times and add alpha
        rgb = tensor.repeat(1, 1, 3)
        alpha = torch.ones(*tensor.shape[:-1], 1)
        tensor = torch.cat([rgb, alpha], dim=-1)
    
    elif tensor.shape[-1] == 3:  # RGB
        # Add alpha channel
        alpha = torch.ones(*tensor.shape[:-1], 1)
        tensor = torch.cat([tensor, alpha], dim=-1)
    
    elif tensor.shape[-1] != 4:
        raise ValueError(f"Invalid number of channels: {tensor.shape[-1]}")
    
    # Convert to uint8 and create PIL Image
    tensor = (tensor * 255).clamp(0, 255).byte()
    image = Image.fromarray(tensor.numpy(), mode='RGBA')
    
    return image


def pil_to_tensor_rgba(image: Image.Image) -> torch.Tensor:
    # RGBAモードでない場合は変換
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # ToTensorを使用して正しい変換を行う
    transform = T.ToTensor()
    tensor = transform(image)
    
    return tensor  # shape: (4, H, W)


class PSDData:
    class _Layer:
        def __init__(self, image:Image, name:str, blend_mode:BlendMode):
            if isinstance(image, torch.Tensor):
                self.image = tensor_to_pil_image(image)
            elif isinstance(image, Image.Image):
                self.image = image.convert("RGBA")
            self.name = name
            self.blend_mode = blend_mode

    def __init__(self):
        self.layers = []
    
    def append(self, image:Image, name:str, blend_mode:BlendMode):
        self.layers.append(self._Layer(image, name, blend_mode))
    
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
                "blend_mode": (blend_modes, { "default": BlendMode.NORMAL.name }),
            },
            "optional": {
                "PSD": ("PSD", {"default": None}),
            }
        }
    
    RETURN_TYPES = ("PSD",)

    FUNCTION = "tag"
    OUTPUT_NODE = False

    CATEGORY = "image"

    def tag(self, image, name, blend_mode=BlendMode.NORMAL.name, PSD=None):
        if PSD is None:
            PSD = PSDData()
        
        blend_mode_data = BlendMode.NORMAL
        for mode in BlendMode:
            if mode.name == blend_mode:
                blend_mode_data = mode
                break

        PSD.append(image, name, blend_mode_data)

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
        img = PSD.create_psd().composite()
        tensor = pil_to_tensor_rgba(img)
        return (tensor,)


NODE_CLASS_MAPPINGS = {
    "PSDLayer": PSDLayer,
    "Save PSD": PSDSave,
    "Convert PSD to Image": PSDConvert
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PSDLayer": "PSDLayer",
    "PSDSave": "PSDSave",

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
