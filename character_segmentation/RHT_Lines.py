import random
import cv2
import numpy as np

def rht(image, num_iterations, tolerance, threshold):
    active_points = find_active_points(image)
    accumulator = {}
    for i in range(num_iterations):
        p1, p2 = random.sample(active_points, 2)
        if p1[0] == p2[0]:  # vertical line
            a = float('inf')
            b = p1[0]
        else:
            a, b = solve_line_equation(p1, p2)
        for key in accumulator:
            # print(key)
            if within_tolerance(key, (a,b), tolerance):
                accumulator[key] += 1
                break
        else:
            accumulator[(a,b)] = 1

        for (a, b), count in accumulator.items():
            if count >= threshold:
                mark_line_in_image(image, (a, b))

        # if accumulator[(a,b)] >= threshold:
        #     mark_line_in_image(image, (a,b))

    return image

def find_active_points(image):
    active_points = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i,j] >= 1:
                active_points.append((i,j))
    return active_points

def solve_line_equation(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    a = (y2 - y1) / (x2 - x1)
    b = y1 - a*x1
    return a, b

def within_tolerance(p1, p2, tolerance):
    return abs(p1[0] - p2[0]) <= tolerance and abs(p1[1] - p2[1]) <= tolerance

def mark_line_in_image(image, line):
    a, b = line
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if abs(a*i + b - j) <= 1:
                image[i,j] = 2

if __name__ == "__main__":

    img = cv2.imread("myfile65.bmp", cv2.THRESH_BINARY)

    new_img = rht(img, 100, 1, 2)

    cv2.imshow('Output', new_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


