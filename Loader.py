# Import required packages
import cv2
import pytesseract
import random
import numpy as np
from pytesseract import Output

line_thickness = 4
epslon = 18

#finds if distance within blocks are whitin the threshold of epslon
def is_close(blockA, blockB):
    for i in range(4):
        for j in range(4):
            dist = np.sqrt(np.square(blockA[i][0]-blockB[j][0])+ np.square(blockA[i][1]-blockB[j][1]))
            if dist<=epslon:
                return True
    return False

def draw(blocks ,clusters, image):
    cluster_squares = {}
    for  block in blocks:
        if block[4]!="":
            cluster_labe = clusters[block[4]]
            if cluster_labe in cluster_squares.keys():
                if cluster_squares[cluster_labe][0] > block[0][0]:
                    cluster_squares[cluster_labe][0] = block[0][0]
                if cluster_squares[cluster_labe][1] > block[0][1]:
                    cluster_squares[cluster_labe][1] = block[0][1]
                if cluster_squares[cluster_labe][2] < block[3][0]:
                    cluster_squares[cluster_labe][2] = block[3][0]
                if cluster_squares[cluster_labe][3] < block[3][1]:
                    cluster_squares[cluster_labe][3] = block[3][1]
            else:
                cluster_squares[cluster_labe] = [block[0][0], block[0][1], block[3][0], block[3][1]]
        else:
            (x1,y1,x2,y2) = (block[0][0], block[0][1], block[3][0], block[3][1])
            image = cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    for squares in cluster_squares.values():
        image = cv2.rectangle(image, (squares[0], squares[1]), (squares[2], squares[3]), (0, 255, 0), 2)

#clusters the detected blocks using Custom DBSCAN
def cluster_blocks(blocks, image):
    #dictonary holds the color labes of a cluster
    cluster= {}
    #updates the cluster key of blocks
    cluster_key = 1
    for i in range(len(blocks)):
        for j in range(i+1,len(blocks)):
            if is_close(blocks[i],blocks[j])==True:
                if blocks[i][4] =="" and blocks[j][4]!="":
                    blocks[i][4] = blocks[j][4]
                elif blocks[j][4] =="" and blocks[i][4]!="":
                    blocks[j][4] = blocks[i][4]
                elif blocks[j][4] =="" and blocks[i][4]=="": 
                    blocks[j][4] = cluster_key
                    blocks[i][4] = cluster_key
                    cluster[cluster_key] = cluster_key
                    cluster_key = cluster_key+1
                else:
                    cluster[blocks[i][4]] = cluster[blocks[j][4]]
    draw(blocks,cluster, image)
    print(cluster)

def detect_blocks(boxes, blocks):
    for i in range(len(boxes)):
        bound = True
        #below loop eleminates the bigger bounding boxes which has boxes within
        for j in range(i+1,len(boxes)):
            if boxes[i][0]<=boxes[j][0] and boxes[i][1]<=boxes[j][1] and boxes[i][2]>=boxes[j][2] and boxes[i][3]>=boxes[j][3]:
                bound = False
                break
        (x1, y1, x2, y2) = (boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3])
        #makes sure it is not a big bounding box and also not a box containing a line
        if bound==True and np.abs(x1-x2)>line_thickness and np.abs(y1-y2)>line_thickness:
            blocks.append([[x1,y1],[x1,y2],[x2,y1],[x2,y2],""])


# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Read image from which text needs to be extracted
img = cv2.imread("C:\\Users\\GHOSH\\OneDrive\\Documents\\GitHub\\CNN\\Images\\M11.png")

# configurations
config = ('-l eng --oem 1 --psm 3')
text = pytesseract.image_to_string(img, config=config)
# print text
text = text.split('\n')
print(text)



# run tesseract, returning the bounding boxes
d = pytesseract.image_to_data(img, output_type=Output.DICT)
keys = list(d.keys())

im2 = img.copy()
boxes = []
blocks = []
# find the bounding boxes on the image
n_boxes = len(d['level'])
for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    boxes.append([x,y,x+w,y+h])

detect_blocks(boxes, blocks)
cluster_blocks(blocks, im2)
im2 = cv2.resize(im2, (500, 900))
cv2.imshow("",im2)


