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
    
    def from_blank(self, width:int, height:int) -> None:
        """Initializes blank slate with desired width and height"""
        self.width = width
        self.height = height
        
        # create enough bits to suffice
        self.bits.clear()
        for x in range(0, self.width * self.height):
            self.bits.append(False)
    
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
if sys.platform == "rp2":
    import ssd1306
    import machine
    import json

    class BitGraphicDisplay:

        def __init__(self, i2c:machine.I2C, width:int, height:int) -> None:
            self._width = width
            self._height = height
            self.oled = ssd1306.SSD1306_I2C(width, height, i2c)

        def show(self) -> None:
            self.oled.show()

        def display(self, bg:BitGraphic, x:int=None, y:int=None, center:tuple[int|float, int|float] = None) -> None:

            # if  they did not specify either x,y or center, throw error
            if (x == None or y == None) and center == None:
                #raise Exception("You must specify either a fixed (x,y) point or a relative center point when displaying a BitGraphic! You specified neither.")
                x = 0 # default to 0
                y = 0 # default to 0

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
            self.characters.append(("0", BitGraphic(jsons=json.dumps({"bits": "0000011111100000000011111111000000011111111110000001111111111000001111111111110000111110011111000011111001111100001111100111110000111110011111000011111001111100001111100111110000111111111111000001111111111000000111111111100000001111111100000000011111100000", "width": 16, "height": 16}))))
            self.characters.append(("1", BitGraphic(jsons=json.dumps({"bits": "0000000011110000000000011111000000000011111100000000111111110000000011111111000000001111111100000000111111110000000111011111000000000001111100000000000111110000000000011111000000000001111100000000000111110000000000011111000000000001111100000000000111110000", "width": 16, "height": 16}))))
            self.characters.append(("2", BitGraphic(jsons=json.dumps({"bits": "0000111111110000000111111111100000011111111111000011111111111100001111100111110000111110011111000000000011111100000000011111110000000011111110000000011111110000000011111110000000011111110000000001111111111100001111111111110000111111111111000011111111111100", "width": 16, "height": 16}))))
            self.characters.append(("3", BitGraphic(jsons=json.dumps({"bits": "0000111111110000000111111111100000111111111110000011111111111100001111101111110000011111111111000000001111111000000000111111100000000111111111000000001111111100001111100111110000111110011111000011111111111100001111111111110000011111111110000000111111110000", "width": 16, "height": 16}))))
            self.characters.append(("4", BitGraphic(jsons=json.dumps({"bits": "0000000011111000000000011111100000000011111110000000001111111000000001111111100000001111111110000000111111111000000111111111100000111111111100000011111111111100001111111111110000111111111111000011111111111100001111111111110000000000111110000000000011111000", "width": 16, "height": 16}))))
            self.characters.append(("5", BitGraphic(jsons=json.dumps({"bits": "0000111111111100000111111111110000011111111111000001111111111100000111111100000000011111111100000011111111111000001111111111110000111111111111000000110001111100001111100111110000111110011111000011111111111100001111111111110000011111111110000000111111110000", "width": 16, "height": 16}))))
            self.characters.append(("6", BitGraphic(jsons=json.dumps({"bits": "0000011111110000000011111111100000011111111111000011111111111100001111100111110000111111111100000011111111111000001111111111110000111111111111000011111001111100001111100111110000111111011111000011111111111100000111111111110000011111111110000000111111110000", "width": 16, "height": 16}))))
            self.characters.append(("7", BitGraphic(jsons=json.dumps({"bits": "0011111111111100001111111111110000111111111111000011111111111100000000011111100000000001111100000000001111110000000000111110000000000111111000000000011111000000000001111100000000001111110000000000111111000000000011111000000000001111100000000000111110000000", "width": 16, "height": 16}))))
            self.characters.append(("8", BitGraphic(jsons=json.dumps({"bits": "0000111111110000000111111111100000011111111110000001111111111000000111100111100000011111111110000001111111111000000011111111000000011111111110000011111111111100001111100111110000111110011111000011111111111100000111111111100000011111111110000000111111110000", "width": 16, "height": 16}))))
            self.characters.append(("9", BitGraphic(jsons=json.dumps({"bits": "0000111111100000000111111111000000011111111110000011111111111000001111101111110000111110011111000011111011111100001111111111110000011111111111000001111111111100000001111111110000111110111110000011111111111000000111111111100000011111111100000000111111100000", "width": 16, "height": 16}))))

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
                    
                    # raise an exception if we don't have that character
                    raise Exception("BitGraphic of character '" + str(c) + "' and size '" + str(width) + "x" + str(height) + " was not found in the list of available BitGraphic characters in the Typewriter.")
                    
                    # make a blank one
                    # CorrectBG = BitGraphic()
                    # CorrectBG.from_blank(width, height)


                # add it!
                ToReturn.add(CorrectBG, ToReturn.width, 0)

            # fuse and return
            return ToReturn.fuse()

else: # all other platforms (windows, linux, etc.)
    
    import PIL.Image
    import os

    def image_to_BitGraphic(img_path:str, threshold:float = 0.5, resize:tuple[int, int] = None) -> BitGraphic:
        """
        Converts a bitmap image (JPG, PNG, etc.) to a BitGraphic.
        
        Parameters
        ----------
        img_path:str
            The path to the image file.
        threshold:float, optional
            Defines how "dark" each RGB pixel has to be for it to be considered "filled in". Higher threshold values are more discriminating.

        Returns
        -------
        tuple
            A tuple containing:
            - bytes: The image data in bytes that can be loaded into a FrameBuffer in MicroPython.
            - int: The width of the image.
            - int: The height of the image.
        """
        
        # create what we will return
        ToReturn:BitGraphic = BitGraphic()

        # open image
        i = PIL.Image.open(img_path)

        # resize if desired
        if resize != None:
            i = i.resize(resize)

        # record size
        width, height = i.size
        ToReturn.width = width
        ToReturn.height = height

        # calculate the threshold. In other words, the average RGB value that the pixel has to be below (filled in with darkness) to be considered "on" and above to be considered "off"
        thresholdRGB:int = 255 - int(round(threshold * 255, 0))
        
        # get a list of individual bits for each pixel (True is filled in, False is not filled in)
        ToReturn.bits.clear()
        for y in range(0, height):
            for x in range(0, width):
                pix:tuple[int, int, int, int] = i.getpixel((x, y)) #[R,G,B,A]
                
                # determine, is this pixel solid (filled in BLACK) or not (filled in WHITE)?
                filled:bool = False
                if len(pix) == 3 or pix[3] > 0: # if there are only three values, it is a JPG, so there is now alpha channel. Evaluate the color. If the alpha channel, it is a PNG. If the alpha is set to 0, that means the pixel is invisible, so don't consider it. Just consider it as not being shown.
                    avg:int = int(round((pix[0] + pix[1] + pix[2]) / 3, 0))
                    if avg <= thresholdRGB: # it is dark
                        filled = True

                # add it to the list of bits
                ToReturn.bits.append(filled)

        # return!
        return ToReturn

    def images_to_BitGraphics(original_bitmaps_dir:str, output_dir:str, threshold:float = 0.5, resize:tuple[int, int] = None) -> None:
        """Converts all bitmap images in a folder to a buffer in another file. Great for converting a group of bitmap images to various sizes, ready for display on SSD-1306."""

        for filename in os.listdir(original_bitmaps_dir):
            fullpath = os.path.join(original_bitmaps_dir, filename)
            converted = image_to_BitGraphic(fullpath, resize=resize, threshold=threshold)
            
            # trim off the ".png" or ".jpg"
            fn_only:str = filename[0:-4]
            result_path = os.path.join(output_dir, fn_only + ".json")
            f = open(result_path, "w")
            f.write(converted.to_json())

            # print
            print("Finished converting '" + filename + "'!")

