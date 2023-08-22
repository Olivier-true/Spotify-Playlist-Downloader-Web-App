from flask import *
import subprocess, json
import time, os, zipfile
from threading import Thread
from sys import platform

global binary
binary = "python3"
if platform == "win32":
    binary += ".exe"

global output # https://github.com/spotDL/spotify-downloader
output = b''
global n
n = 1
global num
num = 1

def installFFMPEG():
    global binary
    # Install Dependency
    proc = subprocess.Popen([binary, "-m", "spotdl", "--download-ffmpeg"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    time.sleep(5)
    proc.stdin.write(b"y")
    proc.stdin.flush()

installFFMPEG()

def readStdout(process):
    global output
    global n
    global num
    while True:
        line = process.stdout.readline()
        if line.startswith(b"Found "):
            try:
                n = int(line.split(b" ")[1].decode())
                num = n
            except:
                a = 1
        if line.startswith(b"Downloaded ") or line.startswith(b"Skipping "):
            n -= 1
        if not line:
            break
        output += line
        time.sleep(0.05)
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    global output
    global binary
    if request.method == 'POST':
        url = json.loads(request.data.decode())["url"]
        # Execute bash command asynchronously
        
        output = b""
        process = subprocess.Popen([binary, '-m', 'spotdl', f'{url}', '--output', './download/'], stdout=subprocess.PIPE)
        Thread(target=readStdout, args=(process,)).start()
        return "OK"
    return """
    <!DOCTYPE html>
<html>
<head>
    <title>Command Output</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        .header {
            background-color: #ff0000;
            color: #ffffff;
            padding: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .search-container {
            position: relative;
        }
        .search-container input[type="text"] {
            width: 100%;
            padding: 12px 20px;
            margin: 8px 0;
            box-sizing: border-box;
            border: none;
            border-bottom: 2px solid #ff0000;
        }
        .search-container button[type="submit"] {
            background-color: #ff0000;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            position: absolute;
            right: 0;
            top: 25px;
        }
        .search-container button[type="submit"]:hover {
            background-color: #cc0000;
        }
        textarea#output {
            width: 100%;
            height: 500px;
            box-sizing:border-box; 
            resize:none; 
            border:none; 
            outline:none; 
        }
        .btn-download {
            background-color: #ff0000;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Command Output</h1>
    </div>

    <div class="container">
        <form id="form" method="POST" class="search-container">
            <label for="url">URL:</label><br>
            <input type="text" id="url" name="url"><br><br>
            <button type="submit">Submit</button>
        </form>

        <textarea id="output" readonly=true></textarea>
    </div>
    <br>
    <a class="btn-download" href="/download">Download All Audio in ZIP Archive Uniquement si la console a affichée : Fin du telechargement</a>
    <script>
        const form = document.getElementById('form');
        const output = document.getElementById('output');

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const url = document.getElementById('url').value;
            await fetch('/', {
                method: 'POST',
                body: JSON.stringify({ url }),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        });

        setInterval(async () => {
            const response = await fetch('/output');
            const text = await response.text();
            output.value = text;
        }, 3000);
    </script>
</body>
</html>


    """

@app.route('/output', methods=['GET'])
def output2():
    global output
    global n
    global num
    try:
        if n == 0:
            output += b"========= Fin du telechargement ========"
            n = -1
            num = -1
        return output
    except Exception as e:
        print(e)
        return ''

@app.route('/download')
def download():
    path = "./download/"
    if len(os.listdir(path)) == 0:
        if "download.zip" in os.listdir("."):
            print("send old zip")
            return send_file("download.zip", as_attachment=True)
        else:
            print("no zip found")
            return """<!DOCTYPE html>
            <html>
            <head>
            <style>
			.container {
            max-width: 100%;
            margin: 0 auto;
            padding: 0px;
			}
            a {
				font-size: 24pt;
                background-color: #ff0000;
                color: white;
				width: 100%;
				height: 70px;
                padding: 12px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            </style>
            <meta http-equiv="refresh" content="5; url=/" />
            </head>
            <body>
			<div class="container">
            <a href="/">Aucun Fichier a télécharger vous aller être rediriger vers la page convertion dans 5 secondes.</a>
            </div>
			</body>
            </html>
            """
    else:
        ziph = zipfile.ZipFile('download.zip', 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))
        os.system("rm ./download/*.mp3")
        return send_file("download.zip", as_attachment=True)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=81) # Set host='0.0.0.0' For access on another machine (replit or LAN)