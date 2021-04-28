# Serial Device Emulator v0.9 - April 27, 2021
# by Joel Caturia <jcaturia@katratech.com>')

 
import serial
import re
import random


###################################################################################################
### ADJUST BAUD AND COM PORT HERE ###
PORT = 'COM21'
BAUD = 115200
###################################################################################################


def __MatchSetPointQuery(match):
    print('Received Command: {}, responded with: [{}]'.format('SET POINT QUERY', state_storage['setpoint_temperature']))
    __SendSerial('{}\n'.format(state_storage['setpoint_temperature']))


def __MatchSetPointValue(match):
    global state_storage

    value = match.group(2).decode()
    print('Received Command: {}, VALUE: [{}]'.format('SET POINT VALUE', value))
    state_storage['setpoint_temperature'] = value


def __MatchTempQuery(match):
    if state_storage['main_temperature'] is False:
        value = str(random.randint(-100, 225)) + '.0'

    else:
        value = state_storage['main_temperature']

    print('Received Command: {}, responded with: [{}]'.format('MAIN TEMPERATURE QUERY', value))
    __SendSerial('{}\n'.format(value))

    IncreaseTemp()


def __SendSerial(data):
    serial_port.write(data.encode())


# This function will do something with our temperature state.
# Since this emulator is virtual (and has no thermocouples), this is how we would simulate warming up, cooling down, etc.
def IncreaseTemp():
    global state_storage

    if state_storage['main_temperature'] is False:
        state_storage['main_temperature'] = 1
    
    else:
        state_storage['main_temperature'] += 1

    print('INFO: Temperature State Set to: [{}]'.format(state_storage['main_temperature']))



if __name__ == '__main__':

    print('\n----------------------------------------------------')
    print('Serial Device Emulator by JDC <jcaturia@katratech.com>')
    print('v0.9 - April 27, 2021\n')
    print('Running on COM port [{}] at baud rate: [{}]'.format(PORT, BAUD))
    print('----------------------------------------------------\n\n')

    serial_port = serial.Serial(PORT, BAUD, timeout=0)

    receive_buffer = b''

    state_storage = {}
    state_storage['setpoint_temperature'] = '0'
    state_storage['main_temperature'] = False

    _command_list = {}
    _command_list[re.compile(b'(SETP\?\n)')] = {'callback': __MatchSetPointQuery}
    _command_list[re.compile(b'(SETP ((?:-){0,1}[0-9]{1,3}(?:\.[0-9]){0,1}))\n')] = {'callback': __MatchSetPointValue}
    _command_list[re.compile(b'(TEMP\?\n)')] = {'callback': __MatchTempQuery}


    try:
        while True:

            if serial_port.in_waiting > 0:
                incoming_data = serial_port.read(serial_port.in_waiting)
                receive_buffer += incoming_data # Append to our buffer

                for regexString in _command_list:
                    while True:
                        result = re.search(regexString, receive_buffer)
                        
                        if result:
                            _command_list[regexString]['callback'](result)
                            receive_buffer = receive_buffer.replace(result.group(0), b'')
                        
                        else:
                            break

    except KeyboardInterrupt:
        print ('\n\nCTRL+C detected.. Exiting!!\n\n')
