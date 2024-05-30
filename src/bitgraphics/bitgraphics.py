import json
import sys

class BitGraphic:
    def __init__(self) -> None:
        self.bits:list[bool] = []
        self.width:int = 0
        self.height:int = 0

    def to_json(self) -> str:

        # assemble bits as 1's and 0's
        bitsbin:str = ""
        for bit in self.bits:
            if bit:
                bitsbin = bitsbin + "1"
            else:
                bitsbin = bitsbin + "0"

        ToReturn = {"bits": bitsbin, "width": self.width, "height": self.height}
        return json.dumps(ToReturn)
    
    def from_json(self, jsons:str) -> None:

        obj = json.loads(jsons)

        # deserialize bits
        self.bits.clear()
        for c in obj["bits"]:
            if c == "0":
                self.bits.append(False)
            elif c == "1":
                self.bits.append(True)
            else:
                raise Exception("Character '" + c + "' in JSON-serializes 'bits' property is not a valid 0 or 1.")
        
        # width and height
        self.width = obj["width"]
        self.height = obj["height"]
    
    def from_file(self, path:str) -> None:
        f = open(path, "r")
        txt:str = f.read()
        self.from_json(txt)



class BitGraphicGroup:
    def __init__(self) -> None:
        self.BitGraphics:list[tuple[BitGraphic, int, int]] = [] # tuple of (BitGraphic, width, height)

    def add(self, bg:BitGraphic, relative_x:int, relative_y:int) -> None:
        self.BitGraphics.append((bg, relative_x, relative_y))

    @property
    def width(self) -> int:
        
        # find the left-most pixel
        left_most:int = None
        for bgp in self.BitGraphics:
            if left_most == None or bgp[1] < left_most:
                left_most = bgp[1]
            
        # find the right-most pixel
        right_most:int = None
        for bgp in self.BitGraphics:
            right:int = bgp[1] + bgp[0].width # x shift + width of the graphic
            if right_most == None or right > right_most:
                right_most = right
        
        return right_most - left_most
    
    @property
    def height(self) -> int:

        # find the top-most pixel
        top_most:int = None
        for bgp in self.BitGraphics:
            if top_most == None or bgp[2] < top_most:
                top_most = bgp[2]
            
        # find the bottom-most pixel
        bottom_most:int = None
        for bgp in self.BitGraphics:
            bottom:int = bgp[2] + bgp[0].height # y shift + height of graphic
            if bottom_most == None or bottom > bottom_most:
                bottom_most = bottom

        return bottom_most - top_most

# Only if on pi
if sys.platform == "rp2":
    import ssd1306
    import machine

    class BitGraphicDisplay:

        def __init__(self, i2c:machine.I2C, width:int, height:int) -> None:
            self.oled = ssd1306.SSD1306_I2C(width, height, i2c)

        def show(self) -> None:
            self.oled.show()

        def display(self, asset:BitGraphic|BitGraphicGroup, x:int, y:int) -> None:

            if type(asset) == BitGraphic: #display single bit graphic
                for yt in range(0, asset.height):
                    for xt in range(0, asset.width):

                        # determine index in the bits array
                        BitIndex:int = (yt * asset.width) + xt

                        # determine pixel position
                        pix_x:int = x + xt
                        pix_y:int = y + yt
                        
                        if asset.bits[BitIndex] == False:
                            self.oled.pixel(pix_x, pix_y, 0)
                        elif asset.bits[BitIndex] == True:
                            self.oled.pixel(pix_x, pix_y, 1)
            
            elif type(asset) == BitGraphicGroup: # BitGraphicGroup
                for bgp in asset.BitGraphics:
                    self.display(bgp[0], x + bgp[1], y + bgp[2])



    