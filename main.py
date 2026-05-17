# The main file
from Functions import fileManager

print("base_dir:", fileManager._base_dir())
print("assets source:", fileManager._base_dir() / "assets")
print("assets exists:", (fileManager._base_dir() / "assets").exists())
print("appdata assets exists:", fileManager.get_assets_dir().exists())
# Ensure AppData structure and bundled assets are available before UI imports
fileManager.ensure_appdata_structure()

from ui.UI import UI

UI()
