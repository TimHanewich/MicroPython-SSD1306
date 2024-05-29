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
time.sleep(1)

# turn off all pixels (blank display)
oled.fill(0)
oled.show()
time.sleep(1)

def post_char(c:str, x:int, y:int) -> None:
    f = open("32x32/" + str(c), "rb")
    data = f.read()
    f.close()
    fb = framebuf.FrameBuffer(bytearray(data), 32, 32, framebuf.MONO_HLSB)
    oled.blit(fb, x, y)

def txt(t:str) -> None:
    if len(t) == 2:
        oled.fill(0)
        post_char(t[0], 32, 16)
        post_char(t[1], 64, 16)
        oled.show()
    elif len(t) == 3:
        oled.fill(0)
        post_char(t[0], 16, 16)
        post_char(t[1], 48, 16)
        post_char(t[2], 80, 16)
        oled.show()
    else:
        print("Unable to show text of length " + str(len(t)))