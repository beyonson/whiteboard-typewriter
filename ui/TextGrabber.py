from PIL import ImageGrab, Image
from Preprocessing import *

def scrotChar(xPos, yPos, fontSize, charsTyped):
    shift = charsTyped*11.36
    ss_region = (xPos+shift, yPos, xPos+shift+11.36, yPos+30)
    ss_name = 'ss' + str(charsTyped) + '.jpg'
    ss_img = ImageGrab.grab(ss_region)
    ss_img = ss_img.resize((110, 300))
    ss_img.save('chars/' + ss_name)
    binarize(ss_name)