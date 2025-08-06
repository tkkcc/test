import time
from tracemalloc import start
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from com.zsr.android import MyAccessibilityService
from com.zsr.android import MediaProjectionService
from org.beeware.android import MainActivity

def find_root_window_id():
    service = MyAccessibilityService.singletonThis
    # service.getRootNode()
    node = service.getRootInActiveWindow()
    print(node.getPackageName())

def take_screenshot(*args):
    start_time = time.time()
    screenshot = MediaProjectionService.singletonThis.takeScreenshot()
    print("Screenshot taken in", (time.time() - start_time)*1000, "ms")
    start_time = time.time()

    # print(screenshot.getWidth())
    arr = screenshot.getAddr()
    print("Screenshot data addr", arr)

    print("Screenshot bytes", (time.time() - start_time)*1000, "ms")
    start_time = time.time()

    # print(screenshot.width, screenshot.height, len(arr), screenshot.timestamp)
    # print("modify screenshot data last from", arr[-1], "to", 101)
    # arr[-1] = 101
    # print("recheck", bytes(MediaProjectionService.singletonThis.getScreenshotCache().getData())[-1])




def run_on_ui_thread(func):
    from java import dynamic_proxy
    from java.lang import Runnable
    from org.beeware.android import MainActivity

    class R(dynamic_proxy(Runnable)):
        def run(self):
            func()

    MainActivity.singletonThis.runOnUiThread(R())


class HelloWorld(toga.App):
    def startup(self):
        main_box = toga.Box(direction=COLUMN)

        name_label = toga.Label(
            "Your name: ",
            margin=(0, 5),
        )
        self.name_input = toga.TextInput(flex=1)

        name_box = toga.Box(direction=ROW, margin=5)
        name_box.add(name_label)
        name_box.add(self.name_input)

        button = toga.Button(
            "Say Hello!",
            on_press=self.say_hello,
            margin=5,
        )

        button2 = toga.Button(
            "test2",
            on_press=take_screenshot,
            margin=5,
        )

        main_box.add(name_box)
        main_box.add(button)
        main_box.add(button2)


        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    async def say_hello(self, widget):
        find_root_window_id()
        await self.main_window.dialog(
            toga.InfoDialog(
                f"Hello, {self.name_input.value}",
                "Hi there!",
            )
        )

def main():
    def run_app():
        app = HelloWorld(
            "HelloWorld",
            "org.beeware.helloworld",
            startup=HelloWorld.startup,
        )
        app.main_loop()
    # run_app()
    run_on_ui_thread(run_app)

