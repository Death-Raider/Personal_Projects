import glob
import os
for i in range(10):
    filesbmp = glob.glob(".\Train_Images\{0}'s\output\*.bmp".format(i))
    for f in filesbmp:
        os.remove(f)
    filespng = glob.glob(".\Train_Images\{0}'s\output\*.png".format(i))
    for f in filespng:
        os.remove(f)
