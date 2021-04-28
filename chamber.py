# Temperature Chamber Control v0.9 - April 27, 2021
# by Joel Caturia <jcaturia@katratech.com>')

import serial
import time
import re
from datetime import datetime


###################################################################################################
### ADJUST BAUD AND COM PORT HERE ###
PORT = 'COM20'
BAUD = 115200

#flag_verbose = True   # for debugging, print lots of extra stuff to the screen
flag_verbose = False   # for debugging, print lots of extra stuff to the screen
###################################################################################################


# Sends a command out to the device, and does not wait or attempt to parse a response
def send_device(command):
    serial_port.write('{}\n'.format(command).encode())

    if flag_verbose:
        print('[SEND] -> [{}]'.format(command))


# Sends a command out to the device, and DOES wait for a response, as defined by the regex that we pass in
def query_device(command, response_regex):
    incoming_data = b''
    receive_buffer = b''
    
    if flag_verbose:
        print('[SEND] -> [{}]'.format(command))
    
    serial_port.write('{}\n'.format(command).encode())

    timeout_expired = False
    timeout_start = time.monotonic()
    timeout_end = timeout_start + 2 # number of seconds for the timeout

    while not timeout_expired:
        
        if time.monotonic() > timeout_end:
            timeout_expired = True

        if serial_port.in_waiting > 0:
            incoming_data = serial_port.read(serial_port.in_waiting)
            receive_buffer += incoming_data # Append to our buffer
            
            if flag_verbose:
                print('[RCV] -> [{}]'.format(receive_buffer))
            
            result = re.search(response_regex, receive_buffer)

            if result:
                break

    if timeout_expired:
        print('[ERR] Device Communication Timed Out')
        return False

    elif result:
        if flag_verbose:
            print('[MATCH] -> [{}]'.format(result.group(1).decode()))

        return result.group(1).decode()


# Set the setpoint temperature on the device
def set_temp(temperature):
    send_device('SETP {}'.format(temperature))

    # Check that our setpoint is actually what we want it set to
    response = read_set_point()
    count = 0

    while "{0:.1f}".format(float(response)) != "{0:.1f}".format(float(temperature)):
        response = read_set_point()
        time.sleep(0.1)
        count += 1
        if count > 10:
            print ('[ERROR] Error Setting Air Temp to: [{}]'.format(temperature))
            return False
    
    return True  
  

# Read the setpoint temperature from the device
def read_set_point():
    response = query_device('SETP?', re.compile(b'(([0-9]{1,3}(?:\.[0-9]){0,1}))\n'))

    if response:
        return response
    
    else:
        return False


# Read the air temperature from the device  
def read_air_temp():
    response = query_device('TEMP?', re.compile(b'(([0-9]{1,3}(?:\.[0-9]){0,1}))\n'))

    if response:
        return response
    
    else:
        return False


def wait_until_temp_reached(temp):

  limit = 0.25  # exit loop when within +/- this limit
  pv = float(read_air_temp())
  while not ((pv - limit) < float(temp) and float(temp) < (pv + limit)):
    pv = float(read_air_temp())
    print ("Set Point =", temp, "| Air Temp = {0:.1f}".format(pv), end = "\r")
    time.sleep(0.25)
  print ("\r")
  print ("Set Point Temp", temp, "Reached")
  return


def printtime () :
  timestamp = datetime.now().strftime('%H:%M:%S')
  print("timestamp =", timestamp)
  print ("\r")
  return


def rigo_temp(ossp, tpv, sp) :
  printtime()
  
  set_temp(ossp) # set temperature
  wait_until_temp_reached(tpv) # if chamber is not powered up it will hang here

  printtime()
  
  set_temp(sp) # set temperature
  wait_until_temp_reached(sp) # if chamber is not powered up it will hang here

  printtime()

  input("##########    Press Enter to Next Step...    ##########")  # only needed for demo code
  print ("\r")
  return

#==========================================================================================
#
# MAIN PROGRAM HERE
#
#==========================================================================================

if __name__ == '__main__':
    serial_port = serial.Serial(PORT, BAUD, timeout=0) 

    wait_until_temp_reached(90)

    #while True:
        #print(read_air_temp())
        #time.sleep(1)

    #myDelay = 2.0  # only used for this demonstration code so you can see that something is happening.  You don't need any delay in general except with certain commands.  

    #chamber_power("ON")
    #time.sleep(myDelay)


    #print ("Current Set Point =", read_set_point())
    #time.sleep(myDelay)

    #rigo_temp('-75.0', '-8.0', '-8.0')
    #rigo_temp(150, 15, 1.5)
    #rigo_temp(150, 14, 8)
    #rigo_temp(150, 18, 13)
    #rigo_temp(150, 27, 19)
    #rigo_temp(150, 32, 25)
    #rigo_temp(150, 39, 30)
    #rigo_temp(150, 46, 37)
    #rigo_temp(150, 58, 44)
    #rigo_temp(150, 64, 49)
    #rigo_temp(150, 71, 55)
    #rigo_temp(150, 75, 61)
    #rigo_temp(150, 80, 66)
    #rigo_temp(150, 85, 70)
    #rigo_temp(150, 91, 77)

    print("done")

    exit()
