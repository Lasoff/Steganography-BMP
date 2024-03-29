import os
import sys


def encode():
    # Enter number replaced bits in byte
    while True:
        degree = int(input('Enter a degree of encoding (1, 2, 4, 8):\n'))
        if degree in (1, 2, 4, 8):
            break
        else:
            print('Wrong number')

    # Verify message and bitmap length
    text_len = os.stat('message.txt').st_size
    bmp_len = os.stat('original.bmp').st_size
    if text_len >= (bmp_len * degree / 8) - 54:
        print('Encoding text is to long for this bitmap')
        return
    print(f'Text message length is {text_len} symbols')

    # Creating a binary masks for encoding
    text_mask = (0b11111111 << (8 - degree)) % 256
    bmp_mask = (0b11111111 << degree) % 256

    # Open files
    with open('message.txt', 'r') as text, open('original.bmp', 'rb') as in_bmp, open('encoded.bmp', 'wb') as out_bmp:

        # Read BMP header (first 54 bytes)
        out_bmp.write(in_bmp.read(54))

        # Cycle for reading chars in message
        while True:
            symbol = text.read(1)
            if not symbol:
                break

            symbol = ord(symbol)

            # Cycle for encoding one Char with bits shift
            for byte in range(0, 8, degree):
                # Clear rewriting bits in BMP byte
                bmp_byte = int.from_bytes(in_bmp.read(1), sys.byteorder) & bmp_mask
                # Clear not required bits in Char and shift required bits
                text_byte = (symbol & text_mask) >> (8 - degree)
                # Add BMP and Char bits
                bmp_byte |= text_byte
                # Writing encoded BMP byte
                out_bmp.write(bmp_byte.to_bytes(1, sys.byteorder))
                # Shift Char bits
                symbol <<= degree

        # Writing remaining BMP bytes
        out_bmp.write(in_bmp.read())
        print("Message encoded successfully")


def decode():
    # Enter number replaced bits in byte and length of encoded message
    while True:
        degree = int(input('Enter a degree of encoding (1, 2, 4, 8):\n'))
        if degree in (1, 2, 4, 8):
            break
        else:
            print('Wrong number')
    text_len = int(input('Enter a length of encoded message:\n'))

    # Verify message and bitmap length
    bmp_len = os.stat('encoded.bmp').st_size
    if text_len >= (bmp_len * degree / 8) - 54:
        print('Encoded message is to long for this bitmap')
        return

    # Open files
    with open('decoded.txt', 'w') as text, open('encoded.bmp', 'rb') as in_bmp:

        # Creating a binary mask for decoding
        bmp_mask = (~(0b11111111 << degree)) % 256

        # Skip bitmap header
        in_bmp.seek(54)

        read_count = 0

        # Cycle for reading chars in bmp
        while read_count < text_len:
            symbol = 0

            # Cycle for reading bits for one char
            for bits_read in range(0, 8, degree):

                # Read one byte from bitmap and applying mask
                bmp_byte = int.from_bytes(in_bmp.read(1), sys.byteorder) & bmp_mask

                # Put bits into byte
                symbol <<= degree
                symbol |= bmp_byte

            read_count += 1

            # Write char byte in file
            text.write(chr(symbol))
        print("Message decoded successfully")


def main():
    while True:
        mode = input('Please select mode: 1 - Encode, 2 - Decode, 3 - Exit\n')
        if mode == '1':
            encode()
        elif mode == '2':
            decode()
        elif mode == '3':
            break
        else:
            print('Unknown command')


if __name__ == "__main__":
    main()
