from flask import Flask, render_template, jsonify
import os
import datetime
import socket

app = Flask(__name__)

@app.route('/')
def home():
    hostname = socket.gethostname()
    container_ip = socket.gethostbyname(hostname)
    container_id = hostname[:12]  # Docker 容器 ID 通常是 hostname 的前 12 碼
    flask_env = os.environ.get("FLASK_ENV", "未設定")
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template(
        "index.html",
        hostname=hostname,
        container_ip=container_ip,
        container_id=container_id,
        flask_env=flask_env,
        timestamp=timestamp
    )

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/info')
def info():
    return jsonify({
        'app_name': 'Flask Docker Demo',
        'python_version': os.sys.version,
        'container_id': os.uname().nodename[:12]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)