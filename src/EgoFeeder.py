'''
Created on 2013. 4. 3.

@author: eM <whoknowwhat0623@gmail.com>
'''

#! -*- coding=utf-8 -*-

import win32api
import win32con
import win32gui


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)


def getWindow(name):
    def callback(hwnd, results):
        text = win32gui.GetWindowText(hwnd)
        if text.find(name) >= 0:
            results.append(hwnd)
    windows = []
    win32gui.EnumWindows(callback, windows)
    if windows:
        return windows[0]
    else:
        return None


def setActive(name):
    hwnd = getWindow(name)
    if hwnd:
        win32gui.SetActiveWindow(hwnd)
        win32gui.SetForegroundWindow(hwnd)


def main():
    setActive("마비노기")
    click(0, 0)


if __name__ == '__main__':
    main()
