import spidev
import RPi.GPIO as GPIO
import warnings
import csv
import time
import signal
import sys
import os

#Default SPI Module
#
#SPI0: MOSI(GPIO 10) - Pin 19
#      MISO(GPIO 9)  - Pin 21
#      SCLK(GPIO 11) - Pin 23
#      CE0(GPIO 8)   - Pin 24
#      CE1(GPIO 7)   - Pin 26

#Alternative
#
#SPI1: MOSI(GPIO 20) - Pin 38
#      MISO(GPIO 19) - Pin 35
#      SCLK(GPIO 21) - Pin 40
#      CE0(GPIO 18)  - Pin 12
#      CE1(GPIO 17)  - Pin 11
#      CE2(GPIO 16)  - Pin 36

#Configure Chip Select pin
CS = 7

#Calibration Results 
air = 300 #FIXME
water = 100 #FIXME

#Reference Voltage
vref = 3.3

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) #Avoid warnings
GPIO.setup(CS,GPIO.OUT)
spi = spidev.SpiDev()

# Initialize SPI
def initSPI():
    #Pull up Chip selects
    GPIO.output(CS,1)

    #Open Default SPI bus
    spi.open(0,0) 
    spi.mode = 3
    spi.max_speed_hz = 5000000
    return 1

def closeSPI():
    spi.close()
    #Set chip selects low
    GPIO.output(CS,0)
    return 1    
    
if __name__ == '__main__':
    #initSPI()
    values = []
    values.append(['Timestamp','Voltage (V)', 'Relative Humidity (%)'])
    # Output CSV file at folder named "outputs" under current directory of the python file
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path,"outputs")
    if not os.path.isdir(path):
        os.makedirs(path)

    # Output Timestamp as file name
    name = time.strftime("%m-%d-%Y_%H:%M:%S.csv")
    filename = os.path.join(path,name)
    
    #Keep Sampling Data unless interrupted by user (Ctrl+C)
    while(True):
        try:
            GPIO.output(CS,0)
            rawBytes = spi.readbytes(1) # 16 Bit value from ADC
            print(rawBytes)
            GPIO.output(CS,1)
            result = int.from_bytes(rawBytes,byteorder = 'big')
            now = time.strftime("%m/%d/%Y %H:%M:%S")
            v = round(vref*(result / (2**16-1)),3)
            relHmd = 100*(result - air)/(water-air)
            values.append([now,v,relHmd])
            print([result,v])
            
            with open(filename,'w+',newline='') as f:
                writer = csv.writer(f)
                writer.writerows(values)
                f.close()

        except KeyboardInterrupt:
            print('Sampling is stopped by the user')
            closeSPI()
            sys.exit(0)
