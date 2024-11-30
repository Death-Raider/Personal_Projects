#Test Data
from modules import autopy as auto
from modules.PIL import Image

rect = (7,10)
start = (1392, 391)

screen = auto.bitmap.capture_screen((start, rect))
screen.save('return.bmp')

img = Image.open('./return.bmp')
thresh = 200
fn = lambda x : 255 if x > thresh else 0
new_img = img.convert('L').point(fn, mode='1')
new_img.save('return.bmp')

value = list(new_img.getdata())
for i in range(len(value)):
    value[i] = value[i]/255
print(value)
