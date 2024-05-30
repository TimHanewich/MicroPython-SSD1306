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