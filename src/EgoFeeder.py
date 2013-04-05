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

DELAY = 0.5
NPCX, NPCY = 1000, 500
ITEMX, ITEMY = 1550, 120
TABX, TABY = 1640, 95

    
class InputMgr():
    def __init__(self):
        self._ahk = ctypes.cdll.AutoHotkey
        self._ahk.ahktextdll(u"")
    
    def click(self, x, y):
        self._ahk.ahkExec(u"MouseMove, %d, %d" % (x, y))
        time.sleep(0.1)
        self._ahk.ahkExec(u"MouseClick, left, %d, %d" % (x, y))
    
    def move(self, x, y):
        self._ahk.ahkExec(u"MouseMove, %d, %d" % (x, y))
        
    def sendKey(self, key):
        self._ahk.ahkExec(u"Send, " + key)

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
        self._state = self.getState("CheckStatusState")
        
    def setState(self, state):
        if state is not None:
            self._state = state
        
    def getState(self, state_name):
        if state_name in self._state_pool:
            return self._state_pool[state_name]
    
    def run(self):
        while True:
            self._state.handle()


class State(object):
    def __init__(self, context):
        self._context = context
        self._ims = ImageSearch()
        self._inp = InputMgr()
        self._wm = WindowMgr()
        self._wm.find_window(u"마비노기")

class CheckStatusState(State):
    def handle(self):
        self._wm.set_foreground()
        time.sleep(DELAY * 2)
        self._inp.sendKey("/")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.move(0, 0)
        time.sleep(DELAY)
        x, y = self._ims.search("Feed.PNG")
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
        
        self._inp.move(0, 0)
        time.sleep(DELAY)
        x, y = self._ims.search("End.PNG")
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            
        x, y = self._ims.search("Chk.PNG")
        if (x, y) != (-1, -1):
            self._context.setState(self._context.getState("CheckInventoryState"))
            
        self._inp.sendKey("/")
        time.sleep(DELAY * 2)


class CheckInventoryState(State):
    def handle(self):
        self._wm.set_foreground()
        time.sleep(DELAY * 2)
        self._inp.sendKey("/")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.move(0, 0)
        time.sleep(DELAY)
        x, y = self._ims.search("Feed.PNG")
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
        else:
            self._inp.sendKey("/")
            time.sleep(DELAY * 2)
            return

        self._inp.move(0, 0)
        time.sleep(DELAY)
        x, y = self._ims.search("Food.PNG")
        if (x, y) != (-1, -1):
            self._context.setState(self._context.getState("FeedState"))
        else:
            self._context.setState(self._context.getState("BuyState"))
        
        self._inp.sendKey("/")
        time.sleep(DELAY * 2)


class FeedState(State):
    def handle(self):
        self._wm.set_foreground()
        time.sleep(DELAY * 2)
        self._inp.sendKey("/")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.move(0, 0)
        time.sleep(DELAY)
        x, y = self._ims.search("Feed.PNG")
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)

        self._inp.move(0, 0)
        time.sleep(DELAY)
        x, y = self._ims.search("Food.PNG")
        if (x, y) != (-1, -1):
            self._inp.click(x + 10, y + 50)
            self._inp.click(x + 10, y + 50)
            self._inp.click(x + 10, y + 50)
            time.sleep(DELAY * 4)
            self._inp.click(x + 100, y + 180)
            time.sleep(DELAY * 4)
            self._context.setState(self._context.getState("CheckStatusState"))
            
        self._inp.sendKey("/")
        time.sleep(DELAY * 2)


class BuyState(State):
    def handle(self):
        self._wm.set_foreground()
        time.sleep(DELAY * 2)
        self._inp.sendKey("{Ctrl Down}")
        time.sleep(DELAY)
        self._inp.click(NPCX, NPCY)
        time.sleep(DELAY)
        self._inp.sendKey("{Ctrl Up}")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        self._inp.sendKey("{SPACE}")
        time.sleep(DELAY)
        
        self._inp.move(0, 0)
        time.sleep(DELAY)
        x, y = self._ims.search("Buy.PNG")
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            self._inp.sendKey("{SPACE}")
            time.sleep(DELAY)
            self._inp.click(TABX, TABY)
            time.sleep(DELAY)
            self._inp.sendKey("{Ctrl Down}")
            time.sleep(DELAY)
            self._inp.click(ITEMX, ITEMY)
            time.sleep(DELAY)
            self._inp.sendKey("{Ctrl Up}")
        else:
            self._inp.sendKey("/")
            time.sleep(DELAY * 2)
            return
        
        self._inp.move(0, 0)
        time.sleep(DELAY)
        x, y = self._ims.search("End.PNG")
        if (x, y) != (-1, -1):
            self._inp.click(x, y)
            time.sleep(DELAY)
            self._context.setState(self._context.getState("FeedState"))
            time.sleep(DELAY * 2)


def main():
    feeder = EgoFeeder()
    feeder.run()


if __name__ == '__main__':
    main()
