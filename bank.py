import config
import socket
import select
import sys

class bank:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((config.local_ip, config.port_bank))
        self.userBalances = {'Alice': 100, 'Bob': 100, 'Carol': 0} 
        self.userPins = {'Alice': 1234, 'Bob': 9999, 'Carol': 0000} 

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

    def prompt(self):
        sys.stdout.write("BANK: ")
        sys.stdout.flush()


    def handleLocal(self,inString):
        usrMsg  = inString.split(" ")
        
        if (len(usrMsg) >= 2): 
            usrCmd  = usrMsg[0]
            usrName = usrMsg[1] 

            if (usrCmd == 'balance'):
                try: 
                    print("$" + str(self.userBalances[usrName]) + "\n") 
                except: 
                    print("Invalid user") 
            if (usrCmd == 'deposit'):
                try: 
                    self.userBalances[usrName] += int(usrMsg[2]) 
                    print("$" + str(usrMsg[2]) + " added to " + usrName + "'s account\n")
                except: 
                    print("Invalid Request. Deposit requires a valid user and an ammount") 
        else: 
            print("Invalid request") 
    
        self.prompt() 


    def handleRemote(self, inBytes):
        atmMessage = inBytes.decode("utf-8") 
        atmMessage  = atmMessage.split(" ") 
        atmRequest  = atmMessage[0]
        atmUsr      = atmMessage[1] 

        if (atmRequest == 'balance'):
            balance     = self.userBalances[atmUsr]   
            response = "$" + str(balance) + "\n" 
            response = response.encode("utf-8")
            self.sendBytes(response)
        
        if (atmRequest == 'withdraw'):
            balance     = self.userBalances[atmUsr]   
            amt = int(atmMessage[2])
            if (balance >= amt): 
                self.userBalances[atmUsr] -= amt 
                response = "$" + str(amt) + " dispensed\n" 
            else: 
                response = "Insufficient Funds.\n" 

            response = response.encode("utf-8")
            self.sendBytes(response)
        
        if (atmRequest == 'check'): 
            response = "invalid"
            cardPin = atmMessage[2].rstrip()
            
            if(atmUsr in self.userPins): 
                if(int(self.userPins[atmUsr]) == int(cardPin)):
                    response = "valid" 
            response = response.encode("utf-8")
            self.sendBytes(response)


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

