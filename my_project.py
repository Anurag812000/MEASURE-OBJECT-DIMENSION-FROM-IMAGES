"""
Filename: my_project.py
Usage: This script will measure dimension(in cm) of different objects in the frame
using a reference object of known dimension.
The object with known dimension must be the leftmost object.
Author: Aryan Gupta, Anurag Kumar Sahu, Anjali Singh.
"""
# Import necessary packages...
from scipy.spatial.distance import euclidean
from imutils import perspective
from imutils import contours
import numpy as np
import imutils
import cv2

# midpoint method will compute the midpoint between two set of (x,y) coordinate...
def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# img_path variable will hold the path of our image and
# load the input image and display the sample3.jpg...
img_path = "sample4.jpg"
image = cv2.imread(img_path)
cv2.imshow("Input image", image)
cv2.waitKey(0)

# convert image to grayscale, and blur(smooth) it slightly to remove noise...
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (3, 3), 0)
cv2.imshow("Blurred image", gray)
cv2.waitKey(0)

# perform edge detection, then perform a dilation + erosion to
# close gaps in between object edges in the edge map...
edged = cv2.Canny(gray, 50, 100)

cv2.imshow("canny image", edged)
cv2.waitKey(0)
edged = cv2.dilate(edged, None, iterations=1)
cv2.imshow("dilate image", edged)
cv2.waitKey(0)
edged = cv2.erode(edged, None, iterations=1)
cv2.imshow("erode image", edged)
cv2.waitKey(0)

# find contours(i.e, outlines) that corresponds to the objects in our edge map...
items = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(items)

# sort the contours from left-to-right (hepls us to ditact our reference object) and
# initialize the 'pixels_Per_cm' calibration variable to None...
(cnts, _) = contours.sort_contours(cnts)
pixels_Per_cm = None

# loop over the contours individually...
for c in cnts:
# if the contour is not sufficiently large, discard it...
    if cv2.contourArea(c) < 100:
        continue
    rect = cv2.minAreaRect(c)
    BoxPoints = cv2.boxPoints(rect)
    BoxPoints = np.array(BoxPoints, dtype="int")

	# arrange our rotated bounding rectangle coordinates such that they appear
	# in top-left, top-right, bottom-right, and bottom-left order(i.e, clockwise)...
    BoxPoints = perspective.order_points(BoxPoints)

    # draw the outline of the object in black colour...
    cv2.drawContours(image, [BoxPoints.astype("int")], -1, (0, 0, 0), 2)

	# This line will draw small red circles as a vertices of the bounding rectangular BoxPoints
    # by looping over the original points...
    for (x, y) in BoxPoints:
        cv2.circle(image, (int(x), int(y)), 5, (0, 0, 255), -1, cv2.FILLED)

 	# unpack the ordered bounding BoxPoints, then compute the midpoint
	# between the top-left and top-right coordinates, followed by
	# the midpoint between bottom-left and bottom-right coordinates...
    (tl, tr, br, bl) = BoxPoints
    (tltrX, tltrY) = midpoint(tl, tr)
    (blbrX, blbrY) = midpoint(bl, br)

	# also compute the midpoint between the top-left + bottom-left points,
	# followed by the midpoint between the top-right and bottom-right...
    (tlblX, tlblY) = midpoint(tl, bl)
    (trbrX, trbrY) = midpoint(tr, br)

	# it will draw the blue midpoints on our image...
    cv2.circle(image, (int(tltrX), int(tltrY)), 5, (89, 33, 32), -1, cv2.FILLED)
    cv2.circle(image, (int(blbrX), int(blbrY)), 5, (89, 33, 32), -1, cv2.FILLED)
    cv2.circle(image, (int(tlblX), int(tlblY)), 5, (89, 33, 32), -1, cv2.FILLED)
    cv2.circle(image, (int(trbrX), int(trbrY)), 5, (89, 33, 32), -1, cv2.FILLED)
    # cv2.imshow("image image", image)
    # cv2.waitKey(0)

	# it will connect the blue midpoint by drawing pink lines between the midpoints...
    cv2.line(image, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)), (255, 0, 255), 1) # Vertical line
    cv2.line(image, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)), (255, 0, 255), 1) # Horizontal line

	# compute the Euclidean distance between the blue midpoints,
    # dA variable will contain the height distance in pixels and
    # dB will hold width distance in pixels
    dA = euclidean((tltrX, tltrY), (blbrX, blbrY))
    dB = euclidean((tlblX, tlblY), (trbrX, trbrY))

    # here we make a check on Line 101 to see
	# if our pixels_Per_cm variable has not been initialized, then
	# compute it as the ratio of pixels to supplied metric
	# (in this case, cm)...
    if pixels_Per_cm is None:
        width_in_cm = 3
        pixels_Per_cm = dB / width_in_cm
        """
        pixels_Per_cm = object_width / known_width.
        The square Box has a known_width 2.2cm.
        """
	# compute the dimension of object(in cm) by
    # dividing the respective euclidean distance by the pixels_Per_cm value...
    dimA = dA / pixels_Per_cm
    dimB = dB / pixels_Per_cm

    # draw the dimension of objects in brown color on our output image...
    cv2.putText(image, "{:.1f}cm".format(dimA), (int(tltrX - 15), int(tltrY -10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (33, 67, 101), 1)
    cv2.putText(image, "{:.1f}cm".format(dimB), (int(trbrX + 10), int(trbrY)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (33, 67, 101), 1)

    # display the output image...
    cv2.imshow("Output image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
