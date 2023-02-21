import cv2 
import numpy as np 
  
def binarize(path):
    # path to input image is specified and  
    # image is loaded with imread command 
    image1 = cv2.imread('./chars/' + path) 
    
    # cv2.cvtColor is applied over the
    # image input with applied parameters
    # to convert the image in grayscale 
    img = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    
    # applying different thresholding 
    # techniques on the input image
    # all pixels value above 120 will 
    # be set to 255
    ret, thresh1 = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
    
    # the window showing output images
    # with the corresponding thresholding 
    # techniques applied to the input images
    cv2.imwrite('./binarized/' + path, thresh1)
        
    # De-allocate any associated memory usage  
    if cv2.waitKey(0) & 0xff == 27: 
        cv2.destroyAllWindows() 
