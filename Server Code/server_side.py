import socket
import threading
import pymysql
from datetime import datetime

def save_message(protocol, sender_ip, receiver_ip, direction, status, duration, server_ip=None, server_port=None):
    connection = pymysql.connect(host='sql_server_Host_IP',
                                 user='sql_server_name',
                                 password='sql_server_password',
                                 database='sql_server_name')
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO messages (protocol, sender_ip, receiver_ip, direction, status, duration, server_port) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (protocol, sender_ip, receiver_ip, direction, status, duration, server_port))
            if server_ip and server_port:
                sql = "INSERT INTO server_logs (server_ip, server_port) VALUES (%s, %s)"
                cursor.execute(sql, (server_ip, server_port))

        connection.commit()
    finally:
        connection.close()

def handle_tcp_connection(conn, address, receiver_ip):
    server_ip, server_port = conn.getsockname()
    print(f"TCP Connection from {address} on {server_ip}:{server_port}")
    while True:
        start_time = datetime.now()
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Received from TCP client: {data}")
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            save_message('TCP', address[0], receiver_ip, 'received',  'TRUE', duration, server_ip, server_port)

            response = "PONG"
            start_time = datetime.now()
            conn.send(response.encode())
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            save_message('TCP', address[0], receiver_ip, 'sent', 'TRUE', duration, server_ip, server_port)
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            save_message('TCP', address[0], receiver_ip, 'sent', 'FALSE', duration, server_ip, server_port)
            print(f"Error sending message: {e}")
            break
    conn.close()

def handle_udp_connection(udp_socket, receiver_ip):
    server_ip, server_port = udp_socket.getsockname()
    while True:
        start_time = datetime.now()
        try:
            data, address = udp_socket.recvfrom(1024)
            print(f"Received from UDP client: {data.decode()} from {address} on {server_ip}:{server_port}")
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            save_message('UDP', address[0], receiver_ip, 'received', 'TRUE', duration, server_ip, server_port)

            response = "PONG"
            start_time = datetime.now()
            udp_socket.sendto(response.encode(), address)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            save_message('UDP', address[0], receiver_ip, 'sent', 'TRUE', duration, server_ip, server_port)
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            save_message('UDP', address[0], receiver_ip, 'sent', 'FALSE', duration, server_ip, server_port)
            print(f"Error sending message: {e}")

def start_tcp_server(host, port):
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((host, port))
    tcp_socket.listen(5)
    print(f"TCP Server running on {host}:{port}")

    while True:
        conn, address = tcp_socket.accept()
        threading.Thread(target=handle_tcp_connection, args=(conn, address, host)).start()

def start_udp_server(host, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((host, port))
    print(f"UDP Server running on {host}:{port}")

    handle_udp_connection(udp_socket, host)

def server_program():
    host = 'Host IP' 
    tcp_ports = [9000, 9001]  # TCP için birden fazla port ekleyebilirsiniz
    udp_ports = [8081, 8082]  # UDP için birden fazla port ekleyebilirsiniz

    for tcp_port in tcp_ports:
        threading.Thread(target=start_tcp_server, args=(host, tcp_port)).start()

    for udp_port in udp_ports:
        threading.Thread(target=start_udp_server, args=(host, udp_port)).start()

if __name__ == '__main__':
    server_program()