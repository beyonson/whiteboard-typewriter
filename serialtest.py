import serial
import time
#
#serialToMotor = serial.Serial(port='COM3',baudrate=9600)
#for i in range(1,10):
#    line = ""
#    for j in range(10):
#        line += str(i*j) + "\n"
#    serialToMotor.write(str.encode(line))

# Open grbl serial port
s = serial.Serial('COM3',9600)

# Open g-code file
f = open('gcode/singleline.gcode','r');

# Wake up grbl
s.write(str.encode("\r\n\r\n"))
time.sleep(2)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input

# Stream g-code to grbl
for line in f:
    l = line.strip() # Strip all EOL characters for streaming
    print(f'Sending: {l}')
    s.write(str.encode(l + '\n')) # Send g-code block to grbl
    grbl_out = s.readline() # Wait for grbl response with carriage return
    print(f' : {grbl_out.strip()}')

# Wait here until grbl is finished to close serial port and file.
print("  Press <Enter> to exit and disable grbl.")

# Close file and serial port
f.close()
s.close()
