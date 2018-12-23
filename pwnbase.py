import socket
import telnetlib 
import time
import hashlib

def recvuntil(sock, txt):
  d = ""
  while d.find(txt) == -1:
    try:
      dnow = sock.recv(1)
      if len(dnow) == 0:
        print("-=(warning)=- recvuntil() failed at recv")
        print("Last received data:")
        print(d)
        return False
    except socket.error as msg:
      print("-=(warning)=- recvuntil() failed:", msg)
      print("Last received data:")
      print(d)     
      return False
    d += dnow
  return d

def recvall(sock, n):
  d = ""
  while len(d) != n:
    try:
      dnow = sock.recv(n - len(d))
      if len(dnow) == 0:
        print("-=(warning)=- recvuntil() failed at recv")
        print("Last received data:")
        print(d)        
        return False
    except socket.error as msg:
      print("-=(warning)=- recvuntil() failed:", msg)
      print("Last received data:")
      print(d)      
      return False
    d += dnow
  return d

# Proxy object for sockets.
class gsocket(object):
  def __init__(self, *p):
    self._sock = socket.socket(*p)

  def __getattr__(self, name):
    return getattr(self._sock, name)

  def recvall(self, n):
    return recvall(self._sock, n)

  def recvuntil(self, txt):
    return recvuntil(self._sock, txt)  

def go():  
  global HOST
  global PORT
  s = gsocket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((HOST, PORT))
  
  # CAPTCHA!
  s.recvuntil("Give a string X such that md5(X).hexdigest()[:5]=")   
  target = s.recvuntil(".\n")[:-2]
  i = 0
  while True:
    if hashlib.md5(str(i)).hexdigest()[:5] == target:
        s.sendall(str(i)+ "\n")
        break
    i += 1

  s.recvuntil("Given a random function defined in range ")
  functionRange = s.recvuntil(")").replace('(','').replace(')','').replace(' ','').split(',')
  functionRange[0] = int(functionRange[0])
  functionRange[1] = int(functionRange[1])
  print "Collecting Y values:"
  y = []
  for i in range(functionRange[0],functionRange[1]+1,1):
    s.sendall("1\n")
    s.sendall(str(i) + '\n')
    s.recvuntil(") = ")
    solution = s.recvuntil('\n')[:-1]
    print solution
    y.append(float(solution))

  # Find maximum value
  x = functionRange[0] + y.index(max(y))
  print "Max Y: " + str(max(y))
  maxY = max(y)
  gap = 0.5
  while True:
    s.sendall("1\n")
    time.sleep(1)
    s.sendall(str(x+gap) + '\n')
    s.recvuntil(") = ")
    solution = float(s.recvuntil('\n')[:-1])
    s.sendall("1\n")
    time.sleep(1)
    s.sendall(str(x-gap) + '\n')
    s.recvuntil(") = ")
    solution2 = float(s.recvuntil('\n')[:-1])
    if solution > maxY:
      x += gap
      print "X: " + str(x)
      print "Y: " + str(solution)
      maxY = solution
    elif solution2 > maxY:
      x -= gap
      print "X: " + str(x)
      print "Y: " + str(solution2)
      maxY = solution2
    else:
      gap /= 2
      print "Continue"
      continue
    print "Guessing: " + str(maxY) + " Gap: " + str(gap)
    s.sendall("2\n")
    time.sleep(1)
    s.sendall(str(maxY) + '\n')
    s.recvuntil("Enter your guess: ")
    print s.recvuntil(".")
    gap /= 2

  # Interactive sockets.
  t = telnetlib.Telnet()
  t.sock = s
  t.interact()
  s.close()

HOST = '199.247.6.180'
PORT = 14001
go()