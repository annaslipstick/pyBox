# Basic 5x5 pixel font
PIXEL_FONT = {
    "A": [
        "  #  ",
        " # # ",
        "#####",
        "#   #",
        "#   #"
    ],
    "B": [
        "#### ",
        "#   #",
        "#### ",
        "#   #",
        "#### "
    ],
    # Add more as needed: C-Z, a-z, 0-9, etc.
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
