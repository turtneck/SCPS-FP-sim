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
    print("Failed to import some modules, likely missing")
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
        print(
'''\n==============NOTICE==============
Some funcs arent their complete purpose as mandated
in reports due to unability to wait apporpriately to a seperate simualted server.

Commands like these have instead been absorbed into others,
still simulating the result between the two.

EX: ABOR becoming a set function that reacts with STOR
instead of using ABOR in the middle of STOR's runtime
==================================
"psst, hey. the login password is: ECE1150"
Enter: "CWD PASS ___" to start the sim
(not required in debug mode)''')

        self.loud_debug = debug

        self.G = None
        self.add_colors=[]

        #self.stream_mode = False
        self.autorestart = False    #0: AutoRest off, 1:AutoRest on (ARST, NARS)
                                    #need more info
        self.abort = 0     #0:off, 1:ABOR, 2:INTR - pg19 table

        #data
        self.curr_datatype = None   #ASCII,IMAGE,PACKET
        self.data_path = None    #str ./__filename__
        self.data = None
        self.dataname_list = []
        self.data_list = []
        self.datatype_list = []
        self.partial_data = None
        self.flag_BETS = None  #need more info
        self.fpSuppressReplyText = False
        self.pass_lock = None
        self.mode = False   #if in transmittion

        #build and display ISS graph
        self.build_graph(not debug)

        #self.cmd_ex()
        if not debug: self.lock(True)
        self.main_loop()

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

    def debug(self):
        print("====NOT REAL CMD, JUST FOR DEBUG OF THIS SIM====")

        #flags
        print("\nFlags:----")
        print(F"autorestart: {self.autorestart}")
        print(F"abort:       {self.abort}")
        print(F"flag_BETS:   {self.flag_BETS}")
        print(F"fpSuppressReplyText: {self.fpSuppressReplyText}")
        print(F"pass_lock:   {self.pass_lock}")
        print(F"mode:        {self.mode}")

        #local temp data
        print("\nLocal Temp Data:----")
        print(F"curr_datatype: {self.curr_datatype}")
        print(F"data_path:     {self.data_path}")
        print(F"data:          {self.data}")
        print(F"partial_data:  {self.partial_data}")

        #server data
        print("\nServer Data:----")
        print("filename, data, filetype:")
        if not self.dataname_list: print("[[NO DATA]]")
        for i in range(len(self.dataname_list)):
            print(F"{i}:\t{self.dataname_list[i]}, {str(self.data_list[i])}, {self.datatype_list[i]}")

    def lock(self,first=False):
        #"CWD PASS ___"
        while self.pass_lock != "ECE1150":
            print("==================================")
            inp = input("enter command: ")  # CMD_NAME INPUTS
            t_ary = inp.split(" ")

            if len(t_ary)==3:   #correct fields
                if str(t_ary[0]) == "CWD" and str(t_ary[1]) == "PASS":   #correct command
                    self.pass_lock = str(t_ary[2])
                    if self.pass_lock != "ECE1150": print("INCORRECT LOGIN")
                else:
                    print(F"ACESS DENIED")
            elif len(t_ary)>3 and str(t_ary[0]) == "CWD" and str(t_ary[1]) == "PASS":
                print(F"ERROR RUNNING COMMAND")
            else:
                print(F"ACESS DENIED")

        print("[[ACCESS GRANTED]]")
        if first: print("==================================")

    def main_loop(self):
        if self.loud_debug: print("==================================")
        print("Use \"HELP\" for a list of commands and examples, or \"HELP _CMD_ for info on a command\"")
        print("Also see \"debug\" for a list of the current variables in use, including list of uploaded data on server")
        while True:
            print("==================================")
            inp = input("enter command: ")  # CMD_NAME INPUTS
            t_ary = inp.split(" ")
            #pass command to FP
            #send str of first entry (cmd name), then inputs as array
            self.cmd_recognize(str(t_ary[0]), t_ary[1:])

    def cmd_recognize(self,cmd,arr):
        #print("CMD:\t"+cmd)
        #print("INPUTS:\t"+str(arr))

        #go through giant list of if's to see if cmd (str) matches,
        #perform that command with arr as input to it
        #try:
        if cmd == "STRU":
            print("DIRECT CONSOLE ACCESS DENIED")
        elif cmd == "TYPE":
            if not arr:
                self.TYPE("curr",None,True,True)
            elif len(arr) == 1:
                self.TYPE(str(arr[0]),None,True,True)
            elif len(arr) == 2:
                self.TYPE(str(arr[0]),str(arr[1]),False,True)
        elif cmd == "STOR":
            if len(arr) == 3:
                self.STOR(arr[0],arr[1],arr[2])
            else:
                self.STOR(arr[0],arr[1],arr[2],arr[3])
        elif cmd == "RETR":
            print("THIS IS A SERVER-CONSOLE COMMAND")
        elif cmd == "PROXY":
            self.PROXY()
        elif cmd == "REST":
            print("DIRECT CONSOLE ACCESS DENIED")
        elif cmd == "USER":
            self.USER()
        elif cmd == "PASS":
            self.PASS()
        elif cmd == "CWD":
            if len(arr)>=2:   #not empty, more then 2 fields
                if str(arr[0]) == "PASS":   #correct command
                    self.CWD(arr[1])
                else:
                    print(F"ERROR RUNNING COMMAND, NOT FOLLOWED BY PASS")
            else:
                print(F"ERROR RUNNING COMMAND")
        elif cmd == "QUIT":
            self.QUIT()
        elif cmd == "PORT":
            print("DIRECT CONSOLE ACCESS DENIED")
        elif cmd == "PASV":
            print("DIRECT CONSOLE ACCESS DENIED")
        elif cmd == "MODE":
            print("DIRECT CONSOLE ACCESS DENIED")
        elif cmd == "RNFR":
            self.RNFR()
        elif cmd == "RNTO":
            self.RNTO()
        elif cmd == "ABOR":
            self.ABOR()
        elif cmd == "DELE":
            self.DELE(str(arr[0]))
        elif cmd == "RMD":
            print("THIS IS A SERVER-CONSOLE COMMAND")
        elif cmd == "MKD":
            print("THIS IS A SERVER-CONSOLE COMMAND")
        elif cmd == "LIST":
            self.LIST(arr)
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
            self.COPY(arr[0],arr[1])
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
            if len(arr) == 3:
                self.READ(arr[0], arr[1], arr[2])
            else:
                self.READ(arr[0], arr[1], arr[2], arr[3])
        elif cmd == "SIZE":
            print(F"FILE SIZE: {self.SIZE(arr[0],True,True)}")
        elif cmd == "SUPP":
            self.SUPP()
        elif cmd == "UPDT":
            if len(arr) == 3:
                self.UPDT(arr[0], arr[1], arr[2])
            else:
                self.UPDT(arr[0], arr[1], arr[2], arr[3])
        elif cmd == "HELP":
            if not arr:
                self.HELP()
            else:
                self.HELP(arr[0])
        elif cmd == "debug":
            self.debug()
        else:
            print("ERROR: CMD NOT RECOGNIZED")
        #except Exception as e:
        #    print(F"ERROR RUNNING COMMAND: {e}")

        return

    def cmd_ex(self):
        print(
"""Examples:
STOR lol ./lol.txt ASCII    : send txt file
---
STOR lol ./lol.txt ASCII x  : send txt file w/ timed-out transmittion, x time(s)
---
ABOR                        : send txt file w/ aborted transmittion
STOR lol ./lol.txt ASCII
---
INTR                        : send txt file w/ interupted transmittion
STOR lol ./lol.txt ASCII
---
ARST                        : send txt file w/ Auto Restart
STOR lol ./lol.txt ASCII 1    could also use above ABOR and INTR cmd combos for diff results
---
STOR lol ./lol.txt ASCII    : see lol.txt's filetype
TYPE ./lol.txt
---
STOR lol ./lol.txt ASCII    : set lol.txt's filetype to an IMAGE
TYPE ./lol.txt IMAGE
---
STOR lol ./lol.txt ASCII    : send a txt file to the server then update it
UPDT lmao ./lol.txt ASCII     also works if both are UPDT commands
---
UPDT lol ./lol.txt ASCII    : send a txt file to the server then delete it
DELE ./lol.txt
---
READ 123456789 ./lol.txt ASCII   : send first half of data to a server,
                                   then the other in another transmission
                                   note: can see how it did this with the "debug" command
---
LIST lol ./lol.txt ASCII lmao ./lmao.txt ASCII    :send multiple files in one command
---
STOR lol ./lol.txt ASCII    : STOR two txt files then rewrite the 2nd
STOR lol ./lmao.txt ASCII     with a copy of the first
COPY ./lol.txt ./lmao.txt

==================================
CMD LIST:
USER, PASS, CWD, QUIT, PORT, PASV, TYPE, STRU, 
MODE, RETR, STOR, RNFR, RNTO, REST, ABOR, DELE, 
RMD, MKD, LIST, STAT, SITE, ACCT, CDUP, NLST, 
NOOP, PWD, STOU, SYST, APPE, HELP

ARST, BETS, COPY, IDLE, INTR, NARS, NBES, NSUP, 
READ, SIZE, SUPP, UPDT

debug (for this sim only)""")

    #actual commands
    def STRU(self,inp):
        print(F"USER-USER_REPO: PACKET STRUCTURE: {inp}")

    def TYPE(self,file,filetype=None,ret=False,verbose=False):
        #ret= 0:return, 1:set
        #ret
        if ret:
            if file == "curr":
                if verbose: print(F"current/last-used filetype: {self.curr_datatype}")
                return self.curr_datatype
            else:
                if verbose: print(F"{file}'s filetype: {self.datatype_list[self.dataname_list.index(file)]}")
                return self.datatype_list[self.dataname_list.index(file)]
        #set
        else:
            if filetype != "IMAGE" and filetype != "ASCII" and filetype != "PACKET":
                raise TypeError("INVALID DATA TYPE: TYPE()")

            if verbose: print(F"Set {file}'s filetype: {filetype}")

            self.curr_datatype = filetype
            self.datatype_list.append(filetype)

    def STOR(self,data,name,file_type,forced_TO=0,recurrsion=False):
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
        if "ISS Server" not in self.adj_better("User console"): raise TypeError("STOR(): CONSOLE NOT CONNECTED TO SERVER: STOR()")
        if name[:2] != "./": raise TypeError(F'STOR(): {name}: FILENAME MUST START WITH "./" FOR DIRECTORY PURPOSES')

        if self.flag_BETS: print("USER-USER: TRANSMITTING IN BEST EFFORT TRANSPORT SERVICE MODE\t\t[[This is for SCPS-TP, not simulated]]")
        if file_type == "PACKET": self.STRU("R")

        #1.)
        #sending from console to server the data from the console located at path
        self.MODE()
        self.PORT()
        self.PASV(False)
        print(F"USER-SERVER: SIZE {name}")
        self.data_path = name
        #self.curr_datatype = file_type
        self.TYPE(None, file_type)
        self.partial_data = data

        #random delay time take to send
        #if at 1(or over, means ACK didnt come
        d_temp = random.randint(0,99)
        print(F"[[waiting rand trans time: {d_temp/100}]]")
        time.sleep(d_temp/100) #random delay 0.0-1.0 time take to send

        #3&4.)
        #error in transmission
        err = int(forced_TO)
        while not d_temp or self.abort>0 or err>0: #1% chance error
            err-=1
            if not self.autorestart:
                #dest file didnt existed at start of transfer
                if name not in self.dataname_list:
                    if self.abort == 2: #INTR
                        print("USER-USER: [KEEPING PARTIAL FILE]")
                elif self.abort == 1 or not d_temp:  # ABOR/timeout
                    print("USER-USER: [DELETING PARTIAL FILE]")
                    self.partial_data = None
                #dest file exist
                else:
                    if self.abort == 2: #INTR
                        print("USER-USER: [DELETING ORIGINAL FILE, KEEPING PARTIAL FILE]")
                        #self.dataname_list.remove(name)
                        self.RMD(name)
                    elif self.abort == 1 or not d_temp:  #ABOR/timeout
                        print("USER-USER: [RESTORING ORIGINAL FILE, DELETING PARTIAL FILE]")
                        self.partial_data = None
            #auto rest
            else:
                if not d_temp:
                    if name not in self.dataname_list:  # dest file didnt existed at start of transfer
                        print("USER-USER: [KEEPING PARTIAL FILE]")
                    else:
                        print("USER-USER: [DELETING ORIGINAL FILE, KEEPING PARTIAL FILE]")
                        #self.dataname_list.remove(name)
                        self.RMD(name)

            if self.abort == 1: #ABOR
                '''
                Server aborts FP service in progress
                - Server closes data connection
                - Server returns 426 indicating service request was terminated abnormally
                - Server sends 226 reply indicating abort successful
                '''
                print("SERVER-SERVER: CLOSED DATA CONNECTION")
                if not self.fpSuppressReplyText: print("SERVER-USER: 446 [SERVICE REQUEST TERMINATED ABNORMALLY, ABOR]")
                if not self.fpSuppressReplyText: print("SERVER-USER: 226 [ABORT SUCCESSFUL, ABOR]")
                self.abort = 0
                self.MODE()
                return
            if self.abort == 2: #INTR
                '''
                1) the user-FP shall send ‘INTR’ to the server-FP;
                2) in response, the server-FP shall stop the file transfer and send ‘256 Transfer
                Interrupted at rrrr’ to the user-FP, where rrrr is the size of the file stored locally at
                the server;
                3) the user-FP shall save the restart marker rrrr for restart;
                4) the user-FP may reinitiate the transfer process by repositioning its local file
                system using restart marker rrrr and sending ‘REST rrrr’ to the server-FP;
                '''
                if not self.fpSuppressReplyText: print(F"SERVER-USER: 256 TRANSFER INTERRUPTED AT {self.SIZE(data,False)} [ABORT SUCCESSFUL, ABOR]")
                self.abort = 0
                #rest in list in handled right below

            d_temp = random.randint(0,99)
            t_temp = time.time()
            self.RETR(t_temp)
            print(F"USER-USER: [rand delay before retry trans: {d_temp/100}]")
            self.IDLE(d_temp/100)
            self.STOR(data,name,file_type,False,True)    #retry
            self.REST(t_temp)
            self.MODE()

        #success
        if not recurrsion:
            #2.)
            #confirmation recieved (is sim)
            self.PASV(True)
            self.MKD(data,name,file_type)
            if not self.fpSuppressReplyText: print(F'SERVER-USER: 213 {self.data_path} SIZE {self.SIZE("curr",False)}')
        return

    def RETR(self,inp):
        '''
        1) the user-FP shall determine the size (rrrr) of the file as stored by the local file system;
        2) to restart the transfer, the user-FP shall reposition its local file system using restart
        marker rrrr and send the command ‘REST rrrr’ to the server-FP;
        3) the server-FP shall save restart marker rrrr for restart;
        '''
        '''
        - Server transfers a copy of the file, specified in the
        pathname, to the server- or user-DTP at the other end of the data connection
        - Status and contents at the server site are unaffected
        '''
        print(F"USER-USER_REPO: restart marker {inp}")
        print(F"USER-SERVER: REST {inp}")
        return

    def PROXY(self):
        '''
        SERVER-SERVER
        1) the user-FP shall send ‘SIZE pathname’ to the receiving server-FP;
        2) the receiving server-FP shall send ‘213 pathname SIZE rrrr’ to the user-FP, where
        rrrr is the size of the file (indicated by pathname) stored locally at the receiving
        server;
        3) to restart the transfer, the user-FP shall
        – send the command ‘REST rrrr’ to the receiving server-FP;
        – send ‘REST ssss’ to the sending server-FP, where ssss = rrrr;
        4) each server shall save the received restart markers for restart.
        '''
        print("Depreciated for this sim; Absorbed into STOR")

    def REST(self,inp):
        #RESTART
        '''
        – The REST command shall cause the server-FP to begin execution the file transfer
        command immediately following the REST command at the restart marker rather
        than at the beginning of the file.
        – The argument field for the REST command shall contain the restart marker at
        which the file transfer is to be restarted.
        – The REST command shall be immediately followed by the appropriate SCPS-FP
        file transfer command, which shall cause the interrupted file transfer to resume
        '''
        #server console command to cancel transmission
        print(F"SERVER-SERVER REPO: restart marker {inp}")
        print("SERVER-SERVER: [restarted transmission]")
        return

    def USER(self):
        '''
        - Server allows new USER command to be entered at any point to change access control
        - If a new USER command is issued, all transfer parameters remain unchanged
        - If a new USER command is issued, any file transfer in progress is completed under the old access control parameters
        '''
        print("Not actually command, but rather a console var replaced with the CMD you put in.\nEx: READ,STOR,TYPE,etc")
        #return user IP?
        return

    def PASS(self):
        '''
        - immediately preceded by user command
        - User-DTP hides sensitive password information
        '''
        print("ERROR: MUST BE FOLLOWING CWD (for this sim)")
        #print("Not actually command, but something put after any CMD and its ARG's for security.\nDepreciated for this sim")

    def CWD(self,inp):
        '''
        - Server permits working with a different directory
        - Server preserves the user’s login/accounting information
        - Server preserves transfer parameter settings
        '''
        self.pass_lock = inp
        if self.pass_lock != "ECE1150":
            print("LOGGED OUT")
            self.lock()
        return

    def QUIT(self):
        '''
        - Server takes the effective action of an abort (ABOR) and a
        logout (QUIT) if an unexpected close occurs on the control connection
        '''
        self.CWD("")
        #quit
        return

    def PORT(self):
        '''
        - User-FP sends PORT command for stream mode for each transfer
        - 32-bit Internet host address and a 16-bit SCPS-TP port address are concatenated to form the PORT argument
        - Address information is broken into eight-bit fields
        - Value of each field is transmitted as a decimal number (in character string representation)
        - Fields are separated by commas
        '''
        print("USER-SERVER: 172,8890,1337,6880\t\t(made up for this sim)")
        #return some kinda port
        return

    def PASV(self,part=False):
        '''
        - Server-FP has implemented PASV
        - User-FP sends PASV per transfer
        '''
        if not part: print("USER-SERVER: [Server Port Request]")
        else:
            if not self.fpSuppressReplyText: print("SERVER-USER: 452,92,806,528\t\t(made up for this sim)")

    def MODE(self):
        #toogle if in transmittion
        self.mode = not self.mode

    def RNFR(self):
        print("[[[Service commands: Description missing from released Document]]]")

    def RNTO(self):
        print("[[[Service commands: Description missing from released Document]]]")

    def ABOR(self):
        #abort
        #cant really sim, so its been absorbed into STOR. just a set now
        '''
        - If the previous command has been completed including data transfer, ABOR is processed
        - If FP command already completed when ABOR received
            - Server closes data connection, if open
            - Server sends 226 reply indicating abort successful
        - FP command not completed when ABOR received
            - Server aborts FP service in progress
            - Server closes data connection
            - Server returns 426 indicating service request was terminated abnormally
            - Server sends 226 reply indicating abort successful
        '''
        if self.abort != 1:
            self.abort = 1
        else:
            self.abort = 0

    def DELE(self,data):
        #delete
        '''
        - Server deletes file specified in the pathname at the server site
        - User-FP provides extra level of protection (‘do you really want to delete’)
        '''
        inp = input("do you really want to delete? (y/n): ")
        if inp == "y" or inp == "Y":
            self.RMD(data)
        else:
            print("DELETION CANCELED")

    def RMD(self,inp,verbose=True):
        #Server removes directory specified in pathname from server site
        if inp not in self.dataname_list:
            if not self.fpSuppressReplyText:
                print(F"SERVER-USER: RMD(): PATHNAME {inp} DOESNT EXIST")
                print("SERVER-USER: DELETION CANCELED")
            return
        else:
            if verbose: print(F"SERVER-SERVER: DELETED {inp} ON SITE")
            self.datatype_list.pop(self.dataname_list.index(inp))
            self.data_list.pop(self.dataname_list.index(inp))
            self.dataname_list.remove(inp)

    def MKD(self,data,name,file_type):
        #Server creates the directory specified in pathname at server site
        if name not in self.dataname_list:
            print(F"SERVER-SERVER: ADDED {name} TO SITE")
            self.data = data
            self.data_path = name
            #self.curr_datatype = file_type
            self.TYPE(None,file_type) #set to file type
            self.dataname_list.append(self.data_path)
            self.data_list.append(self.data)
            self.datatype_list.append(self.curr_datatype)
        else:
            print(F"SERVER-SERVER: REPLACED {name} TO SITE")
            self.data = data
            self.curr_datatype = file_type

    def LIST(self,arr):
        '''
        - Implied Type AN is used
        - Server sends list to the passive DTP
        - Server transfers list of files in the specified directory if the
          pathname specifies a directory or other group of files
        - Server sends current information on file if pathname
          specifies a file
        - Server accesses user’s current working directory or default
          directory if null argument is used with LIST
        '''
        if len(arr)%3 != 0: raise TypeError("LIST(): INVALID LIST")
        new_arr = arr
        while new_arr:
            #print(F"arr: {new_arr}")
            self.STOR(new_arr[0],new_arr[1],new_arr[2])
            new_arr.pop(0); new_arr.pop(0); new_arr.pop(0)

    def STAT(self):
        '''
        - Server sends the status response over the control connection in the form of a reply
            - Telnet IP and Synch signals are included
            - Server responds with the status of the operation in progress
        - STAT can be sent between file transfers
            - If a partial pathname is given, server responds with list of
              file names or attributes associated with the pathname specification
            - If no argument is given, server returns general status
              information about the server FP process
            - General status information includes current values of all
              transfer parameters and the status of connections
        '''
        if not self.fpSuppressReplyText: return

        if self.mode: print(F"SERVER-USER: STATUS: IN TRANSMISSION;\n{self.data_path}")
        else: print("SERVER-USER: STATUS: NOT CURRENTLY IN TRANSMISSION")

    def SITE(self):
        #blank on the list of cmd explanation, bruh
        print("[[[Service commands: Description missing from released Document]]]")

    def ACCT(self):
        #Access control command
        #never described
        print("[[[Access control command: Description missing from released Document]]]")

    def CDUP(self):
        #Access control command
        #never described
        print("[[[Access control command: Description missing from released Document]]]")

    def NLST(self):
        #Service command
        #never described
        print("[[[Description missing from released Document]]]")

    #xml like
    def ARST(self):
        #the autorestart protocol command (ARST) shall be used to enable autorestart at the server-FP;
        #Server turn on its autorestart flag
        #ARST <CRLF>
        self.autorestart = True
        return

    def BETS(self):
        '''
        ENABLE BEST EFFORT TRANSPORT SERVICE OPTION (BETS):
        NOTE – The BETS command is practicable only when SCPS-TP (reference [4])
        provides the underlying transport service.
        – The BETS command shall cause the server-FP to set the MIB parameter
        fpBETSEnabled to ‘TRUE’ (enabled) and save the BETS fill code to use during a
        file transfer, if supplied, in the MIB parameter fpBETSFillChar.
        – While the BETS option is enabled,
        • the sending FP shall request the SCPS-TP to run in BETS mode for RETR and
        STOR operations;
        • the receiving FP/TP shall accept BETS-mode operation.
        – The receiving FP shall inform the user of any gaps in the data and fill the gaps
        with the BETS fill code contained in the MIB parameter fpBETSFillChar.
        – BETS shall be applied to RETR and STOR operations only.
        '''
        #Server turns on its BETS flag
        #Server saves BETS fill code to use during the file transfer
        #BETS <BETS-fill-code> <CRLF>
        self.flag_BETS = True
        return

    def COPY(self,filename1,filename2):
        #COPY
        '''
        The COPY command shall cause the server-FP to copy the file specified in the
        first pathname (argument 1) to the file specified in the second pathname
        (argument 2).
        – The server-FP shall report the success or failure of the copy in a reply.
        '''
        #COPY <SP> <pathname> <SP> <pathname> <CRLF>
        if filename1 == filename2: raise TypeError("CANNOT DUPLICATE TO SAME FILE LOCATION")

        ind = self.dataname_list.index(filename1)
        self.UPDT(self.data_list[ind],filename2,self.datatype_list[ind])

        return

    def IDLE(self, inp):
        #IDLE TIMEOUT
        '''
        The IDLE command shall cause the server-DTP to set the MIB parameter
        fpIdleTimeout to the value specified by the user.
        – If the server is inactive for this idle timeout period, the server-FP shall terminate
        the process and close the control connection.
        '''
        #IDLE <SP> <decimal-integer> <CRLF>
        time.sleep(inp)
        return

    def INTR(self):
        #MANUAL INTERRUPT
        '''
        – The INTR command shall cause the server-DTP to interrupt a file transfer.
        – The server-FP shall communicate the point of interrupt to the user-FP via reply
        message and code.
        '''
        '''
        There are three cases for SCPS-FP interrupt in all modes.
        a) user-to-server transfer:
            1) the user-FP shall send ‘INTR’ to the server-FP;
            2) in response, the server-FP shall stop the file transfer and send ‘256 Transfer
            Interrupted at rrrr’ to the user-FP, where rrrr is the size of the file stored locally at
            the server;
            3) the user-FP shall save the restart marker rrrr for restart;
            4) the user-FP may reinitiate the transfer process by repositioning its local file
            system using restart marker rrrr and sending ‘REST rrrr’ to the server-FP;
        b) server-to-user transfer:
            1) the user-FP shall send ‘INTR’ to the server-FP;
            2) the server-FP shall stop the file transfer and send ‘256 Transfer Interrupted at ssss’
            to the user-FP;
            3) the user-FP shall ignore the restart marker specified in the INTR reply;
            4) the user-FP may reinitiate the transfer process by sending ‘REST rrrr’ to the server-FP,
            where rrrr is the amount of data received and stored successfully at the user site;
        c) server-to-server (‘third-party’) transfer:
            1) the user-FP shall send ‘INTR’ to the sending server-FP;
            2) the sending server-FP shall stop the file transmission and send ‘256 Transfer
            Interrupted at ssss’ to the user-FP;
            3) the user-FP shall send ‘INTR’ to the receiving server-FP:
            – the user-FP should wait for the sending server-FP to respond with the 256
            reply before sending ‘INTR’ to the receiving server-FP;
            – if the sending server-FP responds with a code other than 256 (e.g., 226 - file
            transfer was completed before interrupt received), then the file transfer should
            continue as it normally would in response to the received reply code;
            4) in response to ‘INTR’, the receiving server-FP shall stop the file transfer process
            and send ‘256 Transfer Interrupted at rrrr’ to the user-FP;
            5) the user-FP shall ignore the restart marker in the sending server-FP’s reply and
            use the restart marker in the receiving server-FP’s reply when issuing the REST
            command;
            6) the user-FP may reinitiate the transfer process by sending ‘REST rrrr’ to the
            receiving server-FP and sending server-FP.
        '''
        #INTR <CRLF>
        if self.abort != 2:
            self.abort = 2
        else:
            self.abort = 0

    def NARS(self):
        #the no-autorestart protocol command (NARS) shall be used to disable autorestart at the server-FP.
        #Server turn off its autorestart flag
        #NARS <CRLF>
        self.autorestart = False
        return

    def NBES(self):
        '''
        DISABLE BEST EFFORT TRANSPORT SERVICE OPTION (NBES):
        – The NBES command shall cause the server-FP to set the MIB parameter
        fpBETSEnabled to ‘FALSE’ (disabled).
        – While the BETS option is disabled,
        • the sending FP shall not request BETS-mode operation;
        • the receiving FP/TP shall not accept BETS-mode operation.
        '''
        #Server turn off its BETS flag
        #NBES <CRLF>
        self.flag_BETS = False
        return

    def NSUP(self):
        #DO NOT SUPPRESS REPLY TEXT
        '''
        The NSUP command shall cause the server-FP to set the MIB parameter
        fpSuppressReplyText to ‘FALSE’ (disabled).
        – While suppression is disabled, all replies, including that in response to NSUP,
        shall have the text included in the reply.
        '''
        #NSUP <CRLF>
        self.fpSuppressReplyText = False

    def READ(self,data,filename,filetype,forced_TO=False):
        #RECORD READ
        '''
        1) User operations for the READ command are as follows:
            – the user-DTP shall create a control file as specified in 3.4.2.2;
            – the user-DTP shall then transfer the control file to the server-DTP using the
            STOR command;
            – after transferring the control file, the user-DTP shall issue the READ
            command, passing the remote control-file name as the argument;
            – if the user has specified the forced read option in the user command, the userFP shall transmit an enabled forced read option flag to the server-FP via the
            control data;
            – if the user has not specified the forced read option in the user command, the
            user-FP shall transmit a disabled forced read option flag to the server-FP via
            the control data.
        2) The READ command shall cause the server-DTP to transfer one or more records
        within a remote source file to the user-DTP or receiving server-DTP:
            – if the remote source file that is specified in the control data exists at the server,
            the records identified by the record IDs in the control data shall be transferred
            and stored locally at the user-DTP or receiving server-DTP;
            – the forced read option shall be executed if the user has specified this option in
            the record read user command;
            – the status and contents of the file at the server site shall be unaffected by the
            record read service.
        3) If the forced read option is enabled and either the user-FP or the server-FP
        encounters a recoverable error, each shall continue the read processing until the
        read transfer is deemed completed or an irrecoverable error occurs.
        4) For file structure a record shall be retrieved based on its position in the file
        relative to the start of the file.
        5) For CCSDS Packet structure a record shall be retrieved based on the value of the
        CCSDS Packet Sequence Count in the record rather than on its relative position in
        the file.
        '''
        #READ <SP> <pathname> <CRLF>
        #STOR part of file,then STOR other half
        #use UPDT for other half actually cause easier

        """
        print(b[0:int(math.floor(len(b)/2))])
        print(b[int(math.floor(len(b)/2)):])
        """
        self.STOR(data[:int(math.floor(len(data)/2))]  ,filename,filetype,forced_TO)
        self.STOR(data[int(math.floor(len(data)/2)):]  ,filename+"_READt",filetype,forced_TO)
        #combining data
        ind = self.dataname_list.index(filename)
        self.data_list[ind] = self.data_list[ind]+self.data_list[ind+1]

        self.RMD(filename+"_READt",False)

    def SIZE(self,file,console=True,verbose=False):
        #SIZE
        '''
        – The SIZE command shall cause the server-FP to send the size of the file specified
        in the pathname to the user-FP.
        – The server-FP shall communicate the size of the file via the reply message and
        code.
        '''
        #SIZE <SP> <pathname> <CRLF>

        if (file not in self.dataname_list) and file != "curr": raise TypeError("FILE NOT FOUND")

        ty = self.TYPE(file,None,True)    #return filetype
        if verbose: print(F"Type: {ty}")
        if ty == "IMAGE" or ty == "ASCII" or ty == "PACKET":
            if console:
                return sys.getsizeof(self.data_list[self.dataname_list.index(file)])
            else:
                return sys.getsizeof(file)
        else:   #None
            if verbose: print("MINOR ERROR: SIZE(): TYPE = NONE")
            return 0

    def SUPP(self):
        #SUPPRESS REPLY TEXT
        '''
        The SUPP command shall cause the server-FP to set the MIB parameter
        fpSuppressReplyText to ‘TRUE’ (enabled).
        '''
        #SUPP <CRLF>
        self.fpSuppressReplyText = True

    def UPDT(self,data,filename,filetype,forced_TO=False):
        #RECORD UPDATE
        '''
        1) User operations for the UPDT command are as follows:
            – prior to issuing the UPDT command to the server-FP, the user-FP shall
            • compute a checksum against a local copy of the remote file;
            • test the update request against the same file;
            – the user-DTP shall create a control file as specified in 3.4.2.2, containing the
            remote file names, the local checksum, and the update signals;
            – the user-DTP shall transfer the control file to the server-DTP using the STOR
            command;
            – the user-DTP shall issue the UPDT command passing the remote control-file
            name as the argument.
        2) The UPDT command shall cause the server-DTP to accept record update data
        transferred via the control data and apply it to a remote target file:
            – the record update data, as specified in 3.4.2.2, shall consist of a series of
            signals that indicate which records to delete and modify in the remote file and
            where to add new records;
            – if the remote file specified in the control data exists at the server,
            • the server-FP first shall verify that the remote target file is the correct file
            to modify by comparing the remote file’s checksum with that provided in
            the control data;
            • on checksum mismatch, the server-FP shall notify the user-FP of the
            mismatch via standard reply means;
            – if the remote file to be created already exists at the server, the server-FP shall
            issue a ‘550 File Action Not Taken, File Already Exists’ reply to the user-FP;
            – upon verifying that the target file exists and is the correct file, and that the file
            to be created does not already exist, the server-FP shall apply the update
            signals to a copy of the remote file and store the revised data at the server-FP
            in a new file.
        3) For file structure a record shall be accessed based on its position in the file
        relative to the start of the file.
        4) For CCSDS Packet structure a record shall be accessed based on the value of the
        CCSDS Packet Sequence Count in the record rather than on its relative position in
        the file
        '''
        #UPDT <SP> <pathname> <CRLF>
        #not in: STOR
        if filename not in self.dataname_list:
            if not self.fpSuppressReplyText: print(F'SERVER-USER: {filename} DOESNT EXIST')
            print('USER-USER: SENDING FILE TO SERVER NOW')
            self.STOR(data,filename,filetype,forced_TO)
        #already exists: RMD then STOR
        else:
            if not self.fpSuppressReplyText: print(F'SERVER-USER: {filename} ALREADY EXIST')
            print('USER-USER: UPDATING FILE ON SERVER NOW')
            self.RMD(filename)
            self.STOR(data, filename, filetype, forced_TO)

        return

    def HELP(self,cmd=None):
        '''
        - Server sends help information over the control connection
        - If an argument is provided (e.g., a command), more detailed information is provided as the response
        '''
        if not cmd: #HELP
            self.cmd_ex()
            return

        #HELP _CMD_
        if cmd == "STRU":
            print(F"{cmd}: User-Console Command to log structure of Data Packet;\nNot Accessable by console")
        elif cmd == "TYPE":
            print(F"{cmd}: Return or Set filetype of file given its name;\nSee HELP for more details/uses")
        elif cmd == "STOR":
            print(F"{cmd}: Store File;\nGiven file, filename, and filetype;\nSee HELP for more details/uses")
        elif cmd == "RETR":
            print(F"{cmd}: Server-Console Command to log restart marker;\nNot Accessable by console")
        elif cmd == "PROXY":
            print(F"{cmd}: Depreciated for this sim: absorbed into STOR")
        elif cmd == "REST":
            print(F"{cmd}: User-Console Command to log restart marker;\nNot Accessable by console")
        elif cmd == "USER":
            print(F"{cmd}: Not actually command, but rather a console var replaced with the CMD you put in.\nEx: READ,STOR,TYPE,etc")
        elif cmd == "PASS":
            print(F"{cmd}: Enter Password for access to a Server;\nMust be following CWD Command;\nOnly 1 Server aHELvaliable with Password: ECE1150;\nSee HELP CWD")
        elif cmd == "CWD":
            print(F"{cmd}: Save Password for access to a Server;\nIn real life, PASS _password_ would follow every CMD and it's ARG unless CWD saved it;\nChanged for this sim")
        elif cmd == "QUIT":
            print(F"{cmd}: Log out of Server")
        elif cmd == "PORT":
            print(F"{cmd}: User-to-Server-Console Command that sends IP for stream mode for each transfer;\nNot Accessable by console")
        elif cmd == "PASV":
            print(F"{cmd}: User-to-Server-Console Command that requests IP of Server for each transfer;\nNot Accessable by console")
        elif cmd == "MODE":
            print(F"{cmd}: User-Console Command to toggle if it transmittion;\nNot Accessable by console")
        elif cmd == "RNFR":
            print(F"{cmd}: Service command: Description missing from released Document")
        elif cmd == "RNTO":
            print(F"{cmd}: Service command: Description missing from released Document")
        elif cmd == "ABOR":
            print(F"{cmd}: Set ABORT Flag for STOR operation;\nSee HELP for more details/uses")
        elif cmd == "DELE":
            print(F"{cmd}: User-to-Server-Console Command to remove a file;\nGiven filename")
        elif cmd == "RMD":
            print(F"{cmd}: Server-Console Command to remove a file;\nNot Accessable by console")
        elif cmd == "MKD":
            print(F"{cmd}: Server-Console Command to add a file;\nNot Accessable by console")
        elif cmd == "LIST":
            print(F"{cmd}: Store multiple files in one command;\nGiven file, filename, and filetype;\nSee HELP for more details/uses")
        elif cmd == "STAT":
            print(F"{cmd}: Server-to-User-Console Command to check if the server is already transmitting;\n"
                  F"Normally can be used between file transfers,\nwhich would thent he server would give list of currently transmitted file names;\n"
                  F"However due to the unability to wait apporpriately to a seperate simualted server;\n\n"
                  F"Both outcomes of command exists in code but you are unable to see the effect during transmittion")
        elif cmd == "SITE":
            print(F"{cmd}: Service commands: Description missing from released Document")
        elif cmd == "ACCT":
            print(F"{cmd}: Access control command: Description missing from released Document")
        elif cmd == "CDUP":
            print(F"{cmd}: Access control command: Description missing from released Document")
        elif cmd == "NLST":
            print(F"{cmd}: Description missing from released Document")
        elif cmd == "ARST":
            print(F"{cmd}: User-Console command to turn on its autorestart flag")
        elif cmd == "BETS":
            print(F"{cmd}: User-Console command to turn on its BETS flag")
        elif cmd == "COPY":
            print(F"{cmd}: Copy contents of one filename into another;\nGiven filename1(copy data from), filename2(copy data to);\nSee HELP for more details/uses")
        elif cmd == "IDLE":
            print(F"{cmd}: Have User-Console run idle by give time specified;\nEx: IDLE 0.5")
        elif cmd == "INTR":
            print(F"{cmd}: Set INTR Flag for STOR operation;\nSee HELP for more details/uses")
        elif cmd == "NARS":
            print(F"{cmd}: User-Console command to turn off its autorestart flag")
        elif cmd == "NBES":
            print(F"{cmd}: User-Console command to turn off its BETS flag")
        elif cmd == "NSUP":
            print(F"{cmd}: Unsuppress SERVER-USER Replies;\nfpSuppressReplyText = False")
        elif cmd == "READ":
            print(F"{cmd}: Store File;\nUploading one half of the data, then the other half;\nGiven file, filename, and filetype;\nSee HELP for more details/uses")
        elif cmd == "SIZE":
            print(F"{cmd}: Find size of file given its name; Ex: SIZE ./lol.txt")
        elif cmd == "SUPP":
            print(F"{cmd}: Suppress SERVER-USER Replies;\nfpSuppressReplyText = True")
        elif cmd == "UPDT":
            print(F"{cmd}: Store File;\nUpdating to the server duplicate filenames;\nGiven file, filename, and filetype;\nSee HELP for more details/uses")
        elif cmd == "HELP":
            print(F"{cmd}: Gives info on CMD's")
        elif cmd == "debug":
            print(F"{cmd}: List out class variables")
        else:
            print("ERROR: HELP: CMD NOT RECOGNIZED")
'''
funtions to add
ACCESS CONTROL COMMANDS: pg54
USER, PASS, CWD, ACCT, CDUP, QUIT.

TRANSFER PARAMETER COMMANDS: pg55
MODE, PORT, PASV, TYPE, STRU.

SCPS-FP SERVICE COMMANDS: pg56
RETR, STOR, RNFR, RNTO, ABOR, DELE, RMD, MKD, LIST, HELP, SITE, STAT,
PWD, STOU, SYST, NOOP, NLST, APPE.



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
    #put "True" inside FP's initializer for debug mode
        #debug mode: No graph, no passwords
    Feebee = FP(True)