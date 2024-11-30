from PIL import Image
import json,sys

def read_in():
    value = sys.stdin.readlines()[0]
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(value)

values = read_in()
get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]

for im in range(len(values)):
    grid = []
    img = Image.new( 'RGB', (8,12), "black") # Create a new black image
    pixels = img.load() # Create the pixel map
    foundindex = get_indexes(1,values[im][0])
    for i in foundindex:
        grid.append([i%8,(i - i%8)/8])
        for j in range(len(grid)):
            pixels[grid[j][0],grid[j][1]] = (255,255,255)
    img.save('./mongo/userInput({}).png'.format(im))
print([values])
