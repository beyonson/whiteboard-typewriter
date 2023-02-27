import cv2 
import numpy as np 
  
def processChar(path):
    image1 = cv2.imread('./chars/' + path) 
    img = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY_INV)
    cv2.imwrite('./binarized/' + path, thresh1)

    size = np.size(thresh1)
    skel = np.zeros(thresh1.shape,np.uint8)
    
    ret,img = cv2.threshold(thresh1,127,255,0)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    done = False
    
    skel = cv2.ximgproc.thinning(img)
    
    cv2.imwrite("./skeletonized/" + path, skel)
    if cv2.waitKey(0) & 0xff == 27: 
        cv2.destroyAllWindows() 
