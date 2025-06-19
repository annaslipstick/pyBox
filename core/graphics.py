import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog


root = tk.Tk()
fb = FrameBuffer(320, 240)
wm = WindowManager(fb)

# Create a window or two here, maybe add buttons...

canvas = tk.Canvas(root, width=fb.width, height=fb.height)
canvas.pack()
# Basic 5x5 pixel font for letters used in buttons
PIXEL_FONT = {
    "A": ["  #  "," # # ","#####","#   #","#   #"],
    "B": ["#### ","#   #","#### ","#   #","#### "],
    "C": [" ####","#    ","#    ","#    "," ####"],
    "D": ["#### ","#   #","#   #","#   #","#### "],
    "E": ["#####","#    ","#### ","#    ","#####"],
    "F": ["#####","#    ","#### ","#    ","#    "],
    "G": [" ####","#    ","#  ##","#   #"," ####"],
    "H": ["#   #","#   #","#####","#   #","#   #"],
    "I": ["#####","  #  ","  #  ","  #  ","#####"],
    "J": ["#####","   # ","   # ","#  # "," ##  "],
    "K": ["#   #","#  # ","###  ","#  # ","#   #"],
    "L": ["#    ","#    ","#    ","#    ","#####"],
    "M": ["#   #","## ##","# # #","#   #","#   #"],
    "N": ["#   #","##  #","# # #","#  ##","#   #"],
    "O": [" ### ","#   #","#   #","#   #"," ### "],
    "P": ["#### ","#   #","#### ","#    ","#    "],
    "Q": [" ### ","#   #","#   #","#  ##"," ####"],
    "R": ["#### ","#   #","#### ","#  # ","#   #"],
    "S": [" ####","#    "," ### ","    #","#### "],
    "T": ["#####","  #  ","  #  ","  #  ","  #  "],
    "U": ["#   #","#   #","#   #","#   #"," ### "],
    "V": ["#   #","#   #","#   #"," # # ","  #  "],
    "W": ["#   #","#   #","# # #","## ##","#   #"],
    "X": ["#   #"," # # ","  #  "," # # ","#   #"],
    "Y": ["#   #"," # # ","  #  ","  #  ","  #  "],
    "Z": ["#####","   # ","  #  "," #   ","#####"],
    " ": ["     ","     ","     ","     ","     "],
}

def draw_char(buffer, x, y, char, color):
    glyph = PIXEL_FONT.get(char.upper())
    if not glyph:
        return
    for row, line in enumerate(glyph):
        for col, pixel in enumerate(line):
            if pixel == "#":
                buffer.set_pixel(x + col, y + row, color)

def draw_text(buffer, x, y, text, color):
    for i, char in enumerate(text):
        draw_char(buffer, x + i * 6, y, char, color)

class FrameBuffer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buffer = [[(0, 0, 0) for _ in range(height)] for _ in range(width)]

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.buffer[x][y] = color

    def clear(self, color=(0, 0, 0)):
        for x in range(self.width):
            for y in range(self.height):
                self.buffer[x][y] = color

    def to_image(self):
        img = Image.new("RGB", (self.width, self.height))
        pixels = img.load()
        for x in range(self.width):
            for y in range(self.height):
                pixels[x, y] = self.buffer[x][y]
        return img

class Button:
    def __init__(self, x, y, w, h, text, callback=None):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.callback = callback
        self.hover = False

    def draw(self, win):
        border = (100, 100, 100)
        bg = (80, 80, 180) if self.hover else (50, 50, 100)
        text_color = (255, 255, 255)

        for i in range(self.w):
            for j in range(self.h):
                color = border if i == 0 or i == self.w - 1 or j == 0 or j == self.h - 1 else bg
                win.set_pixel(self.x + i, self.y + j, color)

        text_x = self.x + 3
        text_y = self.y + (self.h // 2) - 3
        draw_text(win, text_x, text_y, self.text, text_color)

    def handle_click(self, x, y):
        if self.x <= x < self.x + self.w and self.y <= y < self.y + self.h:
            if self.callback:
                self.callback()
            return True
        return False

    def handle_hover(self, x, y):
        self.hover = self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

class VirtualWindow:
    CLOSE_BTN_POS = (-8, 3)
    CLOSE_BTN_SIZE = (6, 6)

    def __init__(self, id, x, y, width, height, title="Window", visible=True):
        self.id = id
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.title = title
        self.visible = visible
        self.buffer = [[(0, 0, 0) for _ in range(height)] for _ in range(width)]
        self.dragging = False
        self.drag_offset = (0, 0)
        self.widgets = []
        self.should_close = False

    def set_pixel(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.buffer[x][y] = color

    def clear(self, color=(0, 0, 0)):
        for x in range(self.w):
            for y in range(self.h):
                self.buffer[x][y] = color

    def close_button_hit(self, rel_x, rel_y):
        cx, cy = self.w + self.CLOSE_BTN_POS[0], self.CLOSE_BTN_POS[1]
        cw, ch = self.CLOSE_BTN_SIZE
        return cx <= rel_x < cx + cw and cy <= rel_y < cy + ch

    def draw_widgets(self):
        for widget in self.widgets:
            widget.draw(self)

    def blit_to_fb(self, fb, focused=False):
        if not self.visible:
            return

        border_color = (200, 200, 200)
        title_height = 12
        title_bg = (50, 50, 100) if focused else (30, 30, 30)
        close_btn_color = (200, 60, 60)

        for x in range(self.w):
            for y in range(self.h):
                tx = self.x + x
                ty = self.y + y

                if x == 0 or y == 0 or x == self.w - 1 or y == self.h - 1:
                    fb.set_pixel(tx, ty, border_color)
                elif y < title_height:
                    fb.set_pixel(tx, ty, title_bg)
                else:
                    fb.set_pixel(tx, ty, self.buffer[x][y])

        # Close button
            for dx in range(6):
                for dy in range(6):
                    cx = self.x + self.w - 8 + dx
                    cy = self.y + 3 + dy
                    fb.set_pixel(cx, cy, close_btn_color)
                    x_coords = [(0,0), (1,1), (2,2), (3,3), (4,4), (5,5)]
                for dx, dy in x_coords:
                    fb.set_pixel(self.x + self.w - 8 + dx, self.y + 3 + dy, (255, 255, 255))
                    fb.set_pixel(self.x + self.w - 8 + dx, self.y + 3 + 5 - dy, (255, 255, 255))

        self.draw_widgets()

class WindowManager:
    def __init__(self, framebuffer):
        self.fb = framebuffer
        self.windows = {}
        self.next_id = 1
        self.focused_id = None

    def create_window(self, x, y, w, h, title="Window"):
        win_id = self.next_id
        self.next_id += 1
        self.windows[win_id] = VirtualWindow(win_id, x, y, w, h, title)
        self.focused_id = win_id
        return win_id

    def get_window(self, win_id):
        return self.windows.get(win_id)

    def draw_all(self):
        self.cleanup_closed_windows()
        self.fb.clear()
        for win_id in self.windows:
            focused = (win_id == self.focused_id)
            self.windows[win_id].blit_to_fb(self.fb, focused=focused)

    def handle_click(self, x, y):
        for win_id in reversed(list(self.windows)):
            win = self.windows[win_id]
            if not win.visible:
                continue
            if win.x <= x < win.x + win.w and win.y <= y < win.y + win.h:
                rel_x = x - win.x
                rel_y = y - win.y

                if win.close_button_hit(rel_x, rel_y):
                    win.should_close = True
                    return None

                for widget in win.widgets:
                    if widget.handle_click(rel_x, rel_y):
                        self.bring_to_front(win_id)
                        return win_id

                self.focused_id = win_id
                self.bring_to_front(win_id)
                win.dragging = True
                win.drag_offset = (x - win.x, y - win.y)
                return win_id
        return None

    def handle_mouse_release(self):
        for win in self.windows.values():
            win.dragging = False

    def handle_mouse_move(self, x, y):
        for win in self.windows.values():
            if win.dragging:
                dx, dy = win.drag_offset
                win.x = x - dx
                win.y = y - dy

            if self.focused_id == win.id and win.visible:
                rel_x = x - win.x
                rel_y = y - win.y
                for widget in win.widgets:
                    widget.handle_hover(rel_x, rel_y)

    def bring_to_front(self, win_id):
        if win_id in self.windows:
            win = self.windows.pop(win_id)
            self.windows[win_id] = win

    def cleanup_closed_windows(self):
        to_remove = [win_id for win_id, win in self.windows.items() if win.should_close]
        for win_id in to_remove:
            del self.windows[win_id]
            if self.focused_id == win_id:
                self.focused_id = None
canvas = tk.Canvas(root, width=fb.width, height=fb.height)
canvas.pack()

def on_click(event):
    x, y = event.x, event.y
    wm.handle_click(x, y)

def on_motion(event):
    x, y = event.x, event.y
    wm.handle_mouse_move(x, y)

def on_release(event):
    wm.handle_mouse_release()

canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", on_motion)
canvas.bind("<ButtonRelease-1>", on_release)

def update():
    wm.draw_all()
    img = fb.to_image()
    photo = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=photo, anchor=tk.NW)
    canvas.image = photo  # prevent GC
    root.after(30, update)

# Example windows/buttons to test:
win_id = wm.create_window(20, 20, 150, 100, "Test Win")

# Add a button inside the window
def on_button_click():
    print("Button clicked!")

button = Button(10, 30, 60, 15, "Click", callback=on_button_click)
wm.get_window(win_id).widgets.append(button)

update()
root.mainloop()