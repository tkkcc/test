from dataclasses import dataclass
from pathlib import Path
from com.zsr.android import MyAccessibilityService
from com.zsr.android import MediaProjectionService
from org.beeware.android import MainActivity
from java import dynamic_proxy
from java.lang import Runnable
from . import zsr as ext
# from .zsr import sum_as_string, find_color_points_in_screenshot, find_all_color_points_in_screenshot
import time

ACCESSIBILITY_SERVICE = MyAccessibilityService.singletonThis
MEDIA_PROJECTION_SERVICE = MediaProjectionService.singletonThis
MAIN_ACTIVITY = MainActivity.singletonThis
""
class Region:
    def __init__(self, left: int, top: int, width: int, height: int):
        self.left = left
        self.top = top
        self.width = width
        self.height = height

class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Point({self.x}, {self.y})"
    def tap(self):
        print(f"tap at ({self.x}, {self.y})")
        # ACCESSIBILITY_SERVICE.tap(self.x, self.y)
        
class ColorPoints:
    def __init__(self, color_points: str, first_point_region: tuple[int, int, int, int]|None = None, tolerance: float = 0.05, tolerance_mode: int=0):
        # color_points format: "967|537|617D31,931|537|617D31,1021|537|617D31,958|552|FFFFFF"
        self.color_points = [(int(x), int(y), int(color[:2], 16), int(color[2:4], 16), int(color[4:], 16)) for x, y, color in (item.split("|") for item in color_points.split(","))]
        self.first_point_region = first_point_region
        self.tolerance = tolerance
        self.tolerance_mode = tolerance_mode

    def find(self) -> Point|None:
        if self.first_point_region is None:
            screenshot = MEDIA_PROJECTION_SERVICE.takeScreenshot()
            addr, width, height = screenshot.getAddr(), screenshot.getWidth(), screenshot.getHeight()
            result = ext.find_color_points_in_screenshot(addr, width, height, self.color_points, self.tolerance, self.tolerance_mode)
            return Point(result[0], result[1]) if result else None
        else:
            result = self.find_all(max_num=1)
            return result[0] if result else None

    def find_all(self, max_num: int|None = None) -> list[Point]:
        screenshot = MEDIA_PROJECTION_SERVICE.takeScreenshot()
        addr, width, height = screenshot.getAddr(), screenshot.getWidth(), screenshot.getHeight()
        result = ext.find_all_color_points_in_screenshot(addr, width, height, self.color_points, self.first_point_region, self.tolerance, max_num)

        # result is a flat list of ints: [x1, y1, x2, y2, ...]
        return [Point(result[i], result[i+1]) for i in range(0, len(result), 2)]

class Image:
    def __init__(self, path: str|Path, first_point_region: tuple[int, int, int, int], tolerance: float = 0.05, tolerance_mode: int = 0):
        self.path = str(path)
        self.first_point_region = first_point_region
        self.tolerance = tolerance
        self.tolerance_mode = tolerance_mode

    def find(self) -> Point|None:
        result = self.find_all(max_num=1)
        return result[0] if result else None

    def find_all(self, max_num: int|None=None) -> list[Point]:
        screenshot = MEDIA_PROJECTION_SERVICE.takeScreenshot()
        addr, width, height = screenshot.getAddr(), screenshot.getWidth(), screenshot.getHeight()
        result = ext.find_all_image_in_screenshot(addr, width, height, str(self.path), self.first_point_region, self.tolerance, self.tolerance_mode, max_num)
        # result is a flat list of ints: [x1, y1, x2, y2, ...]
        return [Point(result[i], result[i+1]) for i in range(0, len(result), 2)]

def find_root_window_id():
    # MyAccessibilityService.getRootNode()
    node = ACCESSIBILITY_SERVICE.getRootInActiveWindow()
    print(node.getPackageName())

def take_screenshot(*args):
    start_time = time.time()
    screenshot = MEDIA_PROJECTION_SERVICE.takeScreenshot()
    print("Screenshot taken in", (time.time() - start_time)*1000, "ms")
    start_time = time.time()

    # print(screenshot.getWidth())
    arr = screenshot.getAddr()
    print("Screenshot data addr", arr)
    width = screenshot.getWidth()
    height = screenshot.getHeight()
    print("Screenshot size", width, height)
    # print("rust result", ext.sum_as_string(arr, width))
    print("Screenshot duration", (time.time() - start_time)*1000, "ms")
    start_time = time.time()



def run_on_ui_thread(func):
    class R(dynamic_proxy(Runnable)):
        def run(self):
            func()

    MAIN_ACTIVITY.runOnUiThread(R())