import cv2
import numpy as np
import pytesseract
import matplotlib.pyplot as plt


## TO STACK ALL THE IMAGES IN ONE WINDOW
def stackImages(imgArray, scale, lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    # width = imgArray[0][0].shape[1]
    # height = imgArray[0][0].shape[0]
    width=480
    height=640
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            # imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            imgArray[x] = cv2.resize(imgArray[x], (480, 640), None)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        hor_con = np.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth = int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        print(eachImgHeight)
        for d in range(0, rows):
            for c in range(0, cols):
                cv2.rectangle(ver, (c * eachImgWidth, eachImgHeight * d),
                              (c * eachImgWidth + len(lables[d][c]) * 13 + 27, 30 + eachImgHeight * d), (255, 255, 255),
                              cv2.FILLED)
                cv2.putText(ver, lables[d][c], (eachImgWidth * c + 10, eachImgHeight * d + 20), cv2.FONT_HERSHEY_COMPLEX,
                            0.7, (255, 0, 255), 2)
    return ver


def reorder(myPoints):
    myPoints = myPoints.reshape((4, 2))
    myPointsNew = np.zeros((4, 1, 2), dtype=np.int32)
    add = myPoints.sum(1)

    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]

    return myPointsNew


def biggestContour(contours):
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 5000:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest, max_area


def drawRectangle(img, biggest, thickness):
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)

    return img


def nothing(x):
    pass


def initializeTrackbars(intialTracbarVals=0):
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Threshold1", "Trackbars", 200, 255, nothing)
    cv2.createTrackbar("Threshold2", "Trackbars", 200, 255, nothing)


def valTrackbars():
    Threshold1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
    Threshold2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
    src = Threshold1, Threshold2
    return src


class ImageConstantROI():
    class CCCD(object):
        ROIS = {
            "name": [(300, 170, 310, 55)],
            "gender":[(320,260,200,50)],
            # "id": [(240, 200, 760, 390)],
            # "name": [(20, 890, 750, 165)]
        }
        # CHECK_ROI = [(313, 174, 597, 63)]

def display_img(cvImg):
    cvImg = cv2.cvtColor(cvImg, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(6,4))
    plt.imshow(cvImg)
    plt.show()

def cropImageRoi(image, roi):
    roi_cropped = image[
        int(roi[1]) : int(roi[1] + roi[3]), int(roi[0]) : int(roi[0] + roi[2])
    ]
    return roi_cropped

def preprocessing_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.multiply(gray, 1.5)
    blured1 = cv2.medianBlur(gray,3)
    blured2 = cv2.medianBlur(gray,51)
    divided = np.ma.divide(blured1, blured2).data
    normed = np.uint8(255*divided/divided.max())
    th, threshed = cv2.threshold(normed, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
    return threshed
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # thresh = cv2.threshold(gray, 0, 255,cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    # cv2.imshow("Otsu", thresh)
    # dist = cv2.distanceTransform(thresh, cv2.DIST_L2, 5)
    # dist = cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)
    # dist = (dist * 255).astype("uint8")
    # cv2.imshow("Dist", dist)
    # dist = cv2.threshold(dist, 0, 255,
    #                      cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    # cv2.imshow("Dist Otsu", dist)
    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    # opening = cv2.morphologyEx(dist, cv2.MORPH_OPEN, kernel)
    # cv2.imshow("Opening", opening)
    # cnts = cv2.findContours(opening.copy(), cv2.RETR_EXTERNAL,
    #                         cv2.CHAIN_APPROX_SIMPLE)
    # cnts = imutils.grab_contours(cnts)
    # chars = []
    # for c in cnts:
    #     (x, y, w, h) = cv2.boundingRect(c)
    #     if w >= 35 and h >= 100:
    #         chars.append(c)
    # chars = np.vstack([chars[i] for i in range(0, len(chars))])
    # hull = cv2.convexHull(chars)
    # mask = np.zeros(image.shape[:2], dtype="uint8")
    # cv2.drawContours(mask, [hull], -1, 255, -1)
    # mask = cv2.dilate(mask, None, iterations=2)
    # cv2.imshow("Mask", mask)
    # final = cv2.bitwise_and(opening, opening, mask=mask)
    # cv2.imshow("hu",final)
    # return thresh

def extractDataFromIdCard(img):
    MODEL_CONFIG = '-l eng --oem 1 --psm 6'
    l=[]
    for key, roi in ImageConstantROI.CCCD.ROIS.items():
        data = ''
        for r in roi:
            crop_img = cropImageRoi(img, r)
            crop_img = preprocessing_image(crop_img)
            display_img(crop_img)
            data += pytesseract.image_to_string(crop_img, config = MODEL_CONFIG) + ' '
        print(f"{key} : {data.strip()}")
        l.append(data.strip())
    return (l)