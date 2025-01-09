from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer, BlendMode


class PSDData:
    class _Layer:
        def __init__(self, image:Image, name:str, blend_mode:BlendMode):
            self.image = image
            self.name = name
            self.blend_mode = blend_mode

    def __init__(self):
        self.layers = []
    
    def append(self, image:Image, name:str, blend_mode:BlendMode):
        self.layers.append(self._Layer(image, name, blend_mode))

    def save(self, path):
        max_width = 0
        max_height = 0
        for layer in self.layers:
            layer_width = layer.image.size.width
            layer_height = layer.image.size.height
            if layer_width > max_width:
                max_width = layer_width
            if layer_height > max_height:
                max_height = layer_height

        psd = PSDImage.new(size=(max_width, max_height), mode='RGBA')

        for layer in self.layers:
            layer = PixelLayer.frompil(layer.image, psd, layer.name)
            layer.blend_mode = layer.blend_mode
            psd.append(layer)

        psd.save(path)


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
                "psd": ("PSD", {"default": None}),
                "blend_mode": (blend_modes, { "default": BlendMode.NORMAL.name }),
            },
        }
    
    RETURN_TYPES = ("PSD",)

    FUNCTION = "tag"
    OUTPUT_NODE = True

    CATEGORY = "image"

    def tag(self, image, name, psd=None,  blend_mode=BlendMode.NORMAL.name):
        if psd is None:
            psd = PSDData()

        psd.append(image, name, BlendMode[blend_mode])
        psd.save("output.psd")

        return (psd,)


NODE_CLASS_MAPPINGS = {
    "PSDLayer": PSDLayer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PSDLayer": "PSDLayer"
}
