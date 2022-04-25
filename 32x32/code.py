import time
import board
import displayio
import rgbmatrix
import framebufferio
import random
import gc

from math import sin,pi,cos

print("Test")

# clear display
displayio.release_displays()

# setup rgbmatrix. this is using an RP2040 with circuitpython 6.3.0
# a feather rgbmatrix adapter and a 32x32 HUB75 panel
matrix = rgbmatrix.RGBMatrix(
    width=32,
    bit_depth=6,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.D25, board.D24, board.A3, board.A2],
    clock_pin=board.D13,
    latch_pin=board.D0,
    output_enable_pin=board.D1,
    doublebuffer=True,
)

# fps code from the scrolling text with background image example
display = framebufferio.FramebufferDisplay(
    matrix,
    rotation=0,
    auto_refresh=False,
)

# Create a bitmap with two colors
bitmap = displayio.Bitmap(display.width, display.height, 32)

# Create a two color palette
palette = displayio.Palette(32)
for i in range(8):
    r = 8*i
    g = 0
    b = 0
    palette[i] = r*65536+g*256+b

for i in range(8):
    r = 8*(7-i)
    g = 8*i
    b = 0
    palette[i+8] = r*65536+g*256+b

for i in range(8):
    r = 0
    g = 8*(7-i)
    b = 8*i
    palette[i+16] = r*65536+g*256+b

for i in range(8):
    r = 0
    g = 0
    b = 8*(7-i)
    palette[i+24] = r*65536+g*256+b

# Create a TileGrid using the Bitmap and Palette
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)


target_fps = 5
ft = 1 / target_fps
now = t0 = time.monotonic_ns()
deadline = t0 + ft

# create displayio group
group = displayio.Group()

# Add the TileGrid to the Group
group.append(tile_grid)

# show the group on the display
display.show(group)

# Draw even more pixels
def update_tilegrid(c):
    for x in range(1):
        for y in range(1):
            bitmap[x, y] = c

def find_cells(x,y):
    n = cells[(x-1)&31][(y-1)&31]
    n += cells[(x)&31][(y-1)&31]
    n += cells[(x+1)&31][(y-1)&31]
    n += cells[(x-1)&31][(y)&31]
    n += cells[(x+1)&31][(y)&31]
    n += cells[(x-1)&31][(y+1)&31]
    n += cells[(x)&31][(y+1)&31]
    n += cells[(x+1)&31][(y+1)&31]
    return n

cells = [[0 for a in range(32)] for b in range(32)]

live_cells = [  (15,15),(16,15),(17,15),
                (15,16),        (17,16),
                (15,17),        (17,17)]

for x,y in live_cells:
    cells[x][y] = 1

mem_used = 0
dead_cells = []
timer = 0
color = 0
#update_tilegrid(counter)
while True:
    timer += 1
    color += 1
    if color == 31 :
        color = 1
    if timer <300: #300:
        for x,y in dead_cells:
            bitmap[x,y] = 0
            cells[x][y] = 0

        for x,y in live_cells:
            if bitmap[x,y] == 0:
                d = color+(abs(x-16)+abs(y-16)) & 31
                if d==0 or d==31:
                    d=1
                bitmap[x,y] = d #color

        dead_cells = []


        new_live_cells = list()
        for x,y in live_cells:
            n = find_cells(x,y)
            if n==2 or n==3:
                new_live_cells.append((x,y))
            else:
                dead_cells.append((x,y))

        for x in range(1,31):
            for y in range(1,31):
                if cells[x][y]==0:
                    n = find_cells(x,y)
                    if n == 3:
                        new_live_cells.append((x,y))
        

        live_cells = new_live_cells.copy()
        for x,y in live_cells:
            cells[x][y] = 1
    else:
        for a in live_cells:
            if a not in dead_cells:
                dead_cells.append(a)
        #dead_cells = dead_cells.extend(live_cells)
        timer = 0
        cells = [[0 for a in range(32)] for b in range(32)]

        live_cells = [  (15,15),(16,15),(17,15),
                        (15,16),        (17,16),
                        (15,17),        (17,17)]

        for x,y in live_cells:
            cells[x][y] = 1


    mem_used += gc.mem_free()
    mem_used /= 2
    if timer & 31 == 0:
        print(mem_used)
        
    # fps code from the scrolling text with background image example
    display.refresh(target_frames_per_second=target_fps, minimum_frames_per_second=1)
    while True:
        now = time.monotonic_ns()
        if now > deadline:
            break
        time.sleep((deadline - now) * 1e-9)
    deadline += ft
