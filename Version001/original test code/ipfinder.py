import socket
def IfDev ():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0] [10:13] == '245'
    

print IfDev()
