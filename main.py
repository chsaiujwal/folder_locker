import PySimpleGUI as sg
import shutil
import zipfile
import secrets
import string
import base64
import time
import os, random, struct
from Crypto.Cipher import AES

global sze
sze=[16,24,32]

def pwdgen():
    length = 32               
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    all = lower + upper + num + symbols
    password = ''.join(secrets.choice(all) for i in range(length))
    return password

def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    if not out_filename:
        out_filename = in_filename + '.enc'
    iv = iv = os.urandom(16)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

sg.theme("DarkGreen")
layout = [
    [sg.Input(), sg.FileBrowse('FileBrowse', )],
    [sg.Input(), sg.FolderBrowse('FolderBrowse')],
    [sg.Text(key='-TXT-', text_color="Red")],
    [sg.Text('Password', size =(15, 1)), sg.Input("", key='-OUTPUT-'),sg.Button('Generate Password')],
    [sg.Checkbox('Delete File/Folder after Encryption', default=False, key="chk") ],
    [sg.Text(key='-TEXT-', text_color="Red")],
    [sg.Text(key='SUCCEESS', text_color="Green")],
    [sg.Button('Encrypt'),sg.Button('Decrypt') , sg.Cancel()],
]

window = sg.Window('Encrypt/Decrypt file/folder', layout,icon=r'C:\Users\chsai\Desktop\folder_locker\enc.ico')
while True:
    event, values = window.read()
    if event is None or event == 'Cancel':
        break
    if event=='Generate Password':
        pwd=pwdgen()
        window["-OUTPUT-"].update(pwd)
    if event == 'Encrypt' or event == 'Decrypt':
        if not values['FolderBrowse'] and not values['FileBrowse']:
            window['-TXT-'].update("Select file or folder")
            continue
        if  len(values['-OUTPUT-']) not in sze:
            window['-TEXT-'].update("password must be either 16, 24, or 32 bytes long")
            continue
        if values['FolderBrowse']:
            window['-TXT-'].update("")
        if values['FileBrowse']:
            window['-TXT-'].update("")
        if values["-OUTPUT-"]:
            window['-TXT-'].update("")
            window['-TEXT-'].update("")
        else:
            window['-TEXT-'].update("Enter password Dude")
            continue
    if event == 'Encrypt':
        passwd =  values["-OUTPUT-"]
        bufferSize  = 1024*1024
        if values['FileBrowse']:
            locn = values['FileBrowse']
            start_time = time.time()
            encrypt_file(key = passwd.encode("utf8"),in_filename=str(locn),out_filename=str(locn)+".aes", chunksize=bufferSize)
            if  values["chk"]:
                os.remove(locn)
            window['SUCCEESS'].update("File encrypted successfully. Make sure to remember/store your password.\nYOU CAN'T RECOVER YOUR FILES IF YOU LOOSE YOUR PASSWORD")
            print(time.time() - start_time, "seconds")
        else:
            locn = values['FolderBrowse']
            shutil.make_archive(locn, 'zip', locn)
            locno=locn+".zip"
            start_time = time.time()
            encrypt_file(key = passwd.encode("utf8"),in_filename=str(locno),out_filename=str(locno)+".aes", chunksize=bufferSize)
            os.remove(locno)
            if values["chk"]:
                shutil.rmtree(locn)
            window['SUCCEESS'].update("Folder encrypted successfully. Make sure to remember/store your password.\nYOU CAN'T RECOVER YOUR FILES IF YOU LOOSE YOUR PASSWORD")
            print(time.time() - start_time, "seconds")

    if event == 'Decrypt':
        passwd =  values["-OUTPUT-"]
        bufferSize  = 1024*1024
        if values['FileBrowse']:
            locn = values['FileBrowse']
            start_time = time.time()
            decrypt_file(passwd.encode("utf8"), in_filename=str(locn), out_filename=str(locn)[0:-4],chunksize=bufferSize)
            os.remove(locn)
            if str(locn).endswith(".zip.aes"):  
                nlocn=str(locn)[0:-4]
                with zipfile.ZipFile(nlocn, 'r') as zip_ref:
                    zip_ref.extractall(nlocn[0:-4])
                    window['SUCCEESS'].update("Folder decrypted successfully")
                os.remove(nlocn)
            else:
                window['SUCCEESS'].update("File decrypted successfully")
            print(time.time() - start_time, "seconds")
            

window.close()