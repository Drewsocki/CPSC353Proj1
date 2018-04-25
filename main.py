import math
import sys
from PIL import Image

# a function to convert strings into bits
def str_bits(string1):
    bit_list = []
    for c in string1:
        bits = bin(c)[2:]
        bits = '00000000'[len(bits):] + bits
        bit_list.extend([int(b) for b in bits])
    return bit_list

# a function to convert bits into strings
def bits_str(bits):
    chars = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)

#our encoding function. Takes in a text and image file. Returns an image file.
def encoder(text, image):

    # load our original jpg image
    image_file = Image.open(image)
    image_pix = image_file.load()
    # load our future image
    new_image = Image.new(image_file.mode, image_file.size)
    new_image_pix = new_image.load()

    # open our text file, get a size, and a convert the text to bits
    text_file = open(text, "r")
    text_file = text_file.read()
    text_file = text_file.encode()
    text_file_bits = str_bits(text_file)

    # get width, height, num rows, num columns, and number of pixels
    width, height = image_file.size
    num_pix = width * height
    row = height - 1
    column = width - 1

    # check to see if the amount of bits we have to encode are more then the amount of pixel spots we have
    if len(text_file_bits) > ((num_pix - 11) * 3):
        raise ValueError("Error - Text bigger than image")

    num_loops = bin(int(math.ceil(len(text_file_bits) / 3 + 1)))
    num_loops = num_loops[2:]
    i = len(num_loops) - 1
    #for loop to set last 11 pixels rgb values to binary size of text file
    for x in range(11):
        red, green, blue = image_pix[column - x, row]
        # red, green, blue = an rgb value
        red = int(bin(red), 2)
        green = int(bin(green), 2)
        blue = int(bin(blue), 2)

        if i >= 0:
            red = red | (1 << 0)
            if num_loops[i] != '1':
                red &= ~(1 << 0)
            i -= 1
        else:
            red &= ~(1 << 0)
        if i >= 0:
            green = green | (1 << 0)
            if num_loops[i] != '1':
                green &= ~(1 << 0)
            i -= 1
        else:
            green &= ~(1 << 0)
        if i >= 0:
            blue = blue | (1 << 0)
            if num_loops[i] != '1':
                blue &= ~(1 << 0)
            i -= 1
        else:
            blue &= ~(1 << 0)

        new_image_pix[column - x, row] = (red, green, blue)

    index = 0
    # set the remaining pixels rgb values to the necessary bit value for the text
    # the for loop is in reverse and ignores the last 11 pixels of the image so that we start from the 12th
    for y in range(row, -1, -1):
        for x in range(column, -1, -1):
            if y == row - 1 and x >= column - 11:
                continue

            red, green, blue = image_pix[x, y]
            # red, green, blue = an rgb value
            red = int(bin(red), 2)
            green = int(bin(green), 2)
            blue = int(bin(blue), 2)

            if index < len(text_file_bits):
                red = red | (1 << 0)
                if text_file_bits[index] != 1:
                    red &= ~(1 << 0)
                index += 1
            if index < len(text_file_bits):
                green = green | (1 << 0)
                if text_file_bits[index] != 1:
                    blue &= ~(1 << 0)
                index += 1
            if index < len(text_file_bits):
                green = green | (1 << 0)
                if text_file_bits[index] != 1:
                    green &= ~(1 << 0)
                index += 1
            new_image_pix[x, y] = (red, green, blue)
    return new_image

# our function for decoding a png file. Takes in a png file and opens and loads it
def decoder(image):
    image_file = Image.open(image)
    image_file_pix = image_file.load()

    width, height = image_file.size
    row = height - 1
    column = width - 1

    size_of_text = ''
    # get the last 11 pixels of the image file
    # get there rgb values last bit
    # use these values to compute size of the text
    for x in range(11):
        red, green, blue = image_file_pix[column - x, row]
        # red, green, blue = an rgb value
        red = int(bin(red), 2)
        green = int(bin(green), 2)
        blue = int(bin(blue), 2)
        size_of_text = str(red & 0b1) + size_of_text
        size_of_text = str(green & 0b1) + size_of_text
        size_of_text = str(blue & 0b1) + size_of_text

    count = int(size_of_text, 2)
    count2 = count
    text = []
    index = 0
    index2 = index
    # reverse loop through the image
    # if the index equals count we break the loop
    # otherwise we keep appending the 0th bit of each rgb value to the end of text
    for i in range(row, -1, -1):
        if count == index:
            break
        for j in range(column, -1, -1):
            if count2 == index2:
                break
            red, green, blue = image_file_pix[i, j]
            # red, green, blue = an rgb value
            red = int(bin(red), 2)
            green = int(bin(green), 2)
            blue = int(bin(blue), 2)
            if i == row and j >= column - 11:
                continue
            text.append(red & 0b1)
            text.append(green & 0b1)
            text.append(blue & 0b1)

            index += 1
            index2 += 1
    return_text = bits_str(text)

    return return_text
# end of our defs
# where our file begins running
# default for command
command = ' '

# get our arguments from running the file
# 4 arguments after python.exe sets up for encode
if len(sys.argv) == 4:
    command = sys.argv[1]

# 3 arguments after python.exe sets up for decode
if len(sys.argv) == 3:
    command = sys.argv[1]

# make sure they typed in encode as the command
if command == "encode":
    # check if the image file is in jpeg or jpg format if so we run encoder
    if not sys.argv[3].endswith(".jpeg") and not sys.argv[3].endswith("jpg"):
        print("Sorry your image file needs to be a jpeg or jpg file")
        exit()
    encoder(sys.argv[2], sys.argv[3]).save('output.png')
    
# make sure they typed in decode as the command
elif command == "decode":
    # check if the iamge file is in png format if so then we run decode
    if not sys.argv[2].endswith(".png"):
        print("Sorry your file needs to be a png file")
        exit()
    print(decoder(sys.argv[2]))
# if neither command was run then we just exit the program
else:
    print("Invalid Entry: Try one of two")
    print("main.py encode \"example text\" \"example image/jpg\"")
    print("main.py decode \"example image/jpg\"")
    exit()
