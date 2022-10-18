import socket
import sys
import struct
import locale

from time import time_ns
# Cabeçalho do pacote
HEADER = '>QQ'
# Tamanho do cabeçalho
counter = 0
# Formatação em pt_BR
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
# Parâmetros corretos
if(len(sys.argv) < 5):
    print(f'Formato de utilização:\n\t{sys.argv[0]} <ip> <porta> \
<arquivo> <tamanho_packet>\n\tPara iniciar listening, \
insira \"listen\" em [ip]')

elif(sys.argv[1] == 'listen'):

    ip = socket.gethostbyname(socket.gethostname())
    port = int(sys.argv[2])
    file = open(sys.argv[3], 'wb')
    size = int(sys.argv[4]) + struct.calcsize(HEADER)
    
    # Inicializa socket e inicia listening TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)
    print(f'Ouvindo em {ip}:{port}')

    # Accept na tentativa de conexão do cliente
    client, addr = server.accept()
    print('Conexao aceita de: %s:%d' %(addr[0], addr[1]))

    avg_transf_rate = 0

    while True:
        packet = b''
        # Se não completou o recebimento do pacote, continua 
        # tentando receber
        while(len(packet) < size):
            buffer = client.recv(size - len(packet))
            if(len(buffer) == 0):
                break
            packet += buffer
        # Se não recebeu nada, encerra a conexão
        if(len(packet) == 0):
            break
        # Tamanho da seção de dados
        data_size = len(packet) - struct.calcsize(HEADER)
        id, sent_time, data = \
            struct.unpack(f'{HEADER}{data_size}s', packet)
        # Calcula a taxa de transferência
        ping = (time_ns() - sent_time) / 1000000
        transfer_rate = len(packet) * 8 / (ping / 1000)
        avg_transf_rate += transfer_rate
        counter += 1

        print(f'Pacote {id}\t\t' + \
            locale.format_string('%.2f', ping, True) + ' ms\t' + \
                locale.format_string('%.2f', transfer_rate, True) \
                    + ' bits/s')

        file.write(data)

    avg_transf_rate /= counter

    print(f'\nNúmero de pacotes recebidos: {counter}' + \
        f'\nNúmero de pacotes perdidos: {id - counter}' + \
        f'\nVelocidade de transferência média\t' + \
        locale.format_string('%.2f', avg_transf_rate, True) + \
        ' bits/s')

    client.close()

else:
    # Recebe IP e porta a partir da linha de comando
    ip = sys.argv[1]
    port = int(sys.argv[2])
    file = open(sys.argv[3], 'rb')
    size = int(sys.argv[4])

    # Tenta conexão com o endereço do servidor
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, port))

    # Envio das mensagens
    while True:
        data = file.read(size)
        data_size = len(data)

        if(data_size < 1):
            break
        else:
            counter += 1

        print(f'Pacote enviado nº {counter}')

        packet = struct.pack(f'{HEADER}{data_size}s', \
            counter, time_ns(), data)
        client.send(packet)

    print(f'Envio finalizado.\nNúmero de pacotes enviados: {counter}')

    client.close()