"""Remove third-party place labels and pins from the satellite image (keeps road names and
the Kampala Marriott Hotel label). Input satellite_original.png -> output satellite.png."""
import os, cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
im = cv2.imread(os.path.join(HERE, "satellite_original.png"))
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
boxes = [(288, 420, 425, 461), (66, 528, 302, 565), (0, 588, 135, 635), (440, 573, 592, 620),
         (518, 743, 677, 782), (453, 785, 682, 822), (0, 788, 12, 830), (403, 818, 422, 830)]
pins = [(305, 437), (85, 546), (574, 592), (537, 762), (472, 804)]
textlike = ((hsv[..., 2] > 185) & (hsv[..., 1] < 45)) | (hsv[..., 1] > 110)
mask = np.zeros(im.shape[:2], np.uint8)
for x1, y1, x2, y2 in boxes:
    mask[y1:y2, x1:x2] = textlike[y1:y2, x1:x2] * 255
mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=4)
for cx, cy in pins:
    cv2.circle(mask, (cx, cy), 16, 255, -1)
out = cv2.inpaint(im, mask, 6, cv2.INPAINT_TELEA)
cv2.imwrite(os.path.join(HERE, "satellite.png"), out)
print("ok")
