import pygame.transform


def scaleImage(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blitRotateCenter(win, image, topLeft, angle):
    rotatedImage = pygame.transform.rotate(image, angle)
    newRect = rotatedImage.get_rect(
        center=image.get_rect(topleft=topLeft).center)
    win.blit(rotatedImage, newRect.topleft)

def blitTextCenter(win, font, text):
    render = font.render(text, 1, (200,200,200))
    win.blit(render, (win.get_width()/2 - render.get_width()/2, win.get_height()))