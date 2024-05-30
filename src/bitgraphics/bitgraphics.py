import json
import sys

class BitGraphic:
    def __init__(self) -> None:
        self.bits:list[bool] = []
        self.width:int = 0
        self.height:int = 0

    def bit(self, x:int, y:int) -> bool:
        """Returns the bit value for a given coordinate"""
        bit_index:int = (y * self.width) + x
        return self.bits[bit_index]

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
        """Add a BitGraphic to the group with a relative position to the group"""
        self.BitGraphics.append((bg, relative_x, relative_y))

    @property
    def left(self) -> int:
        """Returns the left-most position (min x)"""
        left_most:int = None
        for bgp in self.BitGraphics:
            if left_most == None or bgp[1] < left_most:
                left_most = bgp[1]
        return left_most
    
    @property
    def right(self) -> int:
        """Returns the right-most position (max x)"""
        right_most:int = None
        for bgp in self.BitGraphics:
            right:int = bgp[1] + bgp[0].width # x shift + width of the graphic
            if right_most == None or right > right_most:
                right_most = right
        return right_most

    @property
    def width(self) -> int:
        """Returns the full width of the combined graphics"""
        return self.right - self.left
    
    @property
    def top(self) -> int:
        """Returns the top-most position (min y)"""
        top_most:int = None
        for bgp in self.BitGraphics:
            if top_most == None or bgp[2] < top_most:
                top_most = bgp[2]
        return top_most
    
    @property
    def bottom(self) -> int:
        """Returns the bottom-most position (max y)"""
        bottom_most:int = None
        for bgp in self.BitGraphics:
            bottom:int = bgp[2] + bgp[0].height # y shift + height of graphic
            if bottom_most == None or bottom > bottom_most:
                bottom_most = bottom
        return bottom_most
    
    @property
    def height(self) -> int:
        """Returns the full height of the combined graphics"""
        return self.bottom - self.top

    def fuse(self) -> BitGraphic:
        """Combines all BitGraphics into a single BitGraphic."""

        ToReturn:BitGraphic = BitGraphic()
        ToReturn.width = self.width
        ToReturn.height = self.height
        ToReturn.bits.clear()
        
        for y in range (self.top, self.bottom):
            for x in range(self.left, self.right):

                # declare a variable for what this bit will end up being
                ThisBit:bool = False
                
                # is this pixel covered by a BitGraphic?
                for bgp in self.BitGraphics:
                    if x >= bgp[1] and x < bgp[1] + bgp[0].width and y >= bgp[2] and y < bgp[2] + bgp[0].height: # within the bounds
                        relative_x:int = x - bgp[1]
                        relative_y:int = y - bgp[2]
                        value:bool = bgp[0].bit(relative_x, relative_y)
                        if value:
                            ThisBit = True # set to true if it is filled in

                # add it!
                ToReturn.bits.append(ThisBit)
        
        return ToReturn




# Only if on pi
if sys.platform == "rp2":
    import ssd1306
    import machine

    class BitGraphicDisplay:

        def __init__(self, i2c:machine.I2C, width:int, height:int) -> None:
            self._width = width
            self._height = height
            self.oled = ssd1306.SSD1306_I2C(width, height, i2c)

        def show(self) -> None:
            self.oled.show()

        def display(self, bg:BitGraphic, x:int=None, y:int=None, center:tuple[int|float, int|float] = None) -> None:

            # if center was not null, calculate x and y automatically, centering on that point
            if center != None:

                # firstly, if center was provided as a float (between 0 and 1), they are specifying it as a percentage of the width and height. If it was an int, it is absolute
                if type(center[0] == float):
                    nc0 = int(round(center[0] * self._width, 0))
                    center = (nc0, center[1])
                if type(center[1] == float):
                    nc1 = int(round(center[1] * self._height, 0))
                    center = (center[0], nc1)

                # calculate center point
                x = center[0] - int(round(bg.width / 2, 0))
                y = center[1] - int(round(bg.height / 2, 0))

            # display BitGraphic
            for yt in range(0, bg.height):
                for xt in range(0, bg.width):

                    # determine index in the bits array
                    BitIndex:int = (yt * bg.width) + xt

                    # determine pixel position
                    pix_x:int = x + xt
                    pix_y:int = y + yt
                    
                    if bg.bits[BitIndex] == False:
                        self.oled.pixel(pix_x, pix_y, 0)
                    elif bg.bits[BitIndex] == True:
                        self.oled.pixel(pix_x, pix_y, 1)
        



