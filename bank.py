import config
import socket
import select
import sys

class bank:
  def __init__(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.s.bind((config.local_ip, config.port_bank))
 
  def __del__(self):
    self.s.close()

  def sendBytes(self, m):
    self.s.sendto(m, (config.local_ip, config.port_router))

  def recvBytes(self):
      data, addr = self.s.recvfrom(config.buf_size)
      if addr[0] == config.local_ip and addr[1] == config.port_router:
        return True, data
      else:
        return False, bytes(0)

  #====================================================================
  # TO DO: Modify the following function to output prompt properly
  #====================================================================
  def prompt(self):
    sys.stdout.write("BANK: ")
    sys.stdout.flush()


  #====================================================================
  # TO DO: Modify the following function to handle the console input
  #====================================================================
  def handleLocal(self,inString):
    self.sendBytes(bytes(inString, "utf-8"))
    self.prompt() 

  #====================================================================
  # TO DO: Modify the following function to handle the atm request 
  #====================================================================
  def handleRemote(self, inBytes):
    print("\nFrom ATM: ", inBytes.decode("utf-8") )
    self.sendBytes(inBytes)
    self.prompt() 
 

  def mainLoop(self):
    self.prompt()
  
    while True:
      l_socks = [sys.stdin, self.s]
           
      # Get the list sockets which are readable
      r_socks, w_socks, e_socks = select.select(l_socks, [], [])
           
      for s in r_socks:
        # Incoming data from the router
        if s == self.s:
          ret, data = self.recvBytes()
          if ret == True:
            self.handleRemote(data) # call handleRemote 
                                 
        # User entered a message
        elif s == sys.stdin:
          m = sys.stdin.readline().rstrip("\n")
          if m == "quit": 
            return
          self.handleLocal(m) # call handleLocal
        

if __name__ == "__main__":
  b = bank()
  b.mainLoop()

