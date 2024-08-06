import sys
sys.path.append("./DLL/")
import time
import keyboard
import pydxshot
import cv2
import random
import string
import threading
from threading import Event
from ctypes import WinDLL
from utils import CONFIG
import numpy as np
import ctypes
import ctypes.wintypes as wintypes

class aim:
    
    WH_MOUSE_LL = 14
    WM_MOUSEMOVE = 0x0200
    
    LowLevelMouseProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
    
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    
    SetWindowsHookEx = user32.SetWindowsHookExW
    SetWindowsHookEx.argtypes = [ctypes.c_int, LowLevelMouseProc, wintypes.HINSTANCE, wintypes.DWORD]
    SetWindowsHookEx.restype = wintypes.HHOOK
    
    UnhookWindowsHookEx = user32.UnhookWindowsHookEx
    UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
    UnhookWindowsHookEx.restype = wintypes.BOOL
    
    CallNextHookEx = user32.CallNextHookEx
    CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
    CallNextHookEx.restype = ctypes.c_int
    
    GetModuleHandle = kernel32.GetModuleHandleW
    GetModuleHandle.argtypes = [wintypes.LPCWSTR]
    GetModuleHandle.restype = wintypes.HINSTANCE
    
    hook = None
    
    def hook_callback(nCode, wParam, lParam):
        if nCode >= 0 and wParam == aim.WM_MOUSEMOVE:
            return 1  # Block mouse movement
        return aim.CallNextHookEx(hook, nCode, wParam, lParam)
    
    HookCallback = LowLevelMouseProc(hook_callback)
    
    def disable_mouse_movement():
        global hook
        h_module = aim.GetModuleHandle(None)
        hook = aim.SetWindowsHookEx(aim.WH_MOUSE_LL, aim.HookCallback, h_module, 0)

(user32, kernel32, shcore) = (
    WinDLL('user32', use_last_error=True),
    WinDLL('kernel32', use_last_error=True),
    WinDLL('shcore', use_last_error=True)
)

shcore.SetProcessDpiAwareness(2)

(WIDTH, HEIGHT) = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

KEY_MAPPING = {
    'a': 'd',
    'd': 'a',
    'w': 's',
    's': 'w'
}

class triggerbot:
    def __init__(self):
        self.config = self.start_config()
        self.previous_fps = self.config.target_fps
        self.previous_zone = self.config.GRAB_ZONE
        self.cam = pydxshot.create(output_color='BGR')
        self.adjusting = 1
        self.img = None
        self.yes = False
        self.trigger_times = 0
        self.filter_delay = 0.0
        self.real_one = 0.0
        self.stop_event = Event()
        
    def start_config(self):
        return CONFIG()

    def start_threads(self):
        self.stop_event.clear()
        self.thread1 = threading.Thread(target=self.lastandfilter, daemon=True)
        self.thread2 = threading.Thread(target=self.running, daemon=True)
        self.thread1.start()
        self.thread2.start()

    def stop_threads(self):
        self.stop_event.set()
        self.thread1.join()
        self.thread2.join()
        
    def restart_threads(self):
        self.stop_threads()
        self.start_threads()

    @staticmethod
    def randomgen(size=12, chars=string.ascii_uppercase + string.digits):
        return ''.join((random.choice(chars) for _ in range(size)))

    def lastframe(self):
        image = self.cam.get_latest_frame()
        if image is not None:
            self.img = image
            self.start = time.perf_counter()
            
    def filterimage(self):
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.config.low_color, self.config.high_color)
        kernel = np.ones((3, 3), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=self.config.detection_threshold)
        self.yes = cv2.countNonZero(dilated_mask) != 0

    def is_pressed_excluding_tab(self, key):
        return keyboard.is_pressed(key) and not keyboard.is_pressed('tab')

    def lastandfilter(self):
        while not self.stop_event.is_set():
            if self.config.not1shot:
                while (self.is_pressed_excluding_tab(self.config.hotkey_trigger) or self.is_pressed_excluding_tab(self.config.vandal_ht)):
                    if not self.cam.is_capturing:
                        self.cam.start(target_fps=self.config.target_fps, video_mode=True, region=self.config.GRAB_ZONE)
                    if self.cam.is_capturing:
                        self.lastframe()
                        self.filterimage()
            else:
                while self.is_pressed_excluding_tab(self.config.hotkey_trigger):
                    if not self.cam.is_capturing:
                        self.cam.start(target_fps=self.config.target_fps, video_mode=True, region=self.config.GRAB_ZONE)
                    if self.cam.is_capturing:
                        self.lastframe()
                        self.filterimage()
            if self.cam.is_capturing:
                self.cam.stop()
            time.sleep(0.1)

    def apply_cooldown(self):
        self.real_one = time.perf_counter() - self.start
        if self.real_one < self.config.initial_num:
            additional_delay = self.randomizedelay() - self.real_one
            time.sleep(additional_delay)
            
    def searcherino(self):
        if self.yes:
            if self.config.aim:
                aim.disable_mouse_movement()
            held = []
            if self.config.counterstrafe:
                if self.is_pressed_excluding_tab('a') and not self.is_pressed_excluding_tab('d'):
                    keyboard.press('d')
                    held.append('d')
                    time.sleep(0.1)
                elif self.is_pressed_excluding_tab('s') and not self.is_pressed_excluding_tab('w'):
                    keyboard.press('w')
                    held.append('w')
                    time.sleep(0.1)
                elif self.is_pressed_excluding_tab('d') and not self.is_pressed_excluding_tab('a'):
                    keyboard.press('a')
                    held.append('a')
                    time.sleep(0.1)
                elif self.is_pressed_excluding_tab('w') and not self.is_pressed_excluding_tab('s'):
                    keyboard.press('s')
                    held.append('s')
                    time.sleep(0.1)
            self.apply_cooldown()
            keyboard.press(self.config.shoot_key)
            time.sleep(self.randomizedelaytoshoot())
            aim.UnhookWindowsHookEx(hook)
            keyboard.release(self.config.shoot_key)
            for cap in held:
                time.sleep(0.2)
                keyboard.release(cap)
            self.trigger_times += 1
            time.sleep(self.config.cooldowntime / 10)

    def hold(self):
        self.start_threads()
        
    def running(self):
        while not self.stop_event.is_set():
            if self.config.not1shot:
                while (self.is_pressed_excluding_tab(self.config.hotkey_trigger) or self.is_pressed_excluding_tab(self.config.vandal_ht)):
                    self.searcherino()
                    time.sleep(0.001)
            else:
                while self.is_pressed_excluding_tab(self.config.hotkey_trigger):
                    self.searcherino()
                    time.sleep(0.001)
            time.sleep(0.1)

    def randomizedelay(self):
        return random.uniform(self.config.initial_num, self.config.last_num)
    
    def randomizedelaytoshoot(self):
        if self.config.not1shot and self.is_pressed_excluding_tab(self.config.vandal_ht):
            return random.uniform(0.12, 0.17)
        else:
            return random.uniform(0.06, 0.08)