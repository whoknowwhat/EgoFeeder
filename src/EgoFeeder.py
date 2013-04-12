#! -*- coding=utf-8 -*-

'''
Created on 2013. 4. 3.

@author: eM <whoknowwhat0623@gmail.com>
'''

import win32gui

from PIL import Image
from PIL import ImageGrab

import cv2
from cv2 import cv

import numpy
import time
import ctypes
import ConfigParser
import logging

DELAY = 0.5
NPCX, NPCY = 1000, 500
ITEMX, ITEMY = 1550, 120
TABX, TABY = 1640, 95
SWITCH_KEY = "w"
LOGGER = None

CHK_IMAGE = "img/Chk.PNG"
FOOD_IMAGE = "img/Food.PNG"
FEED_IMAGE = "img/Feed.PNG"
END_IMAGE = "img/End.PNG"
BUY_IMAGE = "img/Buy.PNG"


class InputMgr():
    def __init__(self):
        self._ahk = ctypes.cdll.AutoHotkey
        self._ahk.ahktextdll(u"")

    def click(self, x, y):
        self._ahk.ahkExec(u"MouseMove, %d, %d" % (x, y))
        time.sleep(0.1)
        self._ahk.ahkExec(u"MouseClick, left, %d, %d" % (x, y))
        time.sleep(DELAY)

    def move(self, x, y):
        self._ahk.ahkExec(u"MouseMove, %d, %d" % (x, y))
        time.sleep(DELAY)

    def sendKey(self, key):
        self._ahk.ahkExec(u"Send, " + key)
        time.sleep(DELAY)


class WindowMgr():
    """Encapsulates some calls to the winapi for window management"""
    def __init__(self):
        """Constructor"""
        self._handle = None

    def getHandle(self):
        return self._handle

    def find_window(self, window_name):
        self._handle = None
        win32gui.EnumWindows(self._window_enum_callback, window_name)

    def _window_enum_callback(self, hwnd, name):
        '''Pass to win32gui.EnumWindows() to check all the opened windows'''
        if name in win32gui.GetWindowText(hwnd).decode('cp949'):
            self._handle = hwnd

    def set_foreground(self):
        """put the window in the foreground"""
        win32gui.SetActiveWindow(self._handle)
        win32gui.SetForegroundWindow(self._handle)


class ImageSearch():
    def __init__(self):
        self._THRESHOLD = 0.01

    def _getSnapshot(self):
        return ImageGrab.grab()

    def _matchTemplate(self, target, template):
        method = cv.CV_TM_SQDIFF_NORMED
        result = cv2.matchTemplate(template, target, method)

        minVal, _, minLoc, _ = cv2.minMaxLoc(result)

        if minVal < self._THRESHOLD:
            return minLoc
        else:
            return (-1, -1)

    def _PIL2CV(self, img):
        return numpy.array(img.convert('RGB'))

    def search(self, template):
        tim = Image.open(template)
        return self._matchTemplate(self._PIL2CV(self._getSnapshot()), self._PIL2CV(tim))


class EgoFeeder(object):
    def __init__(self):
        self._state_pool = {
            "CheckStatusState": CheckStatusState(self),
            "CheckInventoryState": CheckInventoryState(self),
            "FeedState": FeedState(self),
            "BuyState": BuyState(self)
        }
        self._feed_count = 0
        self._state = self.getState("CheckStatusState")

    def setState(self, state):
        if state is not None:
            self._state = state

    def getState(self, state_name):
        if state_name in self._state_pool:
            return self._state_pool[state_name]

    def counter(self):
        self._feed_count += 1

    def run(self):
        while True:
            self._state.handle()
            if self._state.getCount() > State.MAXLOOPCNT:
                LOGGER.info("Stuck in %s" % (self._state.__name__))
                LOGGER.info("Total feed count" % (self._feed_count))
                self._state._inp.sendKey(SWITCH_KEY)
                return


class State(object):
    MAXLOOPCNT = 10

    def __init__(self, context):
        self._context = context
        self._ims = ImageSearch()
        self._inp = InputMgr()
        self._wm = WindowMgr()
        self._wm.find_window(u"마비노기")
        self._count = 0

    def handle(self):
        pass

    def getCount(self):
        return self._count

    def count(self):
        self._count += 1

    def reset_count(self):
        self._count = 0


class CheckStatusState(State):
    def handle(self):
        self._wm.set_foreground()
        time.sleep(DELAY * 2)
        self._inp.sendKey("/")
        self._inp.sendKey("{SPACE}")
        self._inp.sendKey("{SPACE}")
        self._inp.move(0, 0)
        x, y = self._ims.search(FEED_IMAGE)
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            self._inp.sendKey("{SPACE}")
            self._inp.sendKey("{SPACE}")

        self._inp.move(0, 0)
        x, y = self._ims.search(END_IMAGE)
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            self._inp.sendKey("{SPACE}")
            self._inp.sendKey("{SPACE}")

        x, y = self._ims.search(CHK_IMAGE)
        if (x, y) != (-1, -1):
            self._context.setState(self._context.getState("CheckInventoryState"))
            self.reset_count()
        else:
            self.count()

        self._inp.sendKey("/")
        time.sleep(DELAY * 2)


class CheckInventoryState(State):
    def handle(self):
        self._wm.set_foreground()
        time.sleep(DELAY * 2)
        self._inp.sendKey("/")
        self._inp.sendKey("{SPACE}")
        self._inp.sendKey("{SPACE}")
        self._inp.move(0, 0)
        x, y = self._ims.search(FEED_IMAGE)
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            self._inp.sendKey("{SPACE}")
            self._inp.sendKey("{SPACE}")
        else:
            self._inp.sendKey("/")
            time.sleep(DELAY * 2)
            self.count()
            return

        self._inp.move(0, 0)
        x, y = self._ims.search(FOOD_IMAGE)
        if (x, y) != (-1, -1):
            self._context.setState(self._context.getState("FeedState"))
            self.reset_count()
        else:
            self._context.setState(self._context.getState("BuyState"))
            self.reset_count()

        self._inp.sendKey("/")
        time.sleep(DELAY * 2)


class FeedState(State):
    def handle(self):
        self._wm.set_foreground()
        time.sleep(DELAY * 2)
        self._inp.sendKey("/")
        self._inp.sendKey("{SPACE}")
        self._inp.sendKey("{SPACE}")
        self._inp.move(0, 0)
        x, y = self._ims.search(FEED_IMAGE)
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            self._inp.sendKey("{SPACE}")
            self._inp.sendKey("{SPACE}")
            self._inp.sendKey("{SPACE}")
            self._inp.sendKey("{SPACE}")

        self._inp.move(0, 0)
        x, y = self._ims.search(FOOD_IMAGE)
        if (x, y) != (-1, -1):
            self._inp.click(x + 10, y + 50)
            self._inp.click(x + 100, y + 180)
            self._context.setState(self._context.getState("CheckStatusState"))
            self._context.counter()
            self.reset_count()
        else:
            self.count()

        self._inp.sendKey("/")
        time.sleep(DELAY * 2)


class BuyState(State):
    def handle(self):
        self._wm.set_foreground()
        time.sleep(DELAY * 2)
        self._inp.sendKey("{Ctrl Down}")
        self._inp.click(NPCX, NPCY)
        self._inp.sendKey("{Ctrl Up}")
        self._inp.sendKey("{SPACE}")
        self._inp.sendKey("{SPACE}")
        self._inp.sendKey("{SPACE}")
        self._inp.sendKey("{SPACE}")

        self._inp.move(0, 0)
        x, y = self._ims.search(BUY_IMAGE)
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            self._inp.sendKey("{SPACE}")
            self._inp.sendKey("{SPACE}")
            self._inp.click(TABX, TABY)
            self._inp.sendKey("{Ctrl Down}")
            self._inp.click(ITEMX, ITEMY)
            self._inp.sendKey("{Ctrl Up}")
        else:
            self.count()
            return

        self._inp.move(0, 0)
        x, y = self._ims.search(END_IMAGE)
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            self._context.setState(self._context.getState("FeedState"))
            time.sleep(DELAY * 2)
            self.reset_count()


def main():
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    TABX, TABY = [int(n) for n in config.get("Location", "itemtab").split(',')]
    ITEMX, ITEMY = [int(n) for n in config.get("Location", "item").split(',')]
    NPCX, NPCY = [int(n) for n in config.get("Location", "npc").split(',')]
    DELAY = float(config.get("Etc", "delay"))
    SWITCH_KEY = config.get("Etc", "switch")
    LOGLEVEL = getattr(logging, config.get("Etc", "logging").upper(), None)
    if LOGLEVEL:
        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(LOGLEVEL)
        LOGGER.basicConfig(format='%(asctime)s %(messages)s',
                           filename="log.txt",
                           datefmt="[%Y/%m/%d %H:%M:%S]",
                           filemode='w')

    feeder = EgoFeeder()
    feeder.run()


if __name__ == '__main__':
    main()
