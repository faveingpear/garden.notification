import sys
import ctypes
import win32gui
import traceback
from win32con import (
    SW_HIDE, SW_SHOW,
    GWL_EXSTYLE, WS_EX_TOOLWINDOW
)
from ast import literal_eval

# get resolution for windows only,
# waiting for https://github.com/kivy/plyer/pull/201
u32 = ctypes.windll.user32
RESOLUTION = (u32.GetSystemMetrics(0), u32.GetSystemMetrics(1))

KWARGS = literal_eval(sys.argv[1])
WIDTH = KWARGS['width']
HEIGHT = KWARGS['height']
OFFSET = (
    KWARGS['offset_x'],
    KWARGS['offset_y']
)

# set window from Notification.open arguments
from kivy.config import Config
Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'borderless', 1)
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'width', WIDTH)
Config.set('graphics', 'height', HEIGHT)
Config.set(
    'graphics', 'left',
    RESOLUTION[0] - WIDTH - OFFSET[0]
)
Config.set(
    'graphics', 'top',
    RESOLUTION[1] - HEIGHT - OFFSET[1]
)

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.utils import platform
from kivy.properties import StringProperty, ListProperty


class Notification(App):
    title = StringProperty(KWARGS['title'])
    message = StringProperty(KWARGS['message'])
    notif_icon = StringProperty(KWARGS['icon'])
    background_color = ListProperty(KWARGS['background_color'])
    line_color = ListProperty(KWARGS['line_color'])
    color = ListProperty(KWARGS['color'])

    def build(self):
        if not self.notif_icon:
            self.notif_icon = self.get_application_icon()
        Clock.schedule_once(self._hide_window, 0)
        if KWARGS['timeout_close']:
            Clock.schedule_once(self.stop, KWARGS['timeout'])

    def _hide_window(self, *args):
        if platform == 'win':
            self._hide_w32_window()
        elif platform == 'linux':
            raise NotImplementedError('linux')
        elif platform == 'osx':
            raise NotImplementedError('osx')
        else:
            return

    def _hide_w32_window(self):
        try:
            w32win = win32gui.FindWindow(None, self.title)
            win32gui.ShowWindow(w32win, SW_HIDE)
            win32gui.SetWindowLong(
                w32win,
                GWL_EXSTYLE,
                win32gui.GetWindowLong(
                    w32win, GWL_EXSTYLE) | WS_EX_TOOLWINDOW
            )
            win32gui.ShowWindow(w32win, SW_SHOW)
            self._return_focus_w32()
        except Exception:
            tb = traceback.format_exc()
            Logger.error('Notification_{}: {}'.format(self.title, tb))

    def _return_focus_w32(self):
        w32win = win32gui.FindWindow(None, KWARGS['parent_title'])
        # win32gui.SetFocus(w32win)
        # permission denied for some reason ???


if __name__ == '__main__':
    Notification().run()