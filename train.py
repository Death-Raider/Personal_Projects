import tensorflow as tf
from keras.layers import  Conv2D, UpSampling2D, MaxPool2D
from keras import Model, Input, Sequential
import keras
from parse_data import ParseData
from PIL import Image
import numpy as np
import cv2 as cv

def createTrainingData(input,amount):
    train_input = []
    train_output = []
    indicies = []
    for i in range(amount):
        rand_no = np.random.randint(len(input)-1)
        if rand_no in indicies:
            i -= 1
            continue
        train_input.append(input[rand_no])
        train_output.append(input[rand_no+1])
        indicies.append(rand_no)

    return np.array(train_input), np.array(train_output)

import moviepy.video.io.ImageSequenceClip

def make_movie(size,fps):
    image_files  = list(map(lambda a: f"Images_2021/india_{a}.png",np.arange(0,size)))
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)
    clip.write_videofile(f'animation@{fps}.mp4')
    return True

# make_movie(365,10)
pth1 = "CCS_India_2023-09-22042603am_2018.nc"
pth2 = "CCS_India_2023-09-22042603am_2019.nc"
pth3 = "CCS_India_2023-09-22042603am_2020.nc"
pth4 = "CCS_India_2023-09-22042603am_2021.nc"
pth5 = "CCS_India_2023-09-22042603am_2022.nc"
PD = ParseData()
PD.load(pth2)
PD.getVariableValues()

reshape_india_height = len(PD.LatitudeY)
reshape_india_width = len(PD.LongitudeX)
img = Image.open("images/india.png")
img_reshaped = PD.resizing_img(img,(reshape_india_width,reshape_india_height))
# PD.plotting(img_reshaped,"Images_2021",10)

inputs = PD.Rainfall
(trainX, trainY) = createTrainingData(inputs,int(len(inputs)))
del inputs
del PD

def mymodel(H,W): # basic model
    model = Sequential()
    model.add(Input(shape=(H,W,1)))
    model.add(Conv2D(16,(3,3),padding="same"))
    model.add(Conv2D(8,(3,3),padding="same"))
    model.add(Conv2D(1,(3,3),padding="same"))
    
    model.compile(optimizer="adam", loss="mse")
    return model

# model = mymodel(trainX.shape[1],trainX.shape[2])
# model.summary()
model = keras.models.load_model("test2")
model.fit(trainX,trainY,epochs=10)
model.save("test2")


PD = ParseData()
PD.load(pth2)
PD.getVariableValues()
inputs = PD.Rainfall
print(inputs.shape)
testX = np.expand_dims(inputs,axis=3)

predicted  = model.predict(testX[42].reshape((1,1075,733,1))).squeeze()
print(predicted.shape)

img_numpy = np.asarray(Image.open("images/Resized.png")).copy()
img = img_numpy
zeros = np.zeros_like(predicted)

out = np.array([zeros,zeros,predicted*255/predicted.max()],dtype=int)
out = np.moveaxis(out,0,-1)

out_mask = predicted > 10
out_mask = np.array([out_mask]*3)
out_mask = np.moveaxis(out_mask,0,-1)

img = np.where(out_mask,out,img)
img = Image.fromarray(img.astype(np.uint8))
img.save("images/india_output.png")
print(out)
