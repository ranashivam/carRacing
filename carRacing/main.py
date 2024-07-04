#######Test Comment#######

import math
import time

import pygame
from utils import *
pygame.font.init()


GRASS = scaleImage(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scaleImage(pygame.image.load("imgs/track.png"), 0.9)
TRACK_BORDER = scaleImage(pygame.image.load("imgs/track-border.png"), 0.9)
FINISH = scaleImage(pygame.image.load("imgs/finish.png"), 0.75)
FINISH_POSITION = (140,250)
RED_CAR = scaleImage(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scaleImage(pygame.image.load("imgs/green-car.png"), 0.55)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH_MASK = pygame.mask.from_surface(FINISH)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
pygame.display.set_caption("Racing Game!")
# WIDTH, HEIGHT = 500, 500
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

PATH = [(175, 119), (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377), (176, 388), (178, 260)]

class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.levelStartTime = 0
    def nextLevel(self):
        self.level += 1
        self.started = False
    def reset(self):
        self.level = 1
        self.started = False
        self.levelStartTime = 0
    def gameFinished(self):
        return self.level > self.LEVELS

    def startLevel(self):
        self.started = True
        self.levelStartTime = time.time()

    def getLevelTime(self):
        if not self.started:
            return 0
        else:
            return round(time.time() - self.levelStartTime)


pygame.display.set_caption("Racing Game!")

clock = pygame.time.Clock()

class abstrctClass:
    def __init__(self, maxVel, rotationVel):
        self.img = self.IMG
        self.maxVel = maxVel
        self.vel = 0
        self.rotationVel = rotationVel
        self.angle = 0
        self.x , self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotationVel
        elif right:
            self.angle -= self.rotationVel

    def draw(self, win):
        blitRotateCenter(win, self.img,(self.x, self.y), self.angle)

    def moveForward(self):
        self.vel = min(self.vel + self.acceleration, self.maxVel)
        self.move()

    def moveBackward(self):
        self.vel = max(self.vel - self.acceleration, -self.maxVel)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        carMask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(carMask, offset)
        return poi

    def reset(self):
        self.x , self.y = self.START_POS
        self.angle = 0
        self.move()

class playerCar(abstrctClass):
    IMG = RED_CAR
    START_POS = (180, 200)

    def reduceSpeed(self):
        self.vel = max(self.vel - self.acceleration/2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


class computerCar(abstrctClass):
    IMG = GREEN_CAR
    START_POS = (150, 200)

    def __init__(self, maxVel, rotationVel, path=[]):
        super().__init__(maxVel, rotationVel)
        self.path = path
        self.currentPoint = 0
        self.vel = maxVel

    def drawPoint(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255,0,0), point, 5)

    def draw(self, win):
        super().draw(win)
        # self.drawPoint(win)


    def calculateAngle(self):
        targetX, targetY = self.path[self.currentPoint]
        xDiff = targetX - self.x
        yDiff = targetY -self.y


        if yDiff == 0:
            desiredRadianAngel = math.pi / 2
        else:
            desiredRadianAngel = math.atan(xDiff/yDiff)

        if targetY > self.y:
            desiredRadianAngel += math.pi

        differenceInAngle = self.angle - math.degrees(desiredRadianAngel)
        if differenceInAngle >= 180:
            differenceInAngle -= 360

        if differenceInAngle > 0:
            self.angle -= min(self.rotationVel, abs(differenceInAngle))
        else:
            self.angle += min(self.rotationVel, abs(differenceInAngle))

    def updatePathPoint(self):
        target = self.path[self.currentPoint]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.currentPoint += 1

    def move(self):
        if self.currentPoint >= len(self.path):
            return

        self.calculateAngle()
        self.updatePathPoint()
        super().move()

    def mextLevel(self, level):
        self.reset()
        self.vel = self.maxVel + (level - 1) * 0.2
        self.currentPoint = 0

def draw(win, images, playerCar, compyterCar, gameInfo):
    for img, pos in images:
        win.blit(img, pos)

    levelText = MAIN_FONT.render(f"Level {gameInfo.level}", 1, (255,255,255))
    win.blit(levelText, (10, HEIGHT - levelText.get_height() - 70))

    timeText = MAIN_FONT.render(f"Time: {gameInfo.getLevelTime()}s", 1, (255,255, 255))
    win.blit(timeText, (10, HEIGHT - timeText.get_height() - 40))

    velText = MAIN_FONT.render(
        f"Vel: {round(playerCar.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(velText, (10, HEIGHT - velText.get_height() - 10))

    playerCar.draw(win)
    compyterCar.draw(win)
    pygame.display.update()

def movePlayer(playerCar):

    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        playerCar.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        playerCar.rotate(right=True)
    if keys[pygame.K_DOWN]:
        moved = True
        playerCar.moveBackward()
    if keys[pygame.K_UP]:
        moved = True
        playerCar.moveForward()

    if not moved:
        playerCar.reduceSpeed()


def handleCollision(playerCar, computerCar, gameInfo):
    if playerCar.collide(TRACK_BORDER_MASK) != None:
        playerCar.bounce()

    computerFinishPoiCollide = playerCar.collide(FINISH_MASK, *FINISH_POSITION)
    if computerFinishPoiCollide != None:
        blitTextCenter(WINDOW, MAIN_FONT, "You Lost!")
        pygame.display.update()
        pygame.time.wait(5000)
        gameInfo.reset()
        playerCar.reset()
        computerCar.reset()

    playerFinishPoiCollide = playerCar.collide(FINISH_MASK, *FINISH_POSITION)
    if playerFinishPoiCollide != None:
        #checking if y coordinate at finish line = 0, then we are reversing the car at finish line and we should bounce back
        if playerFinishPoiCollide[1] == 0:
            playerCar.bounce()
        else:
            gameInfo.nextLevel()
            playerCar.reset()
            computerCar.nextLevel(gameInfo.level)



images = [(GRASS, (0,0)), (TRACK, (0,0)), (FINISH, FINISH_POSITION)]
playerCar = playerCar(4,4)
computerCar = computerCar(1,4, PATH)
gameInfo = GameInfo()


while True:
    clock.tick(FPS)

    draw(WINDOW, images, playerCar, computerCar, gameInfo)

    while not gameInfo.started:
        blitTextCenter(WINDOW, MAIN_FONT, f"Press any key to start level {gameInfo.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            if event.type == pygame.KEYDOWN:
                gameInfo.startLevel()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            break

    movePlayer(playerCar)
    computerCar.move()
    handleCollision(playerCar, computerCar,gameInfo)

    if gameInfo.gameFinished():
        blitTextCenter(WINDOW, MAIN_FONT, "You Won!")
        pygame.display.update()
        pygame.time.wait(5000)
        gameInfo.reset()
        playerCar.reset()
        computerCar.reset()

