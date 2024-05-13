from flask import Flask, request, jsonify
import subprocess
import re
from config import LEDGER_ADDRESS_B, PORT

app = Flask(__name__)

@app.route('/', methods=['POST'])
def process_request():
    data = request.get_json()

    required_fields = ['target', 'token', 'amount', 'channel']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    command = ['namadac', 'ibc-gen-shielded',
               '--output-folder-path', './data',
               '--target', data['target'],
               '--token', data['token'],
               '--amount', data['amount'],
               '--port-id', 'transfer',
               '--channel-id', data['channel'],
               '--node', LEDGER_ADDRESS_B]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        response_string = result.stdout.strip()

        path_pattern = r"to\s+(?P<path>[\w./]+)"

        match = re.search(path_pattern, response_string)

        if match:
            path = match.group("path")
            full_path = f"./{path}"
            with open(full_path, 'r') as file:
                data = file.read()
                
            return data, 200
        else:
            return jsonify({'error': 'Path not found in response'}), 500

    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
