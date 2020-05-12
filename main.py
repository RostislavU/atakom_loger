import sys
import serial
import glob

from datetime import datetime

CMD_START = b'\x20\x20'
CMD_GET_DATA = b'\x20'
TIMEOUT = 1.5

TWO_CHANNELS = False


def serial_ports():
    if sys.platform.startswith('win'):
        s_ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        s_ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        s_ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in s_ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == '__main__':

    ser = serial.Serial(baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=TIMEOUT)
    ports = serial_ports()

    if ports:
        print('Доступные порты:')
        print(ports)
        if len(ports) > 1:
            ser.port = input('Введите адрес COM порта ')
        else:
            ser.port = ports[0]
            print('Работаем с портом ' + ser.port)
    else:
        print('\nНет доступных COM портов, проверьте подключние.\n')
        sys.exit()

    try:
        for i in range(10):
            try:
                ser.close()
                ser.open()
                if not ser.is_open:
                    ser.open()
                # knowledge mode
                ser.write(CMD_START)
                first_line = ser.readline().decode('utf-8')
                ser.write(CMD_GET_DATA)
                second_line = ser.readline().decode('utf-8')

                if first_line[2] != second_line[2]:
                    TWO_CHANNELS = True  # CH1 DC -0.0004 V\r\n CH2 DC -0.0005 A\r\n
                break
            except:
                continue

        file_name = datetime.now().strftime("%Y.%m.%d-%H-%M-%S")
        with open(file_name + '.csv', 'w') as f:

            while True:
                ser.write(CMD_GET_DATA)
                message = ser.readline().decode('utf-8')

                if TWO_CHANNELS:
                    if message.startswith('CH1'):
                        line = ';'.join(message[:-2].split(' '))
                        continue
                    line += ';' + ';'.join(message[:-2].split(' '))
                else:
                    line = ';'.join(message[:-2].split(' '))
                f.write(line + '\n')
    except:
        ser.close()
        sys.exit(-1)
