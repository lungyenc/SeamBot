"""

This module takes a image downloaded from a url and the new dimension as
arguments. It returns the image that seam-carved to the new dimension.

Contact: Lung-Yen Chen, lungyen@pricneton.edu

"""
import requests
import numpy as np
import cv2
from numba import jit
import time


def seam_carve(image_downloaded, filename, newX, newY):
    img_array = np.array(bytearray(image_downloaded.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, 1).astype(np.float64)

    y, x, c = img.shape
    removeX = x - newX
    removeY = y - newY

    t = time.time()

    for i in range(removeX):
        img = seam_carve_helper(img)

    img = img_rotate(img)
    
    for i in range(removeY):
        img = seam_carve_helper(img)

    img = img_rotate_anti(img)

    cv2.imwrite(filename, img.astype(np.uint8))

# Seam carving helper
def seam_carve_helper(img):
    energy = cal_energy(img)
    seam = find_seam(energy)
    img = remove_seam(img, seam)
    return img

# Caculate the energy map for the entire image
def cal_energy(img):
    b, g, r = cv2.split(img)
    b_energy = (np.absolute(cv2.Scharr(b, -1, 1, 0)) + 
                np.absolute(cv2.Scharr(b, -1, 0, 1)))
    g_energy = (np.absolute(cv2.Scharr(g, -1, 1, 0)) + 
                np.absolute(cv2.Scharr(g, -1, 0, 1)))
    r_energy = (np.absolute(cv2.Scharr(r, -1, 1, 0)) + 
                np.absolute(cv2.Scharr(r, -1, 0, 1)))
    return b_energy + g_energy + r_energy

# Use dynamic programming to find the shortest path on the energy map
@jit(nopython = True, parallel = True)
def find_seam(energy):
    m, n = energy.shape
    seam = np.zeros((m,), dtype=np.uint32)
    for i in range(1, m):
        for j in range(0, n):
            if j == 0:
                energy[i][j] += min(energy[i - 1][0], energy[i - 1][j + 1])
            elif j == n - 1:
                energy[i][j] += min(energy[i - 1][j - 1], energy[i - 1][j])
            else:
                energy[i][j] += min(min(energy[i - 1][j], energy[i - 1][j - 1]
                                ), energy[i - 1][j + 1])
    seam[-1] = np.argmin(energy[-1])
    for row in range(m - 2, -1, -1):
        prv_x = seam[row + 1]
        if prv_x == 0:
            seam[row] = np.argmin(energy[row][0 : 2])
        else:
            seam[row] = (np.argmin(energy[row]
                    [prv_x - 1: min(prv_x + 2, n - 1)]) + prv_x - 1)
    return seam

# Remove the minimum seam
def remove_seam(img, seam):
    m, n, c = img.shape
    result = np.zeros((m, n - 1, c))
    for i in range(m):
        for k in range(c):
            result[i, :, k] = np.delete(img[i, :, k], seam[i])
    return result
    
def img_rotate(img):
    return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

def img_rotate_anti(img):
    return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)


