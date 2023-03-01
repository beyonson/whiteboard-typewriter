import cv2
import numpy as np
 
# Create an image with text on it
img1 = cv2.imread('./binarized/ss0.jpg') 
thin = cv2.ximgproc.thinning(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY))
cv2.imshow('thinned',thin)
cv2.waitKey(0)