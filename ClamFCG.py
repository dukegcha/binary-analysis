# Copied/modified from https://www.pysimplegui.org/en/latest/ and https://opensource.com/article/18/8/pysimplegui

# In order to compile this program, you need:
#   Python 3 - tested with Python 3.11
#   pysimplegui - Use `pip install pysimplegui` to install it, tested with version 4.60.5
#   py2exe - Use `pip install py2exe` to install it, tested with version 0.13.0.1
#   ClamAV - Include the ClamAV folder in the dist folder and modify the clamscanPath variable if necessary
#   radare2 - Include the radare2 folder in the dist and modify the below radarePath variable if necessary

clamscanPath = ".\\clamav-1.2.1.win.x64\\clamscan.exe"
radarePath = ".\\radare2-5.8.8-w64\\bin\\radare2.exe"

import PySimpleGUI as sg
import subprocess
import threading

sg.theme('BluePurple')

layout = [
    [sg.Text('Select File', size=(15, 1), auto_size_text=False, justification='right'),
     sg.InputText('Select a file', key='fileinput'), sg.FileBrowse(file_types=(("Executable Files", "*.exe;*.dll"),))],
    [sg.Button('Scan File'), sg.Button('Show Disassembled Instructions'), sg.Button('Exit')],
#    [sg.one_line_progress_meter(title="test", current_value=0.2, max_value=1.0)], # causes a crash for some reason
    [sg.Multiline('', disabled=True, size=(105,15), key='outputbox', font=('Courier', 20), horizontal_scroll=True)]
]
window = sg.Window('ClamFCG', layout, resizable=True)

def run_clamav_scan(file_path):
    window['outputbox'].Update('Scanning...\n', append=True)
    result = subprocess.run([clamscanPath, file_path], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW) # Thanks to <https://stackoverflow.com/a/62226026> for creationflags=subprocess.CREATE_NO_WINDOW
    # In order to update a loading bar for scans with more than a few signatures, one may want to look into subprocess.Popen
    window['outputbox'].Update(result.stdout)

def run_radare_disassembly(file_path):
    window['outputbox'].Update('Disassembling...\n', append=True)
    result = subprocess.run([radarePath, "-c", "pd | ", file_path], capture_output=True, text=True, input='exit\n', creationflags=subprocess.CREATE_NO_WINDOW)
    lines = result.stdout.split('\n')[:-4]
    updated_output = '\n'.join(lines)
    window['outputbox'].Update(updated_output)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event == 'Scan File':
        window['outputbox'].Update('')
        file_path = values['fileinput'].replace("/", "\\")
        threading.Thread(target=run_clamav_scan, args=(file_path,)).start()

    if event == 'Show Disassembled Instructions':
        window['outputbox'].Update('')
        file_path = values['fileinput'].replace("/", "\\")
        threading.Thread(target=run_radare_disassembly, args=(file_path,)).start()

window.close()
