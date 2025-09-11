import os
import base64
import requests
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

GITHUB_TOKEN = 'YOUR TOKEN'  # https://github.com/settings/tokens
OWNER = 'YOUR GITHUB USERNAME'
REPO = 'YOUR REPO NAME'
BRANCH = 'main'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return "No files were uploaded.", 400

    # Get mime extension
    filename = file.filename
    mime_type = file.mimetype
    extension = filename.split('.')[-1] if '.' in filename else 'bin'
    unique_name = f"{int(round(os.times()[4]*1000))}.{extension}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(file_path)

    # Read and encode file
    with open(file_path, 'rb') as f:
        content = base64.b64encode(f.read()).decode()

    github_path = f"uploads/{unique_name}"
    api_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{github_path}"
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'message': f'Upload file {unique_name}',
        'content': content,
        'branch': BRANCH
    }

    try:
        resp = requests.put(api_url, json=data, headers=headers)
        resp.raise_for_status()
        raw_url = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}/{github_path}"
        return render_template('result.html', raw_url=raw_url, file_name=unique_name)
    except Exception as e:
        print(e)
        return "Error uploading file.", 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)