import convert
import PIL.Image
import os

folder = r"C:\Users\timh\Downloads\oled\graphics\alphanumeric\bitmaps"
output_folder = r"C:\Users\timh\Downloads\oled\graphics\alphanumeric\32x32"

for filename in os.listdir(folder):
    fullpath = os.path.join(folder, filename)
    converted = convert.image_to_buffer(fullpath, resize=(32,32), threshold=0.1)
    
    # trim off the ".png"
    num_only:str = filename[0:-4]
    result_path = os.path.join(output_folder, num_only)
    f = open(result_path, "wb")
    f.write(bytes(converted[0]))
    f.close()

    # print
    print("Finished converting '" + filename + "'!")