import serial

connection = serial.serial_for_url("loop://", timeout=1)

message = "90,90\n"

connection.write(message.encode())
received = connection.readline().decode().strip()

print(f"Sent: {message.strip()}")
print(f"Received: {received}")

connection.close()