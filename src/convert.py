import PIL.Image
import os
import bitgraphics

def image_to_BitGraphic(img_path:str, threshold:float = 0.5, resize:tuple[int, int] = None) -> bitgraphics.BitGraphic:
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
    ToReturn:bitgraphics.BitGraphic = bitgraphics.BitGraphic()

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