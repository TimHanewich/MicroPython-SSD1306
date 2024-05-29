import PIL.Image
import os

# returns buffer (bytes), width, height
def image_to_buffer(img_path:str, threshold:float = 0.5, resize:tuple[int, int] = None) -> tuple[bytes, int, int]:
    """
    Converts a bitmap image (JPG, PNG, etc.) to a byte buffer, translating each RGB pixel into a single white/black dot that can be displayed on an OLED display.
    
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
    

    # open image
    i = PIL.Image.open(img_path)

    # resize if desired
    if resize != None:
        i = i.resize(resize)

    # record size
    width, height = i.size

    # calculate the threshold. In other words, the average RGB value that the pixel has to be below (filled in with darkness) to be considered "on" and above to be considered "off"
    thresholdRGB:int = 255 - int(round(threshold * 255, 0))
    
    # get a list of individual bits for each pixel (True is filled in, False is not filled in)
    bits:list[bool] = []
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
            bits.append(filled)

    # now that we have all the bits, chunk them by 8 and convert
    BytesToReturn:bytearray = bytearray()
    bit_collection_buffer:list[bool] = []
    for bit in bits:

        # add it
        bit_collection_buffer.append(bit)

        # if we are now at 8, convert and append
        if len(bit_collection_buffer) == 8:

            # convert to 1's and 0's
            AsStr:str = ""
            for bit in bit_collection_buffer:
                if bit:
                    AsStr = AsStr + "1"
                else:
                    AsStr = AsStr + "0"
            
            # convert to byte
            b = int(AsStr, 2)

            # Add it
            BytesToReturn.append(b)

            # clear out bit collection buffer
            bit_collection_buffer.clear()

    # return!
    return (bytes(BytesToReturn), width, height)

def images_to_buffers(original_bitmaps_dir:str, output_dir:str, threshold:float = 0.5, resize:tuple[int, int] = None) -> None:
    """Converts all bitmap images in a folder to a buffer in another file. Great for converting a group of bitmap images to various sizes, ready for display on SSD-1306."""

    for filename in os.listdir(original_bitmaps_dir):
        fullpath = os.path.join(original_bitmaps_dir, filename)
        converted = image_to_buffer(fullpath, resize=resize, threshold=threshold)
        
        # trim off the ".png"
        fn_only:str = filename[0:-4]
        result_path = os.path.join(output_dir, fn_only)
        f = open(result_path, "wb")
        f.write(bytes(converted[0]))
        f.close()

        # print
        print("Finished converting '" + filename + "'!")