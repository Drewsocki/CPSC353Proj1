import math
import sys
from PIL import Image


def str_bits(string1):
    bit_list = []
    for c in string1:
        bits = bin(c)[2:]
        bits = '00000000'[len(bits):] + bits
        bit_list.extend([int(b) for b in bits])
    return bit_list


def bits_str(bits):
    chars = []
    for b in range(int(len(bits) / 8)):
        byte = bits[b*8:(b+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)


def encoder(text, image):

    # load our original jpg image
    image_file = Image.open(image)
    image_pix = image_file.load()
    # load our future image
    new_image = Image.new(image_file.mode, image_file.size)
    new_image_pix = new_image.load()

    # open our text file, get a size, and a convert the text and size to bits
    text_file = open(text, "r")
    text_file = text_file.read()
    text_file = text_file.encode()
    text_file_bits = str_bits(text_file)

    # get width, height, num rows, num columns, and number of pixels
    width, height = image_file.size
    num_pix = width * height
    row = height - 1
    column = width - 1

    if len(text_file) > ((num_pix - 11) * 3):
        raise ValueError("Error - Text bigger than image")

    num_loops = bin(int(math.ceil(len(text_file_bits) / 3 + 1)))
    # num_loops = 1b11111
    num_loops = num_loops[2:]
    # num_loops = 11111

    i = len(num_loops) - 1
    # i = 4
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
    # need to first access the last 11 bits of the image
    #  editing 3 rbg values before moving on to next pixel

    index = 0
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


def decoder(image):
    image_file = Image.open(image)
    image_file_pix = image_file.load()

    width, height = image_file.size
    row = height - 1
    column = width - 1

    size_of_text = ''
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
    for i in range(row, -1, -1):
        if count == index:
            break
        for j in range(column, -1, -1):
            if count2 == index2:
                break
            if i == row and j >= column - 11:
                continue
            text.append(red & 0b1)
            text.append(green & 0b1)
            text.append(blue & 0b1)

            index += 1
            index2 += 1
    return_text = bits_str(text)

    return return_text

command = ' '

if len(sys.argv) == 4:
    command = sys.argv[1]

if len(sys.argv) == 3:
    command = sys.argv[1]

encoder("text.txt", "gorvachev.jpg")

if command == "encode":
    if not sys.argv[3].endswith(".jpeg") and not sys.argv[3].endswith("jpg"):
        print("Sorry your image file needs to be a jpeg or jpg file")
        exit()
    encoder(sys.argv[2], sys.argv[3]).save('output.png')
elif command == "decode":
    if not sys.argv[2].endswith(".png"):
        print("Sorry your file needs to be a png file")
        exit()
    print(decoder(sys.argv[2]))
else:
    print("Invalid Entry: Try one of two")
    print("main.py encode \"example text\" \"example image/jpg\"")
    print("main.py decode \"example image/jpg\"")