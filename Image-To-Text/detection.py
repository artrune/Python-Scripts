import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe"

img = cv2.imread('./Untitled.png')

text = pytesseract.image_to_string(img)
print(text)