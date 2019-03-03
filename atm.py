import config
import socket
import select
import sys
import math

class atm:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((config.local_ip, config.port_atm))
        self.currentUsr = None

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
        if (self.currentUsr == None): 
            sys.stdout.write("ATM: ")
            sys.stdout.flush()
        else: 
            sys.stdout.write("ATM (" + self.currentUsr.rstrip() + "): ") 
            sys.stdout.flush()

  #====================================================================
  # TO DO: Modify the following function to handle the console input
  #====================================================================
    def handleLocal(self,inString):
        usrInput = inString.split(" ")
        command = usrInput[0]  
        atmMessage = "" 

        
            
        if (command == 'begin-session'):
            if (self.currentUsr == None): 
                with open("Inserted.card", 'r') as cardFile:
                    usr     = cardFile.readline().rstrip() 
                    cardPin = cardFile.readline().rstrip() 
                
                    #Validate User is member of bank
                    message = "check " + usr + " " + cardPin
                    self.sendBytes(bytes(message, 'utf-8'))
                    boolean, response = self.recvBytes() 
                    response = response.decode("utf-8")
                
                    if response == "valid":
                        print(" Welcome " + usr)
                        pin = input(" Please enter your pin: ")  
                        if (pin.rstrip() == cardPin.rstrip()): 
                            print(" Authorized.\n")
                            self.currentUsr = str(usr)
                            self.prompt()
                        else: 
                            print(" Unauthorized\n")
                            self.prompt()
                    else:
                        print(response) 
                        print("\n You are not a valid user. Please insert a valid ATM user account card.\n")
                        self.prompt()
            else: 
                print("\n Hey, " + self.currentUsr.rstrip() + ", you're already in a session!\n") 
                self.prompt()
            
        elif (command == 'end-session'): 
            if (self.currentUsr == None): 
                print("\n No user currently logged in\n") 
            else: 
                print("\n " + self.currentUsr + " logged out\n") 
                self.currentUsr = None 
            self.prompt()

        elif (command == 'withdraw'): 
            if (self.currentUsr == None): 
                print("\n No user currently logged in\n")
                self.prompt()
            else:
 
                try: 
                    amt = str(usrInput[1])
             
                    #FAIL SAFE DEFAULT FOR AMOUNT INPUT
                    if (all(a.isdigit() == True for a in amt)): 
                        atmMessage = command + " " +  self.currentUsr.rstrip() + " " + str(abs(int(amt)))                 
                        self.sendBytes(bytes(atmMessage, 'utf-8'))
                    else: 
                        print(" Amount must be a positive integer\n")
                        self.prompt()
                
                except IndexError: 
                    print("\n Withdraw requires an amount\n")
                    self.prompt()

        elif (command == 'balance'): 
            if (self.currentUsr == None): 
                print("\n No user currently logged in\n")
                self.prompt()
            else: 
                atmMessage = command + " " + self.currentUsr.rstrip()              
                self.sendBytes(bytes(atmMessage, 'utf-8'))
    
        #FAIL SAFE DEFAULT FOR COMMAND INPUT
        else: 
            print("\n Invalid Request. Please type only begin-session, end-session, withdraw, or balance\n")
            self.prompt()


    def handleRemote(self, inBytes):
        response = inBytes.decode("utf-8")

        print("\n", inBytes.decode("utf-8") )
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
    a = atm()
    a.mainLoop()

