from netCDF4 import Dataset
from PIL import Image
import numpy as np

class ParseData:
    def _init_(self):
        pass

    def load(self,path):
        print("started")
        self.file = path
        self.data = Dataset(self.file,"r+",format="NETCDF4")
        print("loaded data")
    
    def getVariableValues(self):
        self.LongitudeX = self.data.variables["lon"][:]
        self.LatitudeY = self.data.variables["lat"][:]
        self.Time = self.data.variables["datetime"][:]
        self.Rainfall = self.data.variables["precip"][:]
        self.Rainfall = np.where(self.Rainfall > 0, self.Rainfall, 0)

    def thresholding(self,thresh):
        return self.Rainfall > thresh

    def resizing_img(self,img,shape):
        rimg = img.resize(shape)
        rimg.save("Resized.png")
        return np.asarray(rimg).copy()
    
    def plotting(self,img_numpy,path,thresh):
        zeros = np.zeros_like(self.Rainfall[0])
        opacity = 255*np.ones_like(self.Rainfall[0])
        rainfall_significance = self.thresholding(thresh)

        for i in range(len(self.Time)):
            img = img_numpy.copy()

            out = np.array([zeros,zeros,self.Rainfall[i]*255/self.Rainfall[i].max()],dtype=int)
            out = np.moveaxis(out,0,-1)

            out_mask = rainfall_significance[i]
            out_mask = np.array([out_mask]*3)
            out_mask = np.moveaxis(out_mask,0,-1)

            img = np.where(out_mask,out,img)
            img = Image.fromarray(img.astype(np.uint8))
            img.save(path+f"/india_{i}.png")
            print(i)

    def description(self):
        print("Latitude range:",min(self.LatitudeY),max(self.LatitudeY))
        print("Longitiude range:",min(self.LongitudeX),max(self.LongitudeX))
        print("rainfall range:",self.Rainfall.min(),self.Rainfall.max(), self.Rainfall.mean())