import socket
import struct

# ASCII matrix and UTF-8 table from question 5
ascii_matrix = [
    [
        "NUL",
        "SOH",
        "STX",
        "ETX",
        "EOT",
        "ENO",
        "ACK",
        "BEL",
        "BS",
        "TAB",
        "LF",
        "VT",
        "FF",
        "CR",
        "SO",
        "SI",
    ],
    [
        "DLE",
        "DC1",
        "DC2",
        "DC3",
        "DC4",
        "NAK",
        "SYN",
        "ETB",
        "CAN",
        "EM",
        "SUB",
        "ESC",
        "FS",
        "GS",
        "RS",
        "US",
    ],
    [" ", "!", '"', "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/"],
    ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":", ";", "<", "=", ">", "?"],
    ["@", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O"],
    ["P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "[", "\\", "]", "^", "_"],
    ["`", "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o"],
    ["p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "{", "|", "}", "~", "DEL"],
]

utf8_table = [
    {"bytes": 1, "bits": 7, "first": "U+0000", "last": "U+007F"},
    {"bytes": 2, "bits": 11, "first": "U+0080", "last": "U+07FF"},
    {"bytes": 3, "bits": 16, "first": "U+0800", "last": "U+FFFF"},
    {"bytes": 4, "bits": 21, "first": "U+10000", "last": "U+10FFFF"},
]


def convert_hex(hex_value):
    return str(int(hex_value, 16))


def convert_bin(binary):
    return str(bin(int(binary)))


def operacao_binaria(bin1, bin2, operacao):
    def binario_para_decimal(binario):
        if binario[0] == "1":
            return -(256 - int(binario, 2))
        return int(binario, 2)

    def decimal_para_binario(decimal):
        if decimal < 0:
            return format(256 + decimal, "08b")
        return format(decimal, "08b")

    dec1 = binario_para_decimal(bin1)
    dec2 = binario_para_decimal(bin2)

    if operacao == "+":
        resultado_dec = dec1 + dec2
    elif operacao == "-":
        resultado_dec = dec1 - dec2
    else:
        return "Operação inválida. Use '+' para soma ou '-' para subtração."

    if resultado_dec > 127 or resultado_dec < -128:
        return "Aviso: Ocorreu overflow!"

    return decimal_para_binario(resultado_dec % 256)


def binary_division(dividendo, divisor):
    def binary_to_decimal(binary):
        if binary[0] == "1":
            inverted = "".join("1" if bit == "0" else "0" for bit in binary)
            return -(int(inverted, 2) + 1)
        return int(binary, 2)

    def decimal_to_binary(decimal):
        if decimal < 0:
            positive = bin(abs(decimal))[2:].zfill(8)
            inverted = "".join("1" if bit == "0" else "0" for bit in positive)
            return bin(int(inverted, 2) + 1)[2:].zfill(8)
        return bin(decimal)[2:].zfill(8)

    dec_dividendo = binary_to_decimal(dividendo)
    dec_divisor = binary_to_decimal(divisor)

    if dec_divisor != 0:
        quociente = dec_dividendo // dec_divisor
        resultado_binario = decimal_to_binary(quociente)
        return f"Quociente: {resultado_binario} ({quociente})"
    else:
        return "Erro: Divisão por zero"


def float_to_ieee754(num):
    pacote = struct.pack(">f", float(num))
    variavel = struct.unpack(">I", pacote)[0]
    binario = format(variavel, "032b")
    sinal = binario[0]
    expoente = binario[1:9]
    mantissa = binario[9:]
    return f"sinal: {sinal}\nexpoente: {expoente}\nmantissa: {mantissa}"


def find_char_position(char):
    for i, row in enumerate(ascii_matrix):
        if char in row:
            return i, row.index(char)
    return None


def char_to_hex(char):
    position = find_char_position(char)
    if position:
        row, col = position
        hex_value = row * 16 + col
        return f"{hex_value:02X}"
    return None


def word_to_hex(word):
    hex_values = []
    for char in word:
        hex_value = char_to_hex(char)
        if hex_value:
            hex_values.append(hex_value)
        else:
            hex_values.append("??")
    return " ".join(hex_values)


def process_request(data):
    parts = data.split("|")
    question = int(parts[0])

    if question == 1:
        if parts[1] == "hex":
            return convert_hex(parts[2])
        elif parts[1] == "bin":
            return convert_bin(parts[2])
    elif question == 2:
        return operacao_binaria(parts[1], parts[2], parts[3])
    elif question == 3:
        return binary_division(parts[1], parts[2])
    elif question == 4:
        return float_to_ieee754(parts[1])
    elif question == 5:
        if parts[1] == "ascii_to_hex":
            return word_to_hex(parts[2])
        elif parts[1] == "utf8_compare":
            phrase1, phrase2 = parts[2], parts[3]
            bytes1 = phrase1.encode("utf-8")
            bytes2 = phrase2.encode("utf-8")
            return f"Frase 1: {len(bytes1)} bytes, hex: {bytes1.hex()}\nFrase 2: {len(bytes2)} bytes, hex: {bytes2.hex()}\nDiferença: {len(bytes2) - len(bytes1)} bytes"
    else:
        return "Questão inválida"


def start_server():
    host = "127.0.0.1"
    port = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f"Servidor escutando em {host}:{port}")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"Conectado por {addr}")
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    response = process_request(data)
                    conn.sendall(response.encode())


if __name__ == "__main__":
    start_server()
