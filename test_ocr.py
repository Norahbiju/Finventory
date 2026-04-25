from PIL import Image
import pytesseract
image = Image.open('C:/Users/USER/.gemini/antigravity/brain/7fc40fa6-274b-40ee-8f9b-5a3ab7a6f826/media__1777090419539.png')
text = pytesseract.image_to_string(image)
print('--- OCR TEXT START ---')
print(text)
print('--- OCR TEXT END ---')
