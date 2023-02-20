from PIL.ImageColor import getcolor


def rgbToDec(rgb: str):
    color = getcolor(rgb, 'RGB')
    color = [c / 255 for c in color]
    return color
