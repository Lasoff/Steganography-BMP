import tkinter as tk
from tkinter.ttk import Notebook, Combobox
import os
import sys


def encode():
    # Get value and files names
    degree = int(cmb_degree.get())
    message_file = ent_mess.get()
    original_file = ent_inbmp.get()
    encoded_file = ent_outbmp.get()

    # Verify message and bitmap length
    text_len = os.stat(message_file).st_size
    bmp_len = os.stat(original_file).st_size
    if text_len >= (bmp_len * degree / 8) - 54:
        lbl_status_enc.config(text='Encoding text is to long for this bitmap')
        return

    # Creating a binary masks for encoding
    text_mask = (0b11111111 << (8 - degree)) % 256
    bmp_mask = (0b11111111 << degree) % 256

    # Open files
    with open(message_file, 'r') as text, open(original_file, 'rb') as in_bmp, open(encoded_file, 'wb') as out_bmp:

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
        lbl_status_enc.config(text=f'Text message length is {text_len} symbols\nMessage encoded successfully')


def decode():
    # Get value and files names
    degree = int(cmb_degree2.get())
    text_len = int(ent_lenght.get())
    encoded_file = ent_encbmp.get()
    decoded_file = ent_dectxt.get()

    # Verify message and bitmap length
    bmp_len = os.stat(encoded_file).st_size
    if text_len >= (bmp_len * degree / 8) - 54:
        lbl_status_dec.config(text='Encoded message is to long for this bitmap')
        return

    # Open files
    with open(decoded_file, 'w') as text, open(encoded_file, 'rb') as in_bmp:

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
        lbl_status_dec.config(text="Message decoded successfully")


# GUI, create window
window = tk.Tk()
window.geometry('480x380')
window.resizable(False, False)
window.title('Steganography-BMP')

lbl_main = tk.Label(window, text='Please choose what you want. \n Encode a message to a bitmap file or Decode a message from a bitmap file.')
lbl_main.pack(pady=10)

# GUI, create tabs
tab = Notebook(window)

tab1 = tk.Frame(tab)
tab.add(tab1, text="Encode")
tab.pack(expand=1, fill='both')

tab2 = tk.Frame(tab)
tab.add(tab2, text="Decode")
tab.pack(expand=1, fill='both')

# GUI, tab - Encode
lbl_degree = tk.Label(tab1, text='Select the number of bits to replace in a byte:')
lbl_degree.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)

cmb_degree = Combobox(tab1, state="readonly")
cmb_degree['values'] = (1, 2, 4, 8)
cmb_degree.current(0)
cmb_degree.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)

lbl_mess = tk.Label(tab1, text='A file with a text message to be encoded:')
lbl_mess.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)

ent_mess = tk.Entry(tab1, width=30)
ent_mess.insert(0, 'message.txt')
ent_mess.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)

lbl_inbmp = tk.Label(tab1, text='Source bitmap file:')
lbl_inbmp.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)

ent_inbmp = tk.Entry(tab1, width=30)
ent_inbmp.insert(0, 'original.bmp')
ent_inbmp.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)

lbl_outbmp = tk.Label(tab1, text='Bitmap file to save the encoded message:')
lbl_outbmp.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)

ent_outbmp = tk.Entry(tab1, width=30)
ent_outbmp.insert(0, 'encoded.bmp')
ent_outbmp.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)

btn_enc = tk.Button(tab1, text='Encode', command=encode, width=20)
btn_enc.grid(row=4, column=0, columnspan=2, pady=10)

lbl_status_enc = tk.Label(tab1, text='Status:', bd=2, relief=tk.SUNKEN)
lbl_status_enc.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)

# GUI, tab - Decode
lbl_degree2 = tk.Label(tab2, text='Select the number of bits replaced in a byte:')
lbl_degree2.grid(row=0, column=0, sticky=tk.N, padx=10, pady=10)

cmb_degree2 = Combobox(tab2, state="readonly")
cmb_degree2['values'] = (1, 2, 4, 8)
cmb_degree2.current(0)
cmb_degree2.grid(row=0, column=1, sticky=tk.W, padx=10, pady=10)

lbl_lenght = tk.Label(tab2, text='Enter the length of the encoded message:')
lbl_lenght.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)

ent_lenght = tk.Entry(tab2, width=30)
ent_lenght.insert(0, '0')
ent_lenght.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)

lbl_encbmp = tk.Label(tab2, text='Encoded bitmap file:')
lbl_encbmp.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)

ent_encbmp = tk.Entry(tab2, width=30)
ent_encbmp.insert(0, 'encoded.bmp')
ent_encbmp.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)

lbl_dectxt = tk.Label(tab2, text='File to save the decoded text message:')
lbl_dectxt.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)

ent_dectxt = tk.Entry(tab2, width=30)
ent_dectxt.insert(0, 'decoded.txt')
ent_dectxt.grid(row=3, column=1, sticky=tk.W, padx=10, pady=10)

btn_dec = tk.Button(tab2, text='Decode', command=decode, width=20)
btn_dec.grid(row=4, column=0, columnspan=2, pady=10)

lbl_status_dec = tk.Label(tab2, text='Status:', bd=2, relief=tk.SUNKEN)
lbl_status_dec.grid(row=5, column=0, columnspan=2, sticky=tk.NSEW, padx=10, pady=10)

window.mainloop()
