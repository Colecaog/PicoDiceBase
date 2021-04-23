from machine import Pin, I2C
import utime
import random

#Pimoroni Tiny2040 RGB LED
ledBlue = Pin(20, Pin.OUT)
ledGreen = Pin(19, Pin.OUT)
ledRed = Pin(18, Pin.OUT)


#stores red animation frames
redFrames = [[0x20,0xF6,0x2F,0x7C,0xFD,0x7E,0x54,0x2E],
[0xA2,0x5E,0x3A,0x7C,0xFD,0x3E,0x7F,0x54],
[0x66,0xD5,0x3C,0xFA,0x76,0x7D,0x9E,0x52],
[0x91,0xDE,0xBF,0xFA,0xFF,0x5C,0xFD,0xA7],
[0x9B,0xBB,0x56,0xBD,0xFE,0xBE,0xF6,0x6B],
[0xC2,0xDA,0xFF,0x7E,0x7E,0xFD,0x7E,0x29],
[0x5A,0xAF,0xDA,0x6D,0xFE,0xEF,0x7E,0xA5],
[0xF6,0x7F,0x76,0xBF,0x6E,0x7B,0xDC,0x75]]

#stores green animation frames, mostly empty because red/orange are the primary
greenFrames = [[0x02,0x40,0x01,0x08,0x00,0x40,0x00,0x44],
[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
[0x05,0x40,0x04,0x10,0x00,0x24,0x00,0x82],
[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
[0x48,0x02,0x20,0x00,0x01,0x20,0x82,0x08],
[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00],
[0x50,0x00,0x08,0x00,0x01,0x80,0x08,0x20],
[0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]]

#stores orange animation frames
orangeFrames = [[0x00,0x24,0x58,0xBC,0x6E,0x5C,0x28,0x10],
[0x40,0x5C,0x79,0x56,0x3C,0x3A,0xEA,0x04],
[0x00,0x18,0x3C,0x72,0xB4,0x2D,0x12,0x0A],
[0x24,0x9E,0x3A,0x12,0x28,0x55,0x32,0x08],
[0x21,0x1A,0x8C,0x5A,0xF9,0x3A,0x7C,0x25],
[0x84,0x52,0x51,0x3C,0x5C,0x7D,0x99,0x92],
[0x96,0x21,0x6C,0x1B,0x7A,0x34,0x70,0x95],
[0x88,0x42,0x14,0x9A,0x39,0x24,0x58,0x02]]

#used for storing the full frame, 16 columns
fullFrame = [0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00, 0x00]

displayAddress = 1 #i2C address for display, no jumpers soldered
displayBrightness = 1 #initial brightness
displayEmpty = bytes([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]) #empty frame, all colors off, 16 columns
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000) #initial i2c definition, pins are 4 and 5 of Pimoroni Tiny2040

#clear out the full frame
def display_emptyFrame():
    global fullFrame
    for column, value in enumerate(fullFrame) :
        fullFrame[column] = 0

#write red data, red is odd frames
def display_writeRedFrame(rFrame):
    global fullFrame
    for column, value in enumerate(rFrame) :
        fullFrame[column*2+1] = value

#write green data, green is even columns
def display_writeGreenFrame(gFrame):
    global fullFrame
    for column, value in enumerate(gFrame) :
        fullFrame[column*2] = value

#write orange data to full frame, using or equals so it can set
#a bit if orange data is present but not clear a red or green if not
def display_writeOrangeFrame(oFrame):
    global fullFrame
    for column, value in enumerate(oFrame) :
        fullFrame[column*2+1] |= value
        fullFrame[column*2] |= value

def display_write(writeData):
    i2c.writeto(displayAddress, writeData)

#write data per column, could technically send faster by only sending column number first time
#as it auto increments column if you just send more data inside the same packet
def display_writeColumn(column, writeData):
    concat = bytes([column & 0xFF, writeData])
    i2c.writeto(displayAddress, concat)

#turns on oscillator, turns on display, sets initial brightness
def display_begin(address, brightness):
    global displayAddress
    displayAddress = address & 0xFF
    i2c.writeto(displayAddress, bytes([0x21])) #oscillator on
    i2c.writeto(displayAddress, bytes([0x81])) #display on, not blinking
    i2c.writeto(displayAddress, bytes([0xA0])) #set to an output driver (not a key matirx reader)
    display_setbrightness(brightness) #set initial brightness
    display_clear() #display starts with garbage, clear it

#clear display
def display_clear():
    i2c.writeto((0xFF & displayAddress), displayEmpty)

#set brightness
def display_setbrightness(brightness):
    global displayBrightness
    displayBrightness = brightness
    i2c.writeto(displayAddress, bytes([(0xE0 | displayBrightness & 0xF)]))

#update display by calling repeated write columns for the full animation frame
def display_update():
    for column, value in enumerate(fullFrame) :
        display_writeColumn(column, value)

#turn off base LEDs on Pimoroni Tiny2040
def led_stop():
    ledBlue.value(1)
    ledGreen.value(1)
    ledRed.value(1)

led_stop()

#main code begin

#start display with addess of 0x70 and brightness of 1
display_begin(0x70, 1)

while True:
    #display_emptyFrame() - not needed as red and green override current value, orange does not though
    display_setbrightness(random.randrange(3,15)) #adjust brightness which is typically 0-15
    display_writeRedFrame(redFrames[random.randrange(8)]) #pick random red frame
    display_writeGreenFrame(greenFrames[random.randrange(8)]) #pick random green frame
    display_writeOrangeFrame(orangeFrames[random.randrange(8)]) #pick random orange frame
    display_update() #send data to display
    utime.sleep_ms(random.randrange(10,200)) #sleep for random time