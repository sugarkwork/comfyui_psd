import psd_save

class SavePSD:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "name": ("STRING",),
                "image1": ("IMAGE",),
              "optional": {
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
                "image6": ("IMAGE",),
                "image7": ("IMAGE",),
                "image8": ("IMAGE",),
                "image9": ("IMAGE",),
                },
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_psd"

    CATEGORY = "Example"

    def save_psd(self, name, image1, image2=None, image3=None, image4=None, image5=None, image6=None, image7=None, image8=None, image9=None):
        print(f"save_psd: {name}")
        return

NODE_CLASS_MAPPINGS = {
    "SavePSD": SavePSD
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SavePSD": "SavePSD Node"
}
