import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib.patches import Arc
from scipy.ndimage import generate_binary_structure, maximum_filter
from scipy.spatial.distance import cdist
import os
import math

def hough_peaks(H, numpeaks=1, threshold=None, nHoodSize=None):
    # Set default values
    if threshold is None:
        threshold = 0.7 * np.max(H)
    if nHoodSize is None:
        nHoodSize = np.floor(np.array(H.shape) / 100.0) * 2 + 1

    # Find values greater than threshold
    peaks = np.argwhere(H > threshold)

    # Apply neighborhood suppression
    i = 0
    while i < len(peaks):
        max_peak_x = peaks[i][0] + (nHoodSize[0] - 1)//2
        min_peak_x = peaks[i][0] - (nHoodSize[0] - 1)//2
        max_peak_y = peaks[i][1] + (nHoodSize[1] - 1)//2
        min_peak_y = peaks[i][1] - (nHoodSize[1] - 1)//2

        in_range = np.logical_and(peaks[:, 0] <= max_peak_x, peaks[:, 0] >= min_peak_x)
        in_range = np.logical_and(in_range, peaks[:, 1] <= max_peak_y)
        in_range = np.logical_and(in_range, peaks[:, 1] >= min_peak_y)
        in_range[i] = False

        if np.any(in_range):
            # Find maximum vote and remove others
            max_idx = np.argmax(H[peaks[in_range][:, 0], peaks[in_range][:, 1]])
            in_range_idx = np.argwhere(in_range).reshape(-1)
            max_peak_idx = in_range_idx[max_idx]
            peaks = np.delete(peaks, in_range_idx[in_range_idx != max_peak_idx], axis=0)

        i += 1

    # Order based on max
    peak_vals = H[peaks[:, 0], peaks[:, 1]]
    sorted_idxs = np.argsort(peak_vals)[::-1][:numpeaks]
    peaks = peaks[sorted_idxs]

    return peaks

def hough_circles_acc(BW, radius):
    # Compute Hough accumulator array for finding circles.
    #
    # BW: Binary (black and white) image containing edge pixels
    # radius: Radius of circles to look for, in pixels

    # Initialize accumulator array
    H = np.zeros_like(BW)
    for i in range(BW.shape[0]):
        for j in range(BW.shape[1]):
            if BW[i, j] > 0:
                theta = np.arange(0, 361)
                x_val = np.round((radius*np.cos(np.deg2rad(theta))) + j)
                y_val = np.round((radius*np.sin(np.deg2rad(theta))) + i)

                for k in range(len(x_val)):
                    if (x_val[k] > 0 and x_val[k] < H.shape[0] and y_val[k] > 0 and y_val[k] < H.shape[1]):
                        H[int(x_val[k]), int(y_val[k])] = H[int(x_val[k]), int(y_val[k])] + 1

    return H

def find_circles(BW, radius_range, thresh, nhood):
    centers = []
    radii = []
    votes = []

    for i in range(len(radius_range)):
        H = hough_circles_acc(BW, radius_range[i])
        cur_centers = hough_peaks(H, numpeaks=5, threshold=thresh * np.max(H), nHoodSize=(nhood, nhood))
        for j in range(cur_centers.shape[0]):
            cur_vote = H[cur_centers[j,0], cur_centers[j,1]]
            votes.append(cur_vote)
        centers.append(cur_centers)
        radii.append(np.full((cur_centers.shape[0], 1), radius_range[i]))

    centers = np.concatenate(centers, axis=0)
    radii = np.concatenate(radii, axis=0)
    
    # Remove centers that are too close based on votes and neighborhood size\
    in_range = np.ones(centers.shape[0], dtype=bool)  # all centers are initially in range

    for i in range(centers.shape[0]):
        # Calculate distance between center i and all other centers
        dist = np.sqrt(np.sum((centers - centers[i])**2, axis=1))

        # Find the indexes of the other centers that are within the specified neighborhood size
        other_idx = np.where((dist <= nhood) & (in_range))[0]
        if len(other_idx) > 1:
            # Keep the index of the center with the highest votes within the neighborhood
            kept_idx = np.argmax(np.take(votes, other_idx))
            max_idx = other_idx[kept_idx]

            # Remove the indexes of the other centers from the in_range array
            in_range[other_idx] = False
            in_range[max_idx] = True

    # Filter centers, radii, and votes using the in_range array
    centers = centers[in_range]
    radii = radii[in_range]
    votes = [votes[i] for i in range(len(votes)) if in_range[i]]

    return centers, radii, votes

def find_arcs(centers, radii, votes, img):
    arc_list = []
    x, y = np.where(img != 0)

    for i in range(len(centers)):
        center = centers[i]
        r = radii[i]

        cx = center[0]
        cy = center[1]

        dist = np.sqrt((y - cx)**2 + (x - cy)**2)

        # Find the skeleton pixels that are within the circle
        idx = np.where((dist < r + 2) & (dist > r - 2))[0]
        if len(idx) == 0:
            continue

        # Extract the coordinates of the skeleton pixels that are within the circle
        ex, ey = y[idx], x[idx]

        # Perform k-means clustering to separate the skeleton pixels into two groups
        kmeans = KMeans(n_clusters=3, init='random').fit(np.column_stack((ex, ey)))
        kcenters = kmeans.cluster_centers_
        
        labels = kmeans.labels_

        # Determine which cluster contains the majority of the skeleton pixels
        if np.sqrt((kcenters[0][1] - kcenters[1][1])**2 + (kcenters[0][0] - kcenters[1][0])**2) > r/2:
            majority_label = np.argmax(np.bincount(labels))

            # Extract the coordinates of the skeleton pixels in the majority cluster
            ex, ey = ex[labels == majority_label], ey[labels == majority_label]

        # Compute the angle of each skeleton pixel relative to the circle center
        angles = np.rad2deg(np.arctan2(-cy + ey, ex - cx))

        # Sort the angles in ascending order
        idx = np.argsort(angles)
        angles, ex, ey = angles[idx], ex[idx], ey[idx]

        # Compute the starting and ending angles of the arc
        start_angle, end_angle = angles[0], angles[-1]
        start_idx = (ex[0], ey[0])
        end_idx = (ex[-1], ey[-1])

        # Add the arc to the list
        arc_list.append([(cx, cy), r[0], start_angle, end_angle, start_idx, end_idx])

    return arc_list

def find_lines(img):
    lines = cv2.HoughLinesP(img, rho=1, theta=np.pi/180, threshold=10, minLineLength=10, maxLineGap=5)

    line_segments = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        line_segments.append([(x1, y1), (x2, y2)])

    return line_segments

def get_image(file_path):

    # img = cv2.imread(os.path.join(os.path.dirname(__file__), file_path), cv2.THRESH_BINARY)
    img = cv2.imread(file_path, cv2.THRESH_BINARY)
    # kernel2 = np.ones((5, 5), np.float32)/25
    
    # Applying the filter
    # img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel2)

    return img

def circle_processing(centers, radii, votes):
    good_circles = np.logical_and(votes > 0.6 * np.max(votes), votes > np.array([60])[0])
    centers = centers[np.squeeze(good_circles)]
    radii = radii[good_circles]
    votes = np.take(votes, np.where(good_circles))[0]

    return centers, radii, votes

def connect_nd(ends):
    d = np.diff(ends, axis=0)[0]
    j = np.argmax(np.abs(d))
    D = d[j]
    aD = np.abs(D)
    return ends[0] + (np.outer(np.arange(aD + 1), d) + (aD//2)) // aD



def remove_overlap_lines(line_segments, arc_list):

    arc_list = arc_list
    line_segments = line_segments

    overlapping_line_segment_idx = []
    
    for arc in arc_list:
        center, r, start_angle, end_angle, start_idx, end_idx = arc
        
        points_list = []

        for j in range(round(start_angle), round(end_angle)):
            x_val = center[0] + round(r*math.cos(math.radians(j)))
            y_val = center[1] + round(r*math.sin(math.radians(j)))
            points_list.append([x_val,y_val])

        points_list = np.array(points_list)

        

        for i in range(len(line_segments)):
            line = line_segments[i]
            points = connect_nd(np.array( [[line[0][0], line[0][1]], [line[1][0], line[1][1]]] ))
            intersecting_points = np.array([x for x in set(tuple(x) for x in points) & set(tuple(x) for x in points_list)])
            if len(intersecting_points)/len(points) >= 0.25:
                # line_segments = np.delete(line_segments, i, 0)
                overlapping_line_segment_idx.append(i)

    line_segments_new = [row for i, row in enumerate(line_segments) if i not in overlapping_line_segment_idx]

    return line_segments_new
                
            


        


if __name__ == "__main__":

    img = get_image(os.path.join(os.path.dirname(__file__), "prototyping/chars/myfile68.bmp"))

    line_segments = find_lines(img)




    centers, radii, votes = find_circles(img, range(20,100,5), 0.6, 20)

    centers, radii, votes = circle_processing(centers, radii, votes)

    arc_list = find_arcs(centers, radii, votes, img)

    line_segments = remove_overlap_lines(line_segments, arc_list)

    fig, ax = plt.subplots()
    # ax.imshow(cv2.imread("C:/Users/yasse/Desktop/Senior Design/whiteboard-typewriter/ui/skeletonized/ss2.png"))
    for line in line_segments:
        x1, y1 = line[0]
        x2, y2 = line[1]
        ax.plot([x1, x2], [y1, y2], color='r')

    # Iterate over arc_list and draw arcs on image
    for arc in arc_list:
        center, r, start_angle, end_angle, start_idx, end_idx = arc
        thickness = 5
        color = (255, 255, 255) # Red color

        # center = (int(cx), int(cy))

        # Draw arc on image
        # cv2.circle(img, center, int(r), (255,255,255), 2)
        cv2.ellipse(img, center, (int(r), int(r)), 0, start_angle, end_angle, color, thickness)
        
        # ellipse_img = cv2.ellipse(img, center, (int(r), int(r)), 0, start_angle, end_angle, color, thickness)
        # print(np.where(ellipse_img == 1))
        # print(cv2.ellipse(img, center, (int(r), int(r)), 0, start_angle, end_angle, color, thickness))


    # print(arc_list)
    # print(line_segments)

    # Display image with circles
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.show()