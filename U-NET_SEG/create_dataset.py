from pathlib import Path
import shutil
import json
from PIL import Image
import numpy as np
import os
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

def create_mask(mask_tensor,label,points):
    shape_tensor = mask_tensor.shape
    if len(points) > 3 :
        poly = Polygon(points)
        for y in range(shape_tensor[0]):
            for x in range(shape_tensor[1]):
                p = Point([x,y])
                if poly.contains(p):
                    mask_tensor[y,x,label] = 255
    print("mask made for label", label)
    return mask_tensor

def create_mask_image(mask_tensor, path, name):
    shape_tensor = mask_tensor.shape
    mask_tensor = mask_tensor.astype(int)
    print("making mask images")
    for index in range(shape_tensor[2]):

        images = mask_tensor[:,:,index]
        img = Image.new(size=(shape_tensor[0],shape_tensor[1]), mode='RGB')
        pixels = img.load()

        for x in range(img.width):
            for y in range(img.height):
                pixels[x,y] = (images[y,x],images[y,x],images[y,x])

        save_path = path/Path(f"mask/mask_{name}")

        if not os.path.isdir( save_path ): os.mkdir( save_path )
        img.save(str(save_path)+f"/{index}.png")
        img.close()

    print("done\n")

def main():
    Classes = ["sky","zombie","creeper","skeleton","spider","witch","enderman","husk","villager","cow",
    "sheep","pig","olk_log","leaves","grass","dirt","stone","cobblestone","sand","iron","diamond"]

    image_path = Path("Annoted_images")
    label_path = Path("labels")
    train_path = Path(r"mob_dataset/Dataset/train")
    test_path = Path(r"mob_dataset/Dataset/test")
    for file in label_path.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            shapes = data["shapes"]
            height, width = data["imageHeight"], data["imageWidth"]
        print("got data",file)
        mask_tensor = np.zeros( ( height, width, len(Classes) ) )
        for object in shapes:
            label = Classes.index( object["label"].lower() )
            print(object["label"].lower())
            points = object["points"]
            mask_tensor = create_mask(mask_tensor, label, points)
        create_mask_image(mask_tensor, train_path, file.stem)
        shutil.copy(str(image_path / file.stem)+".png", str(train_path)+"/img")
main()
