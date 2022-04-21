from PIL import Image

img = Image.open('img.png')

w, h = img.size

print(w, h)

for y in range(0, 200, 50):
    for x in range(0, 120, 40):
        newImg = img.crop((x, y, x + 40, y + 50))
        newImg.save(f'{x}_{y}.png')