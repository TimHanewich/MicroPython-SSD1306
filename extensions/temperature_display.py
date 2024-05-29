import machine
import ssd1306
import time
import framebuf

# create I2C interface
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15)) # I have my display hooked up to pins 14 and 15 (for I2C)

# create SSD1306 interface
display_width:int = 128
display_height:int = 64
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# turn on all pixels
oled.fill(1) # make the change
oled.show() # show the update
time.sleep(0.25)

# turn off all pixels (blank display)
oled.fill(0)
oled.show()
time.sleep(0.25)

def post_char(char:str, size:int, x, y) -> None:
    f = open(str(size) + "x" + str(size) + "/" + char, "rb")
    data = f.read()
    f.close()
    fb = framebuf.FrameBuffer(bytearray(data), size, size, framebuf.MONO_HLSB)
    oled.blit(fb, x, y)

def display(temperature:int, low:int, high:int) -> None:
    oled.fill(0)
    
    # display temp - always at Y:8
    if len(str(temperature)) == 2: # if 2 characters, display at X:48 and X:64
        post_char(str(temperature)[0], 16, 48, 8)
        post_char(str(temperature)[1], 16, 64, 8)
    elif len(str(temperature)) == 3: # if 3 charaters, display at X:40, X:56, X:72
        post_char(str(temperature)[0], 16, 40, 8)
        post_char(str(temperature)[1], 16, 56, 8)
        post_char(str(temperature)[2], 16, 72, 8)

    # place low
    if len(str(low)) == 2:
        post_char("l", 8, 18, 44)
        # 4 pixel space
        post_char(str(low)[0], 8, 30, 44)
        post_char(str(low)[1], 8, 38, 44)
    elif len(str(low)) == 3:
        post_char("l", 8, 14, 44)
        # 4 pixel space
        post_char(str(low)[0], 8, 26, 44)
        post_char(str(low)[1], 8, 34, 44)
        post_char(str(low)[2], 8, 42, 44)

    # place high
    if len(str(high)) == 2:
        post_char("h", 8, 82, 44)
        # 4 pixel space
        post_char(str(high)[0], 8, 94, 44)
        post_char(str(high)[1], 8, 102, 44)
    elif len(str(high)) == 3:
        post_char("h", 8, 78, 44)
        # 4 pixel space
        post_char(str(high)[0], 8, 90, 44)
        post_char(str(high)[1], 8, 98, 44)
        post_char(str(high)[2], 8, 106, 44)
    
    # show
    oled.show()


