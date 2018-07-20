# Simple example of reading the MCP3008 analog input channels and printing
# them all out.
# Author: Tony DiCola
# License: Public Domain
import time
import warnings
import csv
import signal
import sys
import os

# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


# Software SPI configuration:
# CLK  = 18
# MISO = 23
# MOSI = 24
# CS   = 25
# mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 1
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

#Calibration Results 
air = 778 #FIXME
water = 375 #FIXME

# Main program loop.
if __name__ == '__main__':
    data = []
    data.append(['Timestamp', 'Relative Humidity (%)'])
    # Output CSV file at folder named "outputs" under current directory of the python file
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(path,"humidityData")
    if not os.path.isdir(path):
        os.makedirs(path)
    # Output Timestamp as file name
    name = time.strftime("%m-%d-%Y_%H:%M:%S.csv")
    filename = os.path.join(path,name)
        
    while True:
        try:
            # Read all the ADC channel values in a list.
            values = [0]*8
            for i in range(8):
                # The read_adc function will get the value of the specified channel (0-7).
                values[i] = mcp.read_adc(i)
            now = time.strftime("%m/%d/%Y %H:%M:%S")

            # Calculate relative humidity & save data to csv file
            relHum = round(float((air - values[0]))/float((air - water))*100, 1)
                # sanitize outputs
            if relHum < 0:
                relHum = 0.0
            if relHum > 100:
                relHum = 100.0
            data.append([now, relHum])
            print('Relative Humidity: '+ str(relHum) + '%')
            # Print the ADC values.       
            print(values[0])
            # Pause for half a second.
            time.sleep(2)
            
            with open(filename,'w+') as f:
                writer = csv.writer(f)
                writer.writerows(data)
                f.close()
            
        except KeyboardInterrupt:
            print('Sampling is stopped by the user')
            sys.exit(0)

