import os
import sys

#Using the tutorial by CG Python: https://www.youtube.com/watch?v=VOMb_zmVrtk



ADDON_FOLDER_PATH = os.path.dirname(__file__)
VERSION = (0, 1, 1)
MODULE_NAME = "RenderMakerbotBlender active patch"
ADDON_NAME = (
    f"RenderMakerbotBlender v{VERSION[0]}.{VERSION[1]}.{VERSION[2]}"
)

bl_info = {
    "name": "RenderMakerbotBlender v0.1.0",
    "author": "GreenAppleIsSpicy",
    "version": (0, 1, 1),
    "blender": (4, 3, 0),
    "description": "Personal Addon for blender that allows someone to render 3D prints sliced for the MakerBot Replicator 5th Gen and Replicator+.",
    "category": "Development",
    "doc_url": "https://github.com/GreenAppleIsSpicy/RenderMakerbotBlenderAddon",
}



def register():
    print(f'ENABLED "{ADDON_NAME}" addon')

    print(f"\tadding {MODULE_NAME} to sys path: {ADDON_FOLDER_PATH}")
    sys.path.append(ADDON_FOLDER_PATH)
    import Panel
    Panel.register()


def unregister():
    print(f'DISABLE "{ADDON_NAME}" addon')

    print(f"\tremoving {MODULE_NAME} from sys path: {ADDON_FOLDER_PATH}")
    sys.path.remove(ADDON_FOLDER_PATH)
    import Panel
    Panel.unregister()


if __name__ == "__main__":
    register()
