from modules import Augmentor
from modules.PIL import Image
import sys, json
import os
import glob

def read_in():
    value = sys.stdin.readlines()[0]
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(value)

sampleSize = 500
data = read_in()
if data == 'generate':
    for i in range(10):

        p = Augmentor.Pipeline(".\Train_Images\{0}'s".format(i))
        p.random_distortion(0.7,3,5,1)
        p.random_distortion(0.1,4,6,1)
        p.sample(sampleSize)

        images = glob.glob(".\Train_Images\{0}'s\output\*.png".format(i))

        os.chdir(r".\Train_Images\{0}'s\output".format(i))
        for index, oldfile in enumerate(glob.glob("*.png"), start=0):
            newfile = '{0}.png'.format(index)
            os.rename (oldfile,newfile)
            img = Image.open(newfile)
            new_img = img.convert('L')
            new_img.save('{0}({1}).bmp'.format(index,i))
            os.remove(newfile)
        os.chdir("..")
        os.chdir("..")
        os.chdir("..")
if isinstance(data, list):
    img_send_value = [0]*len(data)
    for i in range(len(data)):
        img = Image.open(".\Train_Images\{0}'s\output\{1}({0}).bmp".format(data[i][0],data[i][1]))
        img_value = list(img.getdata())
        for k in range(len(img_value)): img_value[k] = img_value[k]/255
        img_send_value[i] = img_value
    print(img_send_value)
