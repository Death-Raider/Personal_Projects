import tensorflow as tf
from tensorflow_examples.models.pix2pix import pix2pix
import matplotlib.pyplot as plt
from pathlib import Path, WindowsPath
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from scipy.spatial import ConvexHull
import json,  math, sys
sys.setrecursionlimit(10000)

def normalize(input_image):
    input_image = (input_image-input_image.min())/(input_image.max()-input_image.min())
    return input_image

def LoadMask(maskPath):
    mask = np.zeros((224,224,21))
    for imgName in maskPath.glob("*.png"):
        print(imgName, imgName.stem)
        i = int(imgName.stem)
        img = Image.open(imgName).resize((224,224)).convert(mode="L")
        imgData = np.array(img)
        img.close()
        mask[:,:,i] = imgData
    return normalize(mask)

def LoadImage(imgPath):
    img = Image.open(imgPath).resize((224,224))
    imgData = np.array(img)
    img.close()
    return normalize(imgData)[:,:,:3]

def displayImg(display_list):
    plt.figure(figsize=(10, 10))
    title = ['Input Image', 'True Mask', 'Predicted Mask']
    for i in range(len(display_list)):
        plt.subplot(1, len(display_list), i+1)
        plt.title(title[i])
        plt.imshow(display_list[i])
        # plt.axis('off')
    plt.show()

def create_unet_model(input_shape, OUTPUT_CLASSES):
    def unet_model(output_channels:int):
        inputs = tf.keras.layers.Input(shape=input_shape)
        # Downsampling through the model
        skips = down_stack(inputs)
        x = skips[-1]
        skips = reversed(skips[:-1])

        # Upsampling and establishing the skip connections
        for up, skip in zip(up_stack, skips):
            x = up(x)
            concat = tf.keras.layers.Concatenate()
            x = concat([x, skip])

        # This is the last layer of the model
        last = tf.keras.layers.Conv2DTranspose(
            filters=output_channels, kernel_size=3, strides=2,
            padding='same')  #64x64 -> 128x128

        x = last(x)
        return tf.keras.Model(inputs=inputs, outputs=x)

    base_model = tf.keras.applications.MobileNetV2(input_shape=input_shape, include_top=False)
    # Use the activations of these layers
    layer_names = [
        'block_1_expand_relu',   # 64x64
        'block_3_expand_relu',   # 32x32
        'block_6_expand_relu',   # 16x16
        'block_13_expand_relu',  # 8x8
        'block_16_project',      # 4x4
    ]
    base_model_outputs = [base_model.get_layer(name).output for name in layer_names]
    # Create the feature extraction model
    down_stack = tf.keras.Model(inputs=base_model.input, outputs=base_model_outputs)
    down_stack.trainable = False

    up_stack = [
        pix2pix.upsample(512, 3),  # 4x4 -> 8x8
        pix2pix.upsample(256, 3),  # 8x8 -> 16x16
        pix2pix.upsample(128, 3),  # 16x16 -> 32x32
        pix2pix.upsample(64, 3),   # 32x32 -> 64x64
    ]

    return unet_model(output_channels=OUTPUT_CLASSES)

def getCutouts(image,predicted):
    segmented = np.zeros((224,224,3,21))
    for k in range(3):
        for i in range(21):
            segmented [:,:,k,i] = 1*(predicted[:,:,i]>0.60)*image[0,:,:,k]  # 0.50 -> everything above 50% accuracy will be shown
    segmented = (segmented - segmented.min())*255/(segmented.max()-segmented.min())
    segmented = segmented.astype(int)
    print(predicted.shape, segmented.shape, segmented.max(), segmented.min())
    return segmented

# def getHulls(predicted,accuracy):
#     # gets the bounding polygon for predicted
#     channels,height,width = predicted.shape
#     hull = [[]]*channels
#     for k in range(channels):
#         points = []
#         for i in range(height):
#             for j in range(width):
#                 if predicted[k,i,j]>accuracy: # [index, height, width]
#                     points.append([j,i]) # (width, height)
#         if len(points) > 2:
#             points = np.array(points)
#             hull[k] = ConvexHull(points)
#     return np.array(hull, dtype='object')

# def get_polygon(hull):
#     if hull != []:
#         return np.array([ [tuple(hull.points[simplex[0]]),tuple(hull.points[simplex[1]]) ] for simplex in hull.simplices ])
#     else:
#         return []

def viewPrediction(image, polygon):
    # newImage = np.array(Image.fromarray((image[0]*255).astype('uint8')).resize((416,416)))
    outputImage = Image.fromarray((image), "RGB")
    img1 = ImageDraw.Draw(outputImage)
    for edge in polygon:
        print(edge)
        img1.line(edge, fill ="red", width = 1)
    outputImage.show()

# def angle_and_distance(point,origin):
#     refvec = [0, 1] # direction of orering
#     vector = [point[0]-origin[0], point[1]-origin[1]]
#     lenvector = math.hypot(vector[0], vector[1])
#     if lenvector == 0:
#         return -math.pi, 0
#     normalized = [vector[0]/lenvector, vector[1]/lenvector]
#     dotprod  = normalized[0]*refvec[0] + normalized[1]*refvec[1]     # x1*x2 + y1*y2
#     diffprod = refvec[1]*normalized[0] - refvec[0]*normalized[1]     # x1*y2 - y1*x2
#     angle = math.atan2(diffprod, dotprod)
#     if angle < 0:
#         return 2*math.pi+angle, lenvector
#     return angle, lenvector
#
# def centroid(points):
#     length = len(points)
#     return (np.sum(points, axis = 0)/length).tolist()

def floodFill(matrix):
    matrix = matrix.tolist()
    checkPoint = lambda P: (P[0] >= len(matrix) or P[1] >= len(matrix[0]) or P[0] < 0 or P[1] < 0)
    p = [ [i,e.index(1)] for i,e in enumerate(matrix) if e.count(1) > 10 ]
    if len(p) > 10:
        A = p[10]
    else:
        return []
    boundary_points = []
    Stack = [A]
    while len(Stack) > 0:
        A = Stack.pop(0)
        if A in boundary_points:
            continue
            # return boundary_points
        back_down_diagonal_point = [A[0]+1, A[1]-1]
        back_up_diagonal_point = [A[0]-1, A[1]-1]
        front_down_diagonal_point = [A[0]+1, A[1]+1]
        front_up_diagonal_point = [A[0]-1, A[1]+1]
        front_point = [A[0], A[1]+1]
        right_point = [A[0]+1, A[1]]
        back_point = [A[0], A[1]-1]
        left_point = [A[0]-1, A[1]]

        c1 = False if checkPoint(A) else matrix[A[0]][A[1]] == 1

        Q = [False]*4
        if not checkPoint(front_point):
            Q[0] = matrix[front_point[0]][front_point[1]] == 0
        if not checkPoint(right_point):
            Q[1] = matrix[right_point[0]][right_point[1]] == 0
        if not checkPoint(left_point):
            Q[2] = matrix[left_point[0]][left_point[1]] == 0
        if not checkPoint(back_point):
            Q[3] = matrix[back_point[0]][back_point[1]] == 0

        c2 = (np.array(Q)==True).any()
        if c1 and c2:
            boundary_points.append(A)
            Stack.insert(0,back_point)
            Stack.insert(0,back_down_diagonal_point)
            Stack.insert(0,right_point)
            Stack.insert(0,front_down_diagonal_point)
            Stack.insert(0,front_point)
            Stack.insert(0,front_up_diagonal_point)
            Stack.insert(0,left_point)
            Stack.insert(0,back_up_diagonal_point)
    return boundary_points


# def getPointsEdge(predicted):
#     up_pad = down_pad = left_pad = right_pad = 2
#     edgePredictions = []
#     for i in range(21):
#         slice = np.pad(predicted[i],[(up_pad, down_pad), (left_pad, right_pad)], mode='constant', constant_values=0)
#         filterEdge = ImageFilter.FIND_EDGES
#         # blur = ImageFilter.GaussianBlur(radius=2)
#         image = Image.fromarray(slice).filter(filterEdge)
#         image.show()
#         imgData = normalize(np.array(image))
#         points = list(np.array([*zip(*np.where(imgData > 0))]) - 2)
#         edgePredictions.append(points)
#     return edgePredictions

def reduceDensity(points,minDist):
    avoid = []
    for i in range( len(points)):
        for j in range( len(points)):
            if i!=j and (i not in avoid) and (j not in avoid):
                p2 = points[j]
                p1 = points[i]
                dist = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
                #checks distance
                if dist < minDist:
                    avoid.append(j)
    new_points = [points[t] for t in range(len(points)) if t not in avoid]
    return new_points

def BoundaryPoints(predicted):
    pred = []
    for i in range(21):
        slice = 1*(np.pad(predicted[i],[(2, 2), (2, 2)], mode='constant', constant_values=0) > 0)
        points = floodFill(slice)
        pred.append(points)
        p = np.array(points)
        print(len(p))
        if len(p) > 2:
            p = np.flip(p,axis = 1)
            plt.scatter(p[:,0],p[:,1])
            plt.imshow(slice)
            plt.show()

    return pred

def LabelMe_helper(predicted,resolution ,file,imgPath):
    # hull = getHulls(predicted, 0.3)
    shapes = []
    with open(file,'w+') as f:
        pointsEdge = BoundaryPoints(predicted)#getPointsEdge(predicted)
        for i in range(21):
            print(Classes[i])
            # points = get_polygon(hull[i])
            if len(list(pointsEdge[i])) > 10:
                points = np.array(pointsEdge[i]).astype(int)-2
                points = np.flip(points,axis = 1).tolist()
                # points = points.reshape((points.shape[0]*points.shape[1],points.shape[2])).tolist()
                # points = [list(t) for t in set(tuple(element) for element in points)]
                # points = sorted(points, key=lambda x: angle_and_distance(x,centroid(points)))
                points = reduceDensity(points,resolution)

                label = Classes[i]
                shapes.append({
                        "label":label,
                        "points":points,
                        "group_id": None,
                        "shape_type": "polygon",
                        "flags": {}
                    })
        data = {
            "version":"4.5.13",
            "flags": {},
            "shapes":shapes,
            "imagePath": imgPath,
            "imageData": None,
            "imageHeight": 416,
            "imageWidth": 416
        }
        f.seek(0)        # <--- should reset file position to the beginning.
        json.dump(data, f, indent=4)
        f.truncate()     # remove remaining part

def upsize(arr,accuracy):
    height,width,channels = arr.shape
    list = []
    for i in range(channels):
        img = Image.fromarray( (255*(predicted[:,:,i]>accuracy)).astype('uint8'), "L").resize((416,416))
        imgData = np.array(img)
        img.close()
        list.append(imgData)
    return np.array(list) # channels height width



Classes = ["sky","zombie","creeper","skeleton","spider","witch","enderman","husk","villager","cow",
"sheep","pig","olk_log","leaves","grass","dirt","stone","cobblestone","sand","iron","diamond"]

# Files_Path = Path(r".\Unannoted_images")

model = tf.keras.models.load_model("net2")
model.compile(optimizer='adam',
            loss='mse',
            metrics=['accuracy'])

location = Path("labels")
File_List = [*location.glob("*.json")]
print(File_List)
for File in File_List:
    file_name = File.stem
    ImagePath = f".\Annoted_images\{file_name}.png" #r"mob_dataset\Dataset\train\img\30.png"
    print(ImagePath)
    # MaskPath = Path(r"mob_dataset\Dataset\train\mask\mask_30")
    image = LoadImage(ImagePath).reshape((1,224,224,3))
    print(image,image.shape)
    # mask = LoadMask(MaskPath)

    predicted = model.predict(image).reshape((224,224,21))
    predicted = upsize(predicted,0.5) # shape(21,416,416)
    print(predicted,predicted.shape,predicted.max())

    LabelMe_helper(predicted,15,f".\labels\{file_name}.json",f"..\\Annoted_images\\{file_name}.png")
    print("done")

# for i in range(21):
#     displayImg([ image[0], mask[:,:,i], segmented[:,:,:,i] ])
