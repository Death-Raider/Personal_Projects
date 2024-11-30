import os
from pathlib import Path
import shutil

p = Path(r"labels_temp")
for f in p.glob("*.json"):
    file_name = f.stem
    image_name = f"Unannoted_images/{file_name}.png"
    new_image_path =  f"Annoted_images/{file_name}.png"
    if os.path.isfile(image_name):
        shutil.move(image_name,new_image_path)
