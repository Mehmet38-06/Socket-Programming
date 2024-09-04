


from flask import Flask, render_template, request, jsonify
import subprocess
import pymysql
import socket
import json
import os

app = Flask(__name__)
process = None  # Global process değişkeni

# JSON dosya yolu
JSON_FILE_PATH = 'path_to_your_folder'

# SQL veritabanı bağlantısını test eden fonksiyon
def test_sql_connection():
    try:
        connection = pymysql.connect(host='Host IP', user='sql_server_name', password='sql_server_password', database='database_name')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return "SQL Bağlantısı Başarılı"
        finally:
            connection.close()
    except Exception as e:
        return f"SQL Bağlantısı Başarısız: {str(e)}"

# Client kodunu çalıştıran fonksiyon ve mesaj gönderme/alma kontrolü
def start_client():
    global process
    try:
        process = subprocess.Popen(['python3', 'path_to_your_client_code'])
        
        # İlk mesaj gönderilip alınıyor mu test ediyoruz
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 5000)  # Sunucu IP ve port bilgileri
        sock.connect(server_address)
        try:
            message = 'Test Message'
            sock.sendall(message.encode())
            data = sock.recv(1024)
            print('Received:', data.decode())
            if data:
                return True  # Bağlantı ve mesajlaşma başarılı
        finally:
            sock.close()
        
        return False  # Bağlantı ya da mesajlaşma başarısız
        
    except Exception as e:
        print(f"Error: {e}")
        return False

# Client işlemini durduran fonksiyon
def stop_client():
    global process
    if process:
        process.terminate()  # Process'i durdur
        process.wait()       # İşlemin tamamen durmasını bekle
        process = None
        return "Client Durduruldu"
    return "Client Zaten Çalışmıyor"

# SQL veritabanındaki son verileri getiren fonksiyon
def get_latest_logs():
    try:
        connection = pymysql.connect(host='Host IP', user='sql_server_name', password='sql_server_password', database='database_name')
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 20")
            logs = cursor.fetchall()
        return logs
    except Exception as e:
        return f"SQL Bağlantısı Başarısız: {str(e)}"

# JSON dosyasını güncelleyen fonksiyon
def update_json_file(ip, tcp_port, udp_port):
    # Eğer dosya mevcut değilse, boş bir JSON dizisi oluştur
    if not os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump([], file)

    with open(JSON_FILE_PATH, 'r+') as file:
        data = json.load(file)

        # Aynı IP adresini kontrol etme
        for server in data:
            if server['host'] == ip:
                server['tcp_port'] = tcp_port
                server['udp_port'] = udp_port
                break
        else:
            # Yeni sunucu ekle
            data.append({
                "host": ip,
                "tcp_port": tcp_port,
                "udp_port": udp_port
            })

        # JSON dosyasını güncelle
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()

# Ana sayfa rotası
@app.route('/')
def index():
    return render_template('index.html', status=None, sql_status=None, logs=[])

# Client başlatma rotası
@app.route('/start_client', methods=['POST'])
def start_client_route():
    status = start_client()
    color = 'green' if status else 'red'
    return jsonify({"status": status, "color": color})

# Client durdurma rotası
@app.route('/stop_client', methods=['POST'])
def stop_client_route():
    stop_status = stop_client()
    return jsonify({"stop_status": stop_status})

# SQL bağlantı testi rotası
@app.route('/test_sql', methods=['POST'])
def test_sql_route():
    sql_status = test_sql_connection()
    return jsonify({"sql_status": sql_status})

# Logs sayfası rotası
@app.route('/logs', methods=['GET'])
def logs_route():
    logs = get_latest_logs()
    return render_template('logs.html', logs=logs)

# Sunucu adresi girme rotası
@app.route('/save-server', methods=['POST'])
def save_server():
    data = request.json
    ip = data['ip']
    tcp_port = data.get('tcp_port')
    udp_port = data.get('udp_port')

    # JSON dosyasını güncelleme
    update_json_file(ip, tcp_port, udp_port)

    return jsonify({"message": "Sunucu bilgileri kaydedildi."}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=5001, debug=True)


