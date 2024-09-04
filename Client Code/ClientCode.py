import socket
import threading
import time
import json
import requests

# Sunucu bilgilerini JSON dosyasından okuma
def load_servers(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Webhook ile SMS gönderme fonksiyonu
def send_sms_via_webhook(message):
    url = "http://**/webhook"  # Webhook sunucusunun IP adresi ve portu
    data = {
        "title": "Sunucuya erişilemedi.",
        "message": message
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("SMS başarıyla gönderildi!")
        else:
            print(f"SMS gönderilemedi: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Webhook isteği başarısız oldu: {e}")

def tcp_communication(server):
    if server['tcp_port'] == -1:
        print("TCP iletişimi kapalı.")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((server['host'], server['tcp_port']))
            print(f"Connected to TCP server at {server['host']}:{server['tcp_port']}.")
            while True:
                message = "PING"
                s.send(message.encode())
                response = s.recv(1024).decode()
                print(f"Received from TCP server {server['host']}:{server['tcp_port']}: {response}")
                time.sleep(5)  # 5 saniye bekleyip tekrar mesaj gönderir
        except Exception as e:
            print(f"TCP bağlantısı başarısız oldu: {e}")
            send_sms_via_webhook(f"TCP iletişimi {server['host']}:{server['tcp_port']} başarısız.")

def udp_communication(server):
    if server['udp_port'] == -1:
        print("UDP iletişimi kapalı.")
        return

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            print(f"Connected to UDP server at {server['host']}:{server['udp_port']}.")
            while True:
                message = "PING"
                s.sendto(message.encode(), (server['host'], server['udp_port']))
                response, _ = s.recvfrom(1024)
                print(f"Received from UDP server {server['host']}:{server['udp_port']}: {response.decode()}")
                time.sleep(5)  # 5 saniye bekleyip tekrar mesaj gönderir
        except Exception as e:
            print(f"UDP bağlantısı başarısız oldu: {e}")
            send_sms_via_webhook(f"UDP iletişimi {server['host']}:{server['udp_port']} başarısız.")

def tcp_udp_client(servers):
    for server in servers:
        if server['udp_port'] != -1:
            udp_thread = threading.Thread(target=udp_communication, args=(server,), daemon=True)
            udp_thread.start()

        if server['tcp_port'] != -1:
            tcp_communication(server)

def main():
    file_path = 'path_to_your_folder'  # JSON dosyasının konumu
    servers = load_servers(file_path)  # JSON dosyasından sunucu bilgilerini yükleme
    tcp_udp_client(servers)

if __name__ == '__main__':
    main()
