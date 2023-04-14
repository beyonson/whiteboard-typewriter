# find edges using Canny edge detection
edges = cv2.Canny(gray, 100, 200)

# set up accumulator array
acc = np.zeros_like(edges)

# perform RHT
iterations = 0
while iterations < max_iterations:
    # randomly select 3 points on the ellipse
    points = np.random.choice(np.argwhere(edges), size=(3,2))
    x1, y1 = points[0]
    x2, y2 = points[1]
    x3, y3 = points[2]
    
    # fit tangent lines using least squares
    pts = np.array([[x1,y1], [x2,y2], [x3,y3]])
    vx,vy,x,y = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01)
    a = vy/vx
    b = -1
    c = y - a*x
    
    # find intersection points of tangent lines
    x4 = (b*(b*x3 - a*y3) - a*c) / (a**2 + b**2)
    y4 = (a*(-b*x3 + a*y3) - b*c) / (a**2 + b**2)
    x5 = (b*(b*x2 - a*y2) - a*c) / (a**2 + b**2)
    y5 = (a*(-b*x2 + a*y2) - b*c) / (a**2 + b**2)
    
    # find center of ellipse
    center_x = (x4 + x5) / 2
    center_y = (y4 + y5) / 2
    
    # find parameters of ellipse
    dist1 = np.sqrt((x1 - center_x)**2 + (y1 - center_y)**2)
    dist2 = np.sqrt((x2 - center_x)**2 + (y2 - center_y)**2)
    dist3 = np.sqrt((x3 - center_x)**2 + (y3 - center_y)**2)
    a = np.sqrt((dist1**2 + dist2**2 + dist3**2) / 3)
    b = a * np.sqrt(1 - np.min([dist1,dist2,dist3])**2 / a**2)
    c = np.sqrt(a**2 - b**2)
    angle = np.arctan2((y2-y1),(x2-x1))
    
    # update accumulator array
    ellipse_params = [center_x, center_y, a, b, angle]
    ellipse_found = False
    for i in range(acc.shape[0]):
        for j in range(acc.shape[1]):
            if acc[i,j] > 0:
                # compare similarity of ellipses
                params = np.array([j,i,acc[i,j],0,0])
                similarity = cv2.compareHist(cv2.ellipse(img, tuple(params[:2]), tuple(params[2:]), 0), cv2.ellipse(img, tuple(ellipse_params[:2]), tuple(ellipse_params[2:]), 0), cv2.HISTCMP_CORREL)
                if similarity > threshold:
                    acc[i,j] += 1
                    ellipse_found = True
                    break
       
