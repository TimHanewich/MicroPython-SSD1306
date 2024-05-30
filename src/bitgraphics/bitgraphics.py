import json
import sys

class BitGraphic:
    def __init__(self, jsons:str = None, path:str = None) -> None:
        self.bits:list[bool] = []
        self.width:int = 0
        self.height:int = 0

        # if they provided JSON, deserialize using that
        if jsons != None:
            self.from_json(jsons)

        # if they provided a path, deserialize using the JSON within that
        if path != None:
            f = open(path, "r")
            txt = f.read()
            f.close()
            self.from_json(txt)

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
        if left_most == None:
            left_most = 0
        return left_most
    
    @property
    def right(self) -> int:
        """Returns the right-most position (max x)"""
        right_most:int = None
        for bgp in self.BitGraphics:
            right:int = bgp[1] + bgp[0].width # x shift + width of the graphic
            if right_most == None or right > right_most:
                right_most = right
        if right_most == None:
            right_most = 0
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
        if top_most == None:
            top_most = 0
        return top_most
    
    @property
    def bottom(self) -> int:
        """Returns the bottom-most position (max y)"""
        bottom_most:int = None
        for bgp in self.BitGraphics:
            bottom:int = bgp[2] + bgp[0].height # y shift + height of graphic
            if bottom_most == None or bottom > bottom_most:
                bottom_most = bottom
        if bottom_most == None:
            bottom_most = 0
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
#if sys.platform == "rp2":
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
    
class Typewriter:

    def __init__(self) -> None:
        self.characters:list[tuple[str, BitGraphic]] = [] # character, graphic pair

        # set up all characters
        bg_folder:str = "16x16/"
        self.characters.append(("0", BitGraphic(path=bg_folder + "/0.json")))
        self.characters.append(("1", BitGraphic(path=bg_folder + "/1.json")))
        self.characters.append(("2", BitGraphic(path=bg_folder + "/2.json")))
        self.characters.append(("3", BitGraphic(path=bg_folder + "/3.json")))
        self.characters.append(("4", BitGraphic(path=bg_folder + "/4.json")))
        self.characters.append(("5", BitGraphic(path=bg_folder + "/5.json")))
        self.characters.append(("6", BitGraphic(path=bg_folder + "/6.json")))
        self.characters.append(("7", BitGraphic(path=bg_folder + "/7.json")))
        self.characters.append(("8", BitGraphic(path=bg_folder + "/8.json")))
        self.characters.append(("9", BitGraphic(path=bg_folder + "/9.json")))
        self.characters.append(("a", BitGraphic(path=bg_folder + "/a.json")))
        self.characters.append(("a", BitGraphic(path=bg_folder + "/a.json")))
        self.characters.append(("a", BitGraphic(path=bg_folder + "/a.json")))
        self.characters.append(("a", BitGraphic(path=bg_folder + "/a.json")))
        self.characters.append(("b", BitGraphic(path=bg_folder + "/b.json")))
        self.characters.append(("c", BitGraphic(path=bg_folder + "/c.json")))
        self.characters.append(("d", BitGraphic(path=bg_folder + "/d.json")))
        self.characters.append(("e", BitGraphic(path=bg_folder + "/e.json")))
        self.characters.append(("f", BitGraphic(path=bg_folder + "/f.json")))
        self.characters.append(("g", BitGraphic(path=bg_folder + "/g.json")))
        self.characters.append(("h", BitGraphic(path=bg_folder + "/h.json")))
        self.characters.append(("i", BitGraphic(path=bg_folder + "/i.json")))
        self.characters.append(("j", BitGraphic(path=bg_folder + "/j.json")))
        self.characters.append(("k", BitGraphic(path=bg_folder + "/k.json")))
        self.characters.append(("l", BitGraphic(path=bg_folder + "/l.json")))
        self.characters.append(("m", BitGraphic(path=bg_folder + "/m.json")))
        self.characters.append(("n", BitGraphic(path=bg_folder + "/n.json")))
        self.characters.append(("o", BitGraphic(path=bg_folder + "/o.json")))
        self.characters.append(("p", BitGraphic(path=bg_folder + "/p.json")))
        self.characters.append(("q", BitGraphic(path=bg_folder + "/q.json")))
        self.characters.append(("r", BitGraphic(path=bg_folder + "/r.json")))
        self.characters.append(("s", BitGraphic(path=bg_folder + "/s.json")))
        self.characters.append(("t", BitGraphic(path=bg_folder + "/t.json")))
        self.characters.append(("u", BitGraphic(path=bg_folder + "/u.json")))
        self.characters.append(("v", BitGraphic(path=bg_folder + "/v.json")))
        self.characters.append(("w", BitGraphic(path=bg_folder + "/w.json")))
        self.characters.append(("x", BitGraphic(path=bg_folder + "/x.json")))
        self.characters.append(("y", BitGraphic(path=bg_folder + "/y.json")))
        self.characters.append(("z", BitGraphic(path=bg_folder + "/z.json")))

    def write(self, text:str, width:int, height:int) -> BitGraphic:
        """Types text into a single BitGraphic."""

        # list of all BitGraphics
        ToReturn:BitGraphicGroup = BitGraphicGroup()
        for c in text.lower():

            # find appropriate one
            CorrectBG:BitGraphic = None
            for cbg in self.characters:
                if cbg[0].lower() == c.lower(): # validate it is the correct character
                    if cbg[1].width == width and cbg[1].height == height: # validate the width and height match
                        CorrectBG = cbg[1] # select the BitGraphic (at index 1)
            
            # if there wasn't one that was found, throw an error
            if CorrectBG == None:
                raise Exception("BitGraphic of character '" + str(c) + "' and size '" + str(width) + "x" + str(height) + " was not found in the list of available BitGraphic characters in the Typewriter.")
            
            # add it!
            ToReturn.add(CorrectBG, ToReturn.width, 0)

        # fuse and return
        return ToReturn.fuse()




