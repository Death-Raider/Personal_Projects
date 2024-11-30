from modules.PIL import Image
import json,sys

def read_in():
    value = sys.stdin.readlines()[0]
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(value)

values = read_in()
print(values)
get_indexes = lambda x, xs: [i for (y, i) in zip(xs, range(len(xs))) if x == y]
foundindex = get_indexes(1,values)
grid = []
img = Image.new( 'RGB', (8,12), "black") # Create a new black image
pixels = img.load() # Create the pixel map

for i in foundindex:
    grid.append([i%8,(i - i%8)/8])
print(foundindex,grid,len(grid))
for i in range(len(foundindex)):
    pixels[grid[i][0],grid[i][1]] = (255,255,255)
img.save('./userInput.bmp')
