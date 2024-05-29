import machine
import ssd1306
import time
import bitgraphics

# create I2C interface
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15)) # I have my display hooked up to pins 14 and 15 (for I2C)
print(i2c.scan()) # 0x3c is the I2C address of the SSD1306. As an integer, 60.

# create SSD1306 interface
display_width:int = 128
display_height:int = 64
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def display(bg:bitgraphics.BitGraphic, x:int, y:int, show:bool = False) -> None:

    #loop
    for yt in range(0, bg.height):
        for xt in range(0, bg.width):

            # determine index in the bits array
            BitIndex:int = (yt * bg.width) + xt

            # determine pixel position
            pix_x:int = x + xt
            pix_y:int = y + yt
            
            if bg.bits[BitIndex] == False:
                oled.pixel(pix_x, pix_y, 0)
            elif bg.bits[BitIndex] == True:
                oled.pixel(pix_x, pix_y, 1)

    # show
    if show:
        oled.show()


def type(txt:str) -> None:

    # reset
    oled.fill(0)

    # collect all bitgraphics
    BGs:list[bitgraphics.BitGraphic] = []

    for char in txt.lower():
        bg = bitgraphics.BitGraphic()
        bg.from_file("16x16/" + char + ".json")
        BGs.append(bg)

    # calculate width
    width:int = 0
    for bg in BGs:
        width = width + bg.width

    # remaining
    rem_width = 128 - width
    on_x:int = int(round(rem_width / 2, 0)) # starting

    # print!
    for bg in BGs:
        display(bg, on_x, 0)
        on_x = on_x + bg.width

    # show at the very end!
    oled.show()
    