"""Remove third-party place labels and pins from the satellite image (keeps road names and
the Kampala Marriott Hotel label). Uses texture-aware FSR inpainting (opencv-contrib) so the
cleaned areas keep the surrounding detail instead of blurring.
Input satellite_original.png -> output satellite.png."""
import os, cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
im = cv2.imread(os.path.join(HERE, "satellite_original.png"))
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
boxes = [(288, 420, 425, 461), (66, 528, 302, 565), (0, 588, 135, 635), (440, 573, 592, 620),
         (518, 743, 677, 782), (453, 785, 682, 822), (0, 788, 12, 830), (403, 818, 422, 830)]
pins = [(305, 437), (85, 546), (574, 592), (537, 762), (472, 804)]
# label text = white fill + dark halo; pins = saturated colour or white/grey circle
textlike = ((hsv[..., 2] > 175) & (hsv[..., 1] < 50)) | (hsv[..., 1] > 110)
mask = np.zeros(im.shape[:2], np.uint8)
for x1, y1, x2, y2 in boxes:
    mask[y1:y2, x1:x2] = textlike[y1:y2, x1:x2] * 255
mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=3)
for cx, cy in pins:
    cv2.circle(mask, (cx, cy), 17, 255, -1)
out = im.copy()
PAD = 40
for x1, y1, x2, y2 in boxes:
    a, b = max(0, x1 - PAD), max(0, y1 - PAD)
    c, d = min(im.shape[1], x2 + PAD), min(im.shape[0], y2 + PAD)
    roi = out[b:d, a:c].copy()
    valid = (mask[b:d, a:c] == 0).astype(np.uint8) * 255
    res = np.zeros_like(roi)
    cv2.xphoto.inpaint(roi, valid, res, cv2.xphoto.INPAINT_FSR_BEST)
    out[b:d, a:c] = res
cv2.imwrite(os.path.join(HERE, "satellite.png"), out)
print("ok")

# --- clean FSR artefacts: saturated specks inside the repaired areas -> small Telea fill
hsv2 = cv2.cvtColor(out, cv2.COLOR_BGR2HSV)
spot = ((hsv2[..., 1] > 150) & (cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=3) > 0)).astype(np.uint8) * 255
spot = cv2.dilate(spot, np.ones((3, 3), np.uint8), iterations=2)
out = cv2.inpaint(out, spot, 3, cv2.INPAINT_TELEA)
cv2.imwrite(os.path.join(HERE, "satellite.png"), out)
print("artefacts cleaned:", int((spot > 0).sum()))
