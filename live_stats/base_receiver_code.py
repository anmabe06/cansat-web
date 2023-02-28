import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

portsList = []

for onePort in ports:
    portsList.append(str(onePort))
    print(str(onePort))

val = input("Select Port: COM")

for x in range(0,len(portsList)):
#    if portsList[x].startswith("COM" + str(val)):
        portVar = str(val)
        print(portVar)

serialInst.baudrate = 9600
serialInst.port = portVar
serialInst.open()


while True:
	if serialInst.in_waiting:
		packet = serialInst.readline()
		print(packet.decode('utf').rstrip('\n'))
        
        
        
        
import xlswriter

archivo = xlswriter.Worbook ('prueba.xlsx')
hoja = archivo.add_worksheet
hoja.write(0,0,'Hola')
archivo.close()