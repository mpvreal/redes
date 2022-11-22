import sys
import locale

from select import select
from socket import *
from time import time_ns

# Formatação em pt_BR
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
# Tamanho da mensagem
SIZE = 500
# Mensagem
MESSAGE = b'teste de rede *2022*' * 25
# Número de pings
ATTEMPTS = 20

def error():
    print(f'Formato de utilização:\n\t{sys.argv[0]} <ip> <porta> \
<protocolo>\n\tPara iniciar listening, insira \"listen\" em <ip>')
    exit(1)

def download(speedtest):
    counter = 0
    avg_transfer_rate = 0

    ready = select([speedtest], [], [], 3)[0]
    while ready:
        start = time_ns()
        if not speedtest.recv(SIZE):
            break
        elapsed = time_ns() - start
        counter += 1

        ping = elapsed / 1000000
        transfer_rate = (SIZE * 8 / elapsed) * 1000000000
        avg_transfer_rate += transfer_rate
        
        print(locale.format_string('%.2f', ping, True) + \
            ' ms\t\t' + \
            locale.format_string('%.2f', transfer_rate, True) \
            + ' bits/s')
        
        ready = select([speedtest], [], [], 3)[0]

    try:
        avg_transfer_rate /= counter
    except ZeroDivisionError:
        print(f'Erro: Nenhum pacote recebido.\nAbortando.')
        exit(1)

    print(f'Pacotes recebidos: {counter}')

    return avg_transfer_rate

def upload_tcp(speedtest):
    counter = 0
    avg_transfer_rate = 0
    sent = 0

    for _ in range(ATTEMPTS):
        start = time_ns()
        speedtest.sendall(MESSAGE)
        elapsed = time_ns() - start
        counter += 1

        ping = elapsed / 1000000
        transfer_rate = SIZE * 8 * 1000000000 / elapsed
        avg_transfer_rate += transfer_rate
        
        print(locale.format_string('%.2f', ping, True) + \
            ' ms\t\t' + \
            locale.format_string('%.2f', transfer_rate, True) \
            + ' bits/s')

    try:
        avg_transfer_rate /= counter
    except ZeroDivisionError:
        print(f'Erro: Nenhum pacote recebido.\nAbortando.')
        exit(1)

    print(f'Pacotes enviados: {counter}')

    return avg_transfer_rate

def upload_udp(speedtest, peer):
    counter = 0
    avg_transfer_rate = 0

    for _ in range(ATTEMPTS):
        start = time_ns()
        speedtest.sendto(MESSAGE, peer)
        elapsed = time_ns() - start
        counter += 1

        ping = elapsed / 1000000
        transfer_rate = SIZE * 8 * 1000000000 / elapsed
        avg_transfer_rate += transfer_rate
        
        print(locale.format_string('%.2f', ping, True) + \
            ' ms\t\t' + \
            locale.format_string('%.2f', transfer_rate, True) \
            + ' bits/s')

    try:
        avg_transfer_rate /= counter
    except ZeroDivisionError:
        print(f'Erro: Nenhum pacote recebido.\nAbortando.')
        exit(1)

    print(f'Pacotes enviados: {counter}')

    return avg_transfer_rate

# Parâmetros corretos
if(len(sys.argv) < 3):
    error()

elif(sys.argv[3] == 'tcp'):
    speedtest = socket(AF_INET, SOCK_STREAM)
    speedtest.settimeout(5)

    if(sys.argv[1] == 'listen'):
        speedtest.bind((gethostbyname(gethostname()), 
            int(sys.argv[2])))
        
        try:
            speedtest.listen(1)
            print('Aguardando conexão...')
            speedtest, address = speedtest.accept()
        except:
            print(f'Erro: Tempo limite de conexão excedido.\nAbortando.')
            exit(1)

        print(f'Conexão aceita de {address[0]}:{address[1]}')

        print('Iniciando teste de download...')
        speed = download(speedtest)
        print(f'Download médio: \t\t' + \
            locale.format_string('%.2f', speed, True) + ' bits/s')

        speedtest.sendall(b'OK')
        
        print('Iniciando teste de upload...')
        speed = upload_tcp(speedtest)
        print(f'Upload médio: \t\t' + \
            locale.format_string('%.2f', speed, True) + ' bits/s')

    else:
        speedtest.connect((sys.argv[1], int(sys.argv[2])))
        print(f'Conectado a {sys.argv[1]}:{sys.argv[2]}')

        print('Iniciando teste de upload...')
        speed = upload_tcp(speedtest)
        print(f'Upload médio: \t\t' + \
            locale.format_string('%.2f', speed, True) + ' bits/s')

        try:
            speedtest.recv(2)
        except TimeoutError:
            print(f'Erro: Nenhum pacote recebido.\nAbortando...')
            exit(1)

        print('Iniciando teste de download...')
        speed = download(speedtest)
        print(f'Download médio: \t\t' + \
            locale.format_string('%.2f', speed, True) + ' bits/s')

elif(sys.argv[3] == 'udp'):
    speedtest = socket(AF_INET, SOCK_DGRAM)
    speedtest.settimeout(5)

    if(sys.argv[1] == 'listen'):
        speedtest.bind((gethostbyname(gethostname()), 
            int(sys.argv[2])))
        print(f'Aguardando em {gethostbyname(gethostname())}:{sys.argv[2]}...')   
        try:
            peer = speedtest.recvfrom(3)[1]
        except TimeoutError:
            print(f'Erro: Limite de tempo excedido.\nAbortando.')
            exit(1)
    
        print('Iniciando teste de download...')
        speed = download(speedtest)
        print(f'Download médio: \t\t' + \
            locale.format_string('%.2f', speed, True) + ' bits/s')

        speedtest.sendto(b'OK', peer)
        
        print('Iniciando teste de upload...')
        speed = upload_udp(speedtest, peer)
        print(f'Upload médio: \t\t' + \
            locale.format_string('%.2f', speed, True) + ' bits/s')
        
    else:
        speedtest.connect((sys.argv[1], int(sys.argv[2])))
        print(f'Conectado a {sys.argv[1]}:{sys.argv[2]}')
        speedtest.sendall(b'OK')

        print('Iniciando teste de upload...')
        speed = upload_udp(speedtest, (sys.argv[1], int(sys.argv[2])))
        print(f'Upload médio: \t\t' + \
            locale.format_string('%.2f', speed, True) + ' bits/s')

        try:
            speedtest.recv(2)
        except TimeoutError:
            print(f'Erro: Nenhum pacote recebido.\nAbortando...')
            exit(1)

        print('Iniciando teste de download...')
        speed = download(speedtest)
        print(f'Download médio: \t\t' + \
            locale.format_string('%.2f', speed, True) + ' bits/s')
else:
    error()
# elif(sys.argv[1] == 'listen'):

#     ip = socket.gethostbyname(socket.gethostname())
#     port = int(sys.argv[2])
#     file = open(sys.argv[3], 'wb')
#     size = int(sys.argv[4]) + struct.calcsize(HEADER)
    
#     # Inicializa socket e inicia listening TCP
#     server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     server.bind((ip, port))
#     server.listen(5)
#     print(f'Ouvindo em {ip}:{port}')

#     # Accept na tentativa de conexão do cliente
#     client, addr = server.accept()
#     print('Conexao aceita de: %s:%d' %(addr[0], addr[1]))

#     avg_transf_rate = 0

#     while True:
#         packet = b''
#         # Se não completou o recebimento do pacote, continua 
#         # tentando receber
#         while(len(packet) < size):
#             buffer = client.recv(size - len(packet))
#             if(len(buffer) == 0):
#                 break
#             packet += buffer
#         # Se não recebeu nada, encerra a conexão
#         if(len(packet) == 0):
#             break
#         # Tamanho da seção de dados
#         data_size = len(packet) - struct.calcsize(HEADER)
#         id, sent_time, data = \
#             struct.unpack(f'{HEADER}{data_size}s', packet)
#         # Calcula a taxa de transferência
#         ping = (time_ns() - sent_time) / 1000000
#         transfer_rate = len(packet) * 8 / (ping / 1000)
#         avg_transf_rate += transfer_rate
#         counter += 1

#         print(f'Pacote {id}\t\t' + \
#             locale.format_string('%.2f', ping, True) + ' ms\t' + \
#                 locale.format_string('%.2f', transfer_rate, True) \
#                     + ' bits/s')

#         file.write(data)

#     avg_transf_rate /= counter

#     print(f'\nNúmero de pacotes recebidos: {counter}' + \
#         f'\nNúmero de pacotes perdidos: {id - counter}' + \
#         f'\nVelocidade de transferência média\t' + \
#         locale.format_string('%.2f', avg_transf_rate, True) + \
#         ' bits/s')

#     client.close()

# else:
#     # Recebe IP e porta a partir da linha de comando
#     ip = sys.argv[1]
#     port = int(sys.argv[2])
#     file = open(sys.argv[3], 'rb')
#     size = int(sys.argv[4])

#     # Tenta conexão com o endereço do servidor
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client.connect((ip, port))

#     # Envio das mensagens
#     while True:
#         data = file.read(size)
#         data_size = len(data)

#         if(data_size < 1):
#             break
#         else:
#             counter += 1

#         print(f'Pacote enviado nº {counter}')

#         packet = struct.pack(f'{HEADER}{data_size}s', \
#             counter, time_ns(), data)
#         client.send(packet)

#     print(f'Envio finalizado.\nNúmero de pacotes enviados: {counter}')

#     client.close()