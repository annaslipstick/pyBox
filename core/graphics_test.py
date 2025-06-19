import tkinter as tk
from PIL import Image, ImageTk

def draw_text(win, x, y, text, color):
    # Minimal text drawing placeholder:
    # Just fill pixels in a crude way for each char — you can improve this later
    for i, ch in enumerate(text):
        # For simplicity, draw a white block for each char
        for dx in range(3):
            for dy in range(5):
                px = x + i*4 + dx
                py = y + dy
                if 0 <= px < win.w and 0 <= py < win.h:
                    win.set_pixel(px, py, color)

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

    def blit_to_fb(self, fb, focused=False):
        if not self.visible:
            return

        border_color = (200, 200, 200)
        title_height = 12
        title_bg = (50, 50, 100) if focused else (30, 30, 30)
        close_btn_color = (200, 60, 60)

        # Draw border
        for x in range(self.w):
            for y in range(self.h):
                tx = self.x + x
                ty = self.y + y

                if x == 0 or y == 0 or x == self.w - 1 or y == self.h - 1:
                    fb.set_pixel(tx, ty, border_color)
                elif y < title_height:
                    fb.set_pixel(tx, ty, title_bg)
                elif y >= title_height:
                    fb.set_pixel(tx, ty, self.buffer[x][y])
                else:
                    fb.set_pixel(tx, ty, self.buffer[x][y])

        # Draw close button
        for dx in range(6):
            for dy in range(6):
                cx = self.x + self.w - 8 + dx
                cy = self.y + 3 + dy
                fb.set_pixel(cx, cy, close_btn_color)

        # Draw widgets
        for widget in self.widgets:
            widget.draw(self)

        # Draw title text on title bar
        draw_text(self, 5, 2, self.title, (255, 255, 255))


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
                color = border if i in (0, self.w - 1) or j in (0, self.h - 1) else bg
                win.set_pixel(self.x + i, self.y + j, color)

        draw_text(win, self.x + 3, self.y + 2, self.text, text_color)

    def handle_click(self, x, y):
        if self.x <= x < self.x + self.w and self.y <= y < self.y + self.h:
            if self.callback:
                self.callback()
            return True
        return False

    def handle_hover(self, x, y):
        self.hover = self.x <= x < self.x + self.w and self.y <= y < self.y + self.h


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

    def handle_mouse_release(self):
        for win in self.windows.values():
            win.dragging = False

    def handle_mouse_move(self, x, y):
        for win in self.windows.values():
            if win.dragging:
                dx, dy = win.drag_offset
                win.x = x - dx
                win.y = y - dy


class GraphicsWindow:
    def __init__(self, framebuffer, scale=4):
        self.fb = framebuffer
        self.scale = scale
        self.root = tk.Tk()
        self.root.title("PyBox VM Display")
        self.canvas = tk.Canvas(
            self.root,
            width=self.fb.width * scale,
            height=self.fb.height * scale
        )
        self.canvas.pack()
        self.wm = WindowManager(self.fb)

        self.tk_image = None
        self.running = True
        self.event_queue = []

        self.canvas.bind("<Button-1>", self._on_mouse_click)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.canvas.bind("<B1-Motion>", self._on_mouse_motion)
        self.root.bind("<Key>", self._on_key_press)

    def _on_mouse_click(self, event):
        x = event.x // self.scale
        y = event.y // self.scale
        self.wm.handle_click(x, y)
        self.event_queue.append({"type": "click", "x": x, "y": y})

    def _on_mouse_release(self, event):
        self.wm.handle_mouse_release()

    def _on_mouse_motion(self, event):
        x = event.x // self.scale
        y = event.y // self.scale
        self.wm.handle_mouse_move(x, y)

    def _on_key_press(self, event):
        self.event_queue.append({"type": "key", "key": event.char})

    def get_events(self):
        events = self.event_queue[:]
        self.event_queue.clear()
        return events

    def update(self):
        self.wm.draw_all()
        img = self.fb.to_image().resize(
            (self.fb.width * self.scale, self.fb.height * self.scale),
            resample=Image.NEAREST
        )
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        if self.running:
            self.root.after(33, self.update)

    def run(self):
        self.update()
        self.root.mainloop()


if __name__ == "__main__":
    fb = FrameBuffer(160, 120)
    gw = GraphicsWindow(fb, scale=4)
    wm = gw.wm

    win_id = wm.create_window(20, 20, 100, 60, "Test Window")
    win = wm.get_window(win_id)

    def on_button_click():
        print("Button clicked!")

    btn = Button(10, 20, 60, 12, "Click Me", callback=on_button_click)
    win.widgets.append(btn)

    gw.run()
