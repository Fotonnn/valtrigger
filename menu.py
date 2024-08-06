import dearpygui.dearpygui as dpg
import keyboard
import threading
import string
import random
from screen import triggerbot
import sys
import hashlib
import ctypes
from ctypes import c_int
import time
dwm = ctypes.windll.dwmapi
import win32gui
import win32con

class MARGINS(ctypes.Structure):
    _fields_ = [("cxLeftWidth", c_int),
                ("cxRightWidth", c_int),
                ("cyTopHeight", c_int),
                ("cyBottomHeight", c_int)
               ]

UNICODE_MAPPING = {
    dpg.mvKey_Tab: 'tab',
    dpg.mvKey_Capital: "capslock",
    dpg.mvKey_Shift: 'shift',
    dpg.mvKey_Control: 'control',
    dpg.mvKey_Alt: 'alt',
    dpg.mvKey_F1: 'f1',
    dpg.mvKey_F2: 'f2',
    dpg.mvKey_F3: 'f3',
    dpg.mvKey_F4: 'f4',
    dpg.mvKey_F5: 'f5',
    dpg.mvKey_F6: 'f6',
    dpg.mvKey_F7: 'f7',
    dpg.mvKey_F8: 'f8',
    dpg.mvKey_F9: 'f9',
    dpg.mvKey_F10: 'f10',
    dpg.mvKey_F11: 'f11',
    dpg.mvKey_F12: 'f12',
    dpg.mvKey_Insert: "insert"
}

viewport = None
title_bar_drag = False
shoot_key = False
trigger_key = False
vandal_key = False
min_delay = 0
max_delay = 0
slider1 = None
slider2 = None
trigger = triggerbot()
config = trigger.config
previous_zone = config.ZONE
quad = None
key_press_handler_id = None
logged = False

def exit():
    sys.exit()

def change_hotkey(sender, app_data):
    global shoot_key, trigger_key, vandal_key
    unregister_key_press_handler()
    key = UNICODE_MAPPING.get(app_data, chr(app_data))
    if key in {config.shoot_key, config.hotkey_trigger, config.vandal_ht}:
        dpg.configure_item(item=alreadykey, show=True)
        return
    if shoot_key:
        config.shoot_key = key
        dpg.set_value("shoot_hotkey", f"Shoot Key: {key}")
        shoot_key = False
    elif trigger_key:
        config.hotkey_trigger = key
        dpg.set_value("trigger_hotkey", f"Trigger Key: {key}")
        trigger_key = False
    elif vandal_key:
        config.vandal_ht = key
        dpg.set_value("vandal_ht", f"Vandal Key: {key}")
    
def handle_key_press(sender, app_data):
    change_hotkey(sender, app_data)

def register_key_press_handler():
    global key_press_handler_id
    with dpg.handler_registry():
        key_press_handler_id = dpg.add_key_press_handler(callback=handle_key_press)

def unregister_key_press_handler():
    if key_press_handler_id:
        dpg.delete_item(key_press_handler_id)

def trigger_key_callback():
    global trigger_key
    trigger_key = True
    register_key_press_handler()
    
def shoot_key_callback():
    global shoot_key
    shoot_key = True
    register_key_press_handler()

def vandal_key_callback():
    global vandal_key
    vandal_key = True
    register_key_press_handler()

def randomgen(size=12, chars=string.ascii_uppercase + string.digits):
    return ''.join((random.choice(chars) for _ in range(size)))

def update_zone_from_slider(sender, attribute):
    value = dpg.get_value(sender)
    setattr(config, attribute, value)
    config.GRAB_ZONE = (
        int(config.width / 2 - value),
        int(config.height / 2 - value),
        int(config.width / 2 + value),
        int(config.height / 2 + value)
    )
    if config.fov:
        show_fov(None, False)
        show_fov(None, True)

def update_config(sender, attribute):
    value = dpg.get_value(sender)
    setattr(config, attribute, value)
    
def login_callback(sender):
    global logged
    license_key = dpg.get_value("##license_input")
    logged = True
    if logged:
        dpg.set_value("##status_text", "Login successful")
        show_main_menu()
        trigger.hold()
    else:
        dpg.set_value("##status_text", "Login failed")

def show_fov(sender, data):
    global quad
    try:
        true = dpg.get_value(data)
    except:
        true = data
    zone = dpg.get_value(slider3)
    grab_zone = (
        int(config.width / 2 - zone), int(config.height / 2 - zone),
        int(config.width / 2 + zone), int(config.height / 2 + zone)
    )
    p1 = (grab_zone[0], grab_zone[1])
    p2 = (grab_zone[2], grab_zone[1])
    p3 = (grab_zone[2], grab_zone[3])
    p4 = (grab_zone[0], grab_zone[3])
    if data:
        quad = dpg.draw_quad(p1, p2, p3, p4, color=(255, 255, 255, 255), parent="FOV")
        config.fov = True
    elif ~data and dpg.does_item_exist(quad):
        dpg.delete_item(quad)
        config.fov = False

def show_main_menu():
    dpg.configure_item(win, show=True)
    dpg.configure_item(login_window, show=False)

def change_title():
    while True:
        time.sleep(1)
        dpg.configure_viewport(viewport, title=randomgen())

def restart_tg():
    trigger.restart_threads()

def set_config_legit():
    config.counterstrafe = True
    config.cooldowntime = 1.5
    config.target_fps = 120
    config.ZONE = 4
    config.initial_num = 0.017
    config.last_num = 0.019
    config.detection_threshold = 10
    config.slowaim = False
    config.shoot_key = 'l'
    show_fov(None, False)
    dpg.set_value("##counterstrafe_checkbox", config.counterstrafe)
    dpg.set_value("##cooldowntime_slider", config.cooldowntime)
    dpg.set_value("##target_fps_slider", config.target_fps)
    dpg.set_value("##zone_slider", config.ZONE)
    dpg.set_value("##initial_num_slider", config.initial_num)
    dpg.set_value("##last_num_slider", config.last_num)
    dpg.set_value("##detection_threshold_slider", config.detection_threshold)
    dpg.set_value("##slowaim_checkbox", config.slowaim)
    dpg.set_value("##fov_checkbox", config.fov)
    dpg.set_value("delay", f"Between {config.initial_num:.4f} and {config.last_num:.4f}")
    dpg.set_value("shoot_hotkey", f"Shoot Hotkey: {config.shoot_key}")

def run():
    global viewport, window_hidden, width, height, slider1, slider2, win, login_window, slider3, hwnd, ZONE, click_through, alreadykey
    width = 400
    height = 500
    context = dpg.create_context()
    viewport = dpg.create_viewport(title='steam', always_on_top=True, decorated=False, clear_color=[0.0, 0.0, 0.0, 0.0], resizable=False, disable_close=True)
    threading.Thread(target=change_title, daemon=True).start()
    dpg.set_viewport_always_top(True)
    dpg.create_context()
    dpg.setup_dearpygui()
    dpg.add_viewport_drawlist(front=False, tag="FOV")
    window_hidden = False
    with dpg.window(label="Foton's Private", width=width, height=height, no_collapse=True, no_resize=True, on_close=exit) as login_window:
        dpg.add_text("Enter your license:")
        dpg.add_input_text(tag="##license_input", width=200)
        with dpg.group(horizontal=True):    
            dpg.add_button(label="Login", callback=login_callback)
            dpg.add_button(label="Exit", callback=lambda: exit)  
        dpg.add_text(tag="##status_text", label="", color=(255, 255, 255))
        
    with dpg.window(label="Foton's Private", width=width, height=height, no_collapse=True, no_resize=True, on_close=exit, show=False) as win:
        dpg.add_slider_int(label="Target FPS", default_value=config.target_fps, min_value=60, max_value=240, tag="##target_fps_slider", callback=lambda sender: update_config(sender, 'target_fps'))
        dpg.add_slider_int(label="Threshold", default_value=config.detection_threshold, min_value=1, max_value=10, tag="##detection_threshold_slider", callback=lambda sender: update_config(sender, 'detection_threshold'))
        slider3 = dpg.add_slider_int(label="Zone", default_value=config.ZONE, min_value=1, max_value=10, tag="##zone_slider", callback=lambda sender: update_zone_from_slider(sender, 'ZONE'))
        dpg.add_slider_float(label="Delay after shoot", default_value=config.cooldowntime, min_value=1.0001, max_value=5.0001, tag="##cooldowntime_slider", callback=lambda sender: update_config(sender, 'cooldowntime'), format="%.4f")
        
        with dpg.group(horizontal=True):    
            dpg.add_text("Delay range")  
            slider1 = dpg.add_slider_float(min_value=0.001, max_value=0.033, default_value=config.initial_num, tag="##initial_num_slider", callback=lambda sender: update_config(sender, 'initial_num'), width=100)
            slider2 = dpg.add_slider_float(min_value=0.002, max_value=0.036, default_value=config.last_num, tag="##last_num_slider", callback=lambda sender: update_config(sender, 'last_num'), width=100)

        dpg.add_checkbox(label="Counterstrafe", default_value=config.counterstrafe, tag="##counterstrafe_checkbox", callback=lambda sender: update_config(sender, 'counterstrafe'))
        dpg.add_checkbox(label="Aim Assist(Stops aim when see enemy)", default_value=config.aim, tag="##aim_checkbox", callback=lambda sender: update_config(sender, 'aim'))
        dpg.add_checkbox(label="FOV (use only out of match)", default_value=config.fov, tag="##fov_checkbox", callback=show_fov)
        with dpg.group(horizontal=True):
            dpg.add_text(label="awp hotkey: ", tag="trigger_hotkey")
            dpg.set_value("trigger_hotkey", f"Trigger Hotkey: {config.hotkey_trigger}")
            dpg.add_button(label="Change", callback=trigger_key_callback)
        with dpg.group(horizontal=True):
            dpg.add_text(label="Shoot Hotkey: ", tag="shoot_hotkey")
            dpg.set_value("shoot_hotkey", f"Shoot Hotkey: {config.shoot_key}")
            dpg.add_button(label="Change", callback=shoot_key_callback)
        dpg.add_checkbox(label="not 1 shot", default_value=config.not1shot, tag="##not1shot", callback=lambda sender: update_config(sender, 'not1shot'))
        with dpg.group(horizontal=True):
            dpg.add_text(label="Vandal Hotkey: ", tag="vandal_ht")
            dpg.set_value("vandal_ht", f"Vandal Hotkey: {config.vandal_ht}")
            dpg.add_button(label="Change", callback=vandal_key_callback)
        dpg.add_text("Delay (Legit = 0.017, Pro = 0.16, Rage = 0.14 to below): ")
        dpg.add_text(label="Between: ", tag="delay")
        dpg.set_value("delay", f"Between {config.initial_num:.4f} and {config.last_num:.4f}")
        dpg.add_button(label="LEGIT", callback=set_config_legit)
        dpg.add_button(label="RESTART in case of bugs", callback=restart_tg)
        alreadykey = dpg.add_text("Key already setted. please choose another.", show=False)

    dpg.show_viewport()
    dpg.toggle_viewport_fullscreen()
    hwnd = win32gui.FindWindow(None, 'steam')
    margins = MARGINS(-1, -1, -1, -1)
    ex_style = win32gui.GetWindowLong(hwnd, win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE))
    dwm.DwmExtendFrameIntoClientArea(hwnd, margins)
    click_through = False

    while dpg.is_dearpygui_running():
        dpg.render_dearpygui_frame()
        if keyboard.is_pressed('insert'):
            click_through = not click_through
            dpg.configure_item(item=alreadykey, show=False)
            time.sleep(0.1)

        if click_through and logged:
            config.saveconfig()
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
            dpg.configure_item(win, show=False)
            config.getconfig()
        elif not click_through and logged:
            dpg.configure_item(win, show=True)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                ex_style & ~win32con.WS_EX_LAYERED & ~win32con.WS_EX_TRANSPARENT)

def start():
    run()
    dpg.destroy_context()

if __name__ == "__main__":
    start()
