import PySimpleGUI as sg
import os
import pyAesCrypt
import shutil
import zipfile
import secrets
import string
import base64

def pwdgen():
    length = 32               
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    all = lower + upper + num + symbols
    password = ''.join(secrets.choice(all) for i in range(length))  
    return password

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
            pyAesCrypt.encryptFile(str(locn), str(locn)+".aes", passwd, bufferSize)
            if  values["chk"]:
                os.remove(locn)
            window['SUCCEESS'].update("File encrypted successfully")
        else:
            locn = values['FolderBrowse']
            shutil.make_archive(locn, 'zip', locn)
            locno=locn+".zip"
            pyAesCrypt.encryptFile(str(locno), str(locno)+".aes", passwd, bufferSize) 
            os.remove(locno)
            if values["chk"]:
                shutil.rmtree(locn)
            window['SUCCEESS'].update("Folder encrypted successfully")

    if event == 'Decrypt':
        passwd =  values["-OUTPUT-"]
        bufferSize  = 1024*1024
        if values['FileBrowse']:
            locn = values['FileBrowse']
            pyAesCrypt.decryptFile(str(locn), str(locn)[0:-4], passwd, bufferSize)
            os.remove(locn)
            if str(locn).endswith(".zip.aes"):  
                nlocn=str(locn)[0:-4]
                with zipfile.ZipFile(nlocn, 'r') as zip_ref:
                    zip_ref.extractall(nlocn[0:-4])
                    window['SUCCEESS'].update("Folder decrypted successfully")
                os.remove(nlocn)
            else:
                window['SUCCEESS'].update("File decrypted successfully")
            

window.close()


