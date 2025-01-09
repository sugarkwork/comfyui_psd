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
        
        blend_mode_data = BlendMode.NORMAL
        for mode in BlendMode:
            if mode.name == blend_mode:
                blend_mode_data = mode
                break

        psd.append(image, name, blend_mode_data)
        psd.save("output.psd")

        return (psd,)


NODE_CLASS_MAPPINGS = {
    "PSDLayer": PSDLayer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PSDLayer": "PSDLayer"
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
