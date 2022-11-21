'''
In this report, we are assessing two things
Ability to conduct independent research, organize information and cite appropriate sources
Ability to apply knowledge gained to an engineering problem.
    This is through simulating (at least part of) the system and demonstrating how you set up the simulation and why,
    and analyzing the observations from the simulation in a clear way.
    The observations from the simulation should reflect the theory.
    You can use any information in the course in addition to what you learned independently.
'''


#RESEARCH =========================================

#TOD0: graph out nodes as different things in space station that would need the internet and how they would be connected
    #involves more research


#https://web.archive.org/web/20130423142305/http://public.ccsds.org/publications/archive/717x0b1s.pdf

#FP: File Protocol

#---
'''
A set of four antenna systems are deployed in the ISS Service Module
supporting the current installation of the Kenwood D700 and D710 radios.
Each of the four antennas can support amateur radio operations on multiple frequencies
and allow for simultaneous automatic and crew-tended operations.
Having four antennas also ensures that ham radio operations can continue
aboard the station should one or more of the antennas fail.
Three of the four antennas are identical and each can support
both transmit and receive operations on 2 meter, 70 cm, L band and S band.
They also support reception for the station's Russian Glisser TV system,
which is used during spacewalks. The fourth antenna has a 2.5-meter (8 foot) long
vertical whip that can be used to support High Frequency (HF) operations,
particularly on 10 meters. Currently, one of the 3 VHF/UHF antennas is disconnected
and the HF antenna has no radio hardware available for use.

Two antennas are installed in the Columbus module,
currently serving the Ericcson radios deployed there.
Frequencies available for transmission to and from Columbus are 2 meters,
70 centimeters, L-band and S-band. These antennas will also support the Ham TV  DATV transmitter.
'''
#ISS Service Module
#has 4 antennas
#Kenwood D700 and D710 radios
#3/4 support L&S band
#1 does HF

#Columbus Module
#2 antennas
#connect to Ericcson radios
#---

#star topolgy   https://public.ccsds.org/Pubs/880x0g3.pdf
#include things like:
    #user consoles, laptops, Air Controller, Solar Panel Switchers (Solar MBSU), Door Control,
    #https://www.researchgate.net/figure/International-Space-Station-EPS-Architecture_fig2_269208039

try:
    import math
    import networkx as nx
    import matplotlib.pyplot as plt
    import numpy as np
    import time
    import sys
    import random
except Exception as e:
    print("Failed to import some modules, if this is not a simulation fix this before continuing")
    print(F"Exception raised: {e}")


'''
TERMINOLOGY

EOF End Of File
FTP File Transfer Protocol
NP Network Protocol
PDU Protocol Data Unit
PICS Protocol Implementation Conformance Statement
RFC Request for Comments
SCPS Space Communications Protocol Specification
SCPS-NP SCPS Network Protocol
SCPS-SP SCPS Security Protocol
SCPS-TP SCPS Transport Protocol
TCP Transmission Control Protocol
'''
class FP:
    def __init__(self,debug=False):
        #https://web.archive.org/web/20130423142305/http://public.ccsds.org/publications/archive/717x0b1s.pdf
        print("network - init")
        self.G = None
        self.add_colors=[]

        self.stream_mode = False

        #data
        self.curr_datatype = None
        self.data_path = None    #str ./__filename__
        self.data = None

        #build and display ISS graph
        self.build_graph(not(debug))

    '''
    def testGraph(self):
        self.G = nx.Graph()
        self.G.add_nodes_from(
            [("one", {"color": "red"}),
             (2, {"color": "green"})])
        self.G.add_edge("one", 2)
        nx.draw(self.G, node_color=['red','blue'], with_labels=True, font_weight='bold')
        #nx.draw(self.G, with_labels=True, font_weight='bold')
        plt.show()

    def matplot_test(self):
        self.G = nx.Graph()
        self.G = nx.petersen_graph()
        subax1 = plt.subplot(121)
        nx.draw(self.G, with_labels=True, font_weight='bold')
        subax2 = plt.subplot(122)
        nx.draw_shell(self.G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
        plt.show()
        '''

    def build_graph(self,show=True):
        self.G = nx.Graph()
        self.G.add_nodes_from([
            ("ISS Service Module"),
            ("Columbus Module"),
            ("Radio connection"),
            ("ISS Server")
            ])

        self.G.add_edges_from([
            ("ISS Service Module","Radio connection"),
            ("Columbus Module","Radio connection"),
            ("Radio connection","ISS Server")
            ])
        #print("nodes: ",self.G.nodes)
        #print("# nodes: ",self.G.number_of_nodes())
        #print("adj: ",self.adj_better("input"))

        self.add_in_nodes("User console, Air Controller, Solar Panel MBSU, Door Control")
        nx.draw(self.G, node_color=["green","green","green","blue"]+self.add_colors, with_labels=True, font_weight='bold')
        # nx.draw(self.G, with_labels=True, font_weight='bold')

        if show: plt.show()

    def adj_better(self,inp):
        l = str(self.G.adj[inp]).split("'")
        l1 = []
        for i in range(len(l)):
            if l[i] == "{" or l[i] == ": {}, " or l[i] == ": {}}":
                continue
            l1.append(l[i])
        return l1

    def add_in_nodes(self,inp):
        l = inp.split(", ")
        self.G.add_nodes_from(l)
        for i in range(len(l)):
            self.add_colors.append("red")
            self.G.add_edge(l[i],"ISS Server")

    def main_loop(self):
        while True:
            print("")
            inp = input("enter command: ")  # CMD_NAME INPUTS
            t_ary = inp.split(" ")
            #pass command to FP
            #send str of first entry (cmd name), then inputs as array
            Feebee.cmd_recognize(str(t_ary[0]), t_ary[1:])

    def cmd_recognize(self,cmd,arr):
        #print("CMD:\t"+cmd)
        #print("INPUTS:\t"+str(arr))

        #go through giant list of if's to see if cmd (str) matches,
        #perform that command with arr as input to it
        try:
            if cmd == "restart":
                self.restart()
            elif cmd == "STRU":
                self.STRU()
            elif cmd == "TYPE":
                if not arr:
                    self.TYPE(None,True)
                else:
                    self.TYPE(str(arr[0]), True)
            elif cmd == "STOR":
                if len(arr) <= 3:
                    self.STOR(arr[0],arr[1],arr[2])
                else:
                    self.STOR(arr[0], arr[1], arr[2], bool(arr[3]))
            elif cmd == "RETR":
                self.RETR()
            elif cmd == "PROXY":
                self.PROXY()
            elif cmd == "REST":
                self.REST()
            elif cmd == "USER":
                self.USER()
            elif cmd == "PASS":
                self.PASS()
            elif cmd == "CWD":
                self.CWD()
            elif cmd == "QUIT":
                self.QUIT()
            elif cmd == "PORT":
                self.PORT()
            elif cmd == "PASV":
                self.PASV()
            elif cmd == "MODE":
                self.MODE()
            elif cmd == "RNFR":
                self.RNFR()
            elif cmd == "RNTO":
                self.RNTO()
            elif cmd == "ABOR":
                self.ABOR()
            elif cmd == "DELE":
                self.DELE()
            elif cmd == "RMD":
                self.RMD()
            elif cmd == "MKD":
                self.MKD()
            elif cmd == "LIST":
                self.LIST()
            elif cmd == "STAT":
                self.STAT()
            elif cmd == "SITE":
                self.SITE()
            elif cmd == "ACCT":
                self.ACCT()
            elif cmd == "CDUP":
                self.CDUP()
            elif cmd == "NLST":
                self.NLST()
            elif cmd == "ARST":
                self.ARST()
            elif cmd == "BETS":
                self.BETS()
            elif cmd == "COPY":
                self.COPY()
            elif cmd == "IDLE":
                self.IDLE(float(arr[0]))
            elif cmd == "INTR":
                self.INTR()
            elif cmd == "NARS":
                self.NARS()
            elif cmd == "NBES":
                self.NBES()
            elif cmd == "NSUP":
                self.NSUP()
            elif cmd == "READ":
                self.temp()
            elif cmd == "SIZE":
                print(F"FILE SIZE: {self.SIZE(True)}")
            elif cmd == "SUPP":
                self.SUPP()
            elif cmd == "UPDT":
                self.UPDT()
            else:
                print("ERROR: CMD NOT RECOGNIZED")
        except Exception as e:
            print(F"ERROR RUNNING COMMAND: {e}")

        return

    def cmd_ex(self):
        print("Examples:\n"
              "STOR lol lol.txt ASCII\t\t: send txt file\n"
              "STOR lol lol.txt ASCII 1\t: send txt file w/ forced fail transmittion")

    #actual commands
    def restart(self):
        return

    def STRU(self):
        return

    def TYPE(self,inp=None,verbose=False):
        #set
        if inp:
            if inp != "IMAGE" and inp != "ASCII" and inp != "PACKET":
                raise TypeError("INVALID DATA TYPE: TYPE()")

            if verbose: print(F"set curr_datatype: {inp}")
            self.curr_datatype = inp
        #ret
        else:
            if verbose: print(F"curr_datatype: {self.curr_datatype}")
            return self.curr_datatype

    def STOR(self,data,name,type,force_error=False,recurrsion=False):
        '''
        user-to-server transfer (e.g., STOR):
        1) the user-FP shall send ‘SIZE pathname’ to the receiving server-FP;
        2) the server-FP shall send ‘213 pathname SIZE rrrr’ to the user-FP, where rrrr is the
        size of the file (indicated by pathname) stored locally at the server;
        3) to restart the transfer, the user-FP shall reposition its local file system using restart
        marker rrrr and send the command ‘REST rrrr’ to the server-FP;
        4) the server-FP shall save restart marker rrrr for restart;
        '''
        #check for connection to server
        if "ISS Server" not in self.adj_better("User console"): raise TypeError("CONSOLE NOT CONNECTED TO SERVER: STOR()")

        #1.)
        #sending from console to server the data from the console located at path
        print(F"USER-SERVER: SIZE ./{name}")
        #random delay time take to send
        #if at 1(or over, means ACK didnt come
        d_temp = random.randint(0,99)
        print(F"[[waiting rand trans time: {d_temp/100}]]")
        time.sleep(d_temp/100) #random delay 0.0-1.0 time take to send

        #3&4.)
        #error in transmission
        err = force_error
        while not d_temp or err: #1% chance error
            err = False #only happen once
            d_temp = random.randint(0,99)
            t_temp = time.time()
            self.RETR(t_temp)
            print(F"USER-USER: [rand delay before retry trans: {d_temp/100}]")
            self.IDLE(d_temp/100)
            self.STOR(data,name,type,False,True)    #retry
            self.REST(t_temp)

        if not recurrsion:
            #2.)
            #confirmation recieved (is sim)
            self.data = data
            self.data_path = "./"+name
            self.curr_datatype = type
            print(F"SERVER-USER: 213 {self.data_path} SIZE {self.SIZE()}")
        return

    def RETR(self,inp):
        '''
        1) the user-FP shall determine the size (rrrr) of the file as stored by the local file system;
        2) to restart the transfer, the user-FP shall reposition its local file system using restart
        marker rrrr and send the command ‘REST rrrr’ to the server-FP;
        3) the server-FP shall save restart marker rrrr for restart;
        '''
        print(F"USER-USER_REPO: restart marker {inp}")
        print(F"USER-SERVER: REST {inp}")
        return

    def PROXY(self):
        return

    def REST(self,inp):
        #server console command to cancel transmission
        print(F"SERVER-SERVER REPO: restart marker {inp}")
        print("SERVER-SERVER: [restarted transmission]")
        return

    def USER(self):
        #return user IP?
        return

    def PASS(self):
        return

    def CWD(self):
        return

    def QUIT(self):
        #quit
        return

    def PORT(self):
        #return some kinda port
        return

    def PASV(self):
        return

    def MODE(self):
        return

    def RNFR(self):
        return

    def RNTO(self):
        #return to
        return

    def ABOR(self):
        #abort
        return

    def DELE(self):
        #delete
        return

    def RMD(self):
        return

    def MKD(self):
        return

    def LIST(self):
        #list files?
        return

    def STAT(self):
        return

    def SITE(self):
        return

    def ACCT(self):
        return

    def CDUP(self):
        return

    def NLST(self):
        return

    #xml like
    def ARST(self):
        #ARST <CRLF>
        return

    def BETS(self):
        #BETS <BETS-fill-code> <CRLF>
        return

    def COPY(self):
        #COPY <SP> <pathname> <SP> <pathname> <CRLF>
        return

    def IDLE(self, inp):
        #IDLE <SP> <decimal-integer> <CRLF>
        time.sleep(inp)
        return

    def INTR(self):
        #INTR <CRLF>
        return

    def NARS(self):
        #NARS <CRLF>
        return

    def NBES(self):
        #NBES <CRLF>
        return

    def NSUP(self):
        #NSUP <CRLF>
        return

    def READ(self):
        #READ <SP> <pathname> <CRLF>
        return

    def SIZE(self,verbose=False):
        #SIZE <SP> <pathname> <CRLF>
        ty = self.TYPE()    #should just get the var but its part of the challenge
        if verbose: print(F"Type: {ty}")
        if ty == "IMAGE" or ty == "ASCII" or ty == "PACKET":
            return sys.getsizeof(self.data)
        else:   #None
            if verbose: print("MINOR ERROR: SIZE(): TYPE = NONE")
            return 0

    def SUPP(self):
        #SUPP <CRLF>
        return

    def UPDT(self):
        #UPDT <SP> <pathname> <CRLF>
        return
'''
funtions to add
USER, PASS, CWD, QUIT, PORT, PASV, TYPE, STRU, 
MODE, RETR, STOR, RNFR, RNTO, REST, ABOR, DELE, 
RMD, MKD, LIST, STAT, SITE, ACCT, CDUP, NLST, 
NOOP, PWD, STOU, SYST, APPE, HELP, 

ARST <CRLF>
BETS <BETS-fill-code> <CRLF>
COPY <SP> <pathname> <SP> <pathname> <CRLF>
IDLE <SP> <decimal-integer> <CRLF>
INTR <CRLF>
NARS <CRLF>
NBES <CRLF>
NSUP <CRLF>
READ <SP> <pathname> <CRLF>
SIZE <SP> <pathname> <CRLF>
SUPP <CRLF>
UPDT <SP> <pathname> <CRLF>
'''




if __name__ == "__main__":
    Feebee = FP()#True)
    #Feebee.testGraph()
    #Feebee.matplot_test()

    Feebee.cmd_ex()
    Feebee.main_loop()