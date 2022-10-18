import locale
import select
import socket
import struct
import sys

from time import time_ns
# Cabeçalho do pacote
HEADER = 'QQ'
WINDOW_SIZE = int(sys.argv[5])
# Formatação em pt_BR
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

socket.setdefaulttimeout(5)
# Parâmetros corretos
if(len(sys.argv) < 5):
    print(f'Formato de utilização:\n\t{sys.argv[0]} <ip> <porta> \
<arquivo> <tamanho_packet> <tamanho_janela>\n\tPara iniciar listening, \
insira \"listen\" em [ip]')

elif sys.argv[1] == 'listen':
    ip = socket.gethostbyname(socket.gethostname())
    port = sys.argv[2]
    target = (ip, int(port))
    file = open(sys.argv[3], 'wb')
    size = int(sys.argv[4])

    print(f'Ouvindo em {ip}:{port}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(target)
    counter = 0
    avg_transf_rate = 0
    perdidos = 0

    while True:
        ready = select.select([sock], [], [], 3)[0]
        if ready:
            while True:
                packet, addr = \
                    sock.recvfrom(struct.calcsize(f'{HEADER}{size}s'))
                data_size = len(packet) - struct.calcsize(HEADER)
                index, sent_time, data = \
                    struct.unpack(f'{HEADER}{data_size}s', packet)
                if(len(packet) > 0):
                    counter += 1
                    file.write(data)
                    sock.sendto(b'ACK', addr)
                    break
                else:
                    perdidos += 1
            ping = (time_ns() - sent_time) / 1000000
            transfer_rate = len(packet) * 8 / (ping / 1000)
            print(f'Pacote {index}\t\t' + \
            locale.format_string('%.2f', ping, True) + ' ms\t\t' + \
                locale.format_string('%.2f', transfer_rate, True) \
                    + ' bits/s')
            avg_transf_rate += transfer_rate
        else:
            file.close()
            break

    avg_transf_rate /= counter
    print(f'\nNúmero de pacotes recebidos: {counter}' + \
        f'\nNúmero de pacotes perdidos: {perdidos}' + \
        f'\nVelocidade de transferência média\t\t' + \
        locale.format_string('%.2f', avg_transf_rate, True) + \
        ' bits/s')

    sock.close()

else:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ip = sys.argv[1]
    port = sys.argv[2]
    target = (ip, int(port))
    sock.connect(target)
    file = open(sys.argv[3], 'rb')
    size = int(sys.argv[4])
    counter = 0
    window = []
    packet = b''

    data = file.read(size * WINDOW_SIZE)
    while(data):
        sent_time = time_ns()
        for i in range(0, len(data), size):
            packet = struct.pack\
                (f'{HEADER}{len(data[i : i + size])}s', counter, \
                    sent_time, data[i : i + size])
            window.append(packet)
            counter += 1
        while True:
            try:
                for i in range(len(window)):
                    sock.sendto(window[i], target)
                    sock.recvfrom(100)
            except socket.timeout:
                continue
            else:
                data = file.read(size * WINDOW_SIZE)
                window.clear()
                break

    print(f'Envio finalizado.\nNúmero de pacotes enviados: {counter}')

    sock.close()