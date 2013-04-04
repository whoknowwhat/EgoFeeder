#! -*- coding=utf-8 -*-

'''
Created on 2013. 4. 3.

@author: eM <whoknowwhat0623@gmail.com>
'''

import win32api
import win32con
import win32gui

from PIL import Image
from PIL import ImageGrab

import cv2
from cv2 import cv

import numpy
import time
import ctypes


def sendKey(k):
    win32api.keybd_event(k, 0,)
    win32api.keybd_event(k, 0, win32con.KEYEVENTF_KEYUP,)


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


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


def getSnapshot():
    return ImageGrab.grab()


def getMatchLocation(target, template):
    method = cv.CV_TM_SQDIFF_NORMED
    result = cv2.matchTemplate(template, target, method)

    # We want the minimum squared difference
    _, _, mnLoc, _ = cv2.minMaxLoc(result)

    # Draw the rectangle:
    # Extract the coordinates of our best match
    return mnLoc


def PIL2CV(img):
    return numpy.array(img.convert('RGB'))


def main():
    w = WindowMgr()
    w.find_window(u"마비노기")
    w.set_foreground()

    time.sleep(1)
    ahk = ctypes.cdll.AutoHotkey
    ahk.ahktextdll(u"")
    ahk.ahkExec(u"Send, {Enter}")
    time.sleep(1)

    targetImage = getSnapshot()
    templateImage = Image.open("Chk.PNG")
    x, y = getMatchLocation(PIL2CV(targetImage), PIL2CV(templateImage))
    print x, y
    click(x, y)


if __name__ == '__main__':
    main()
