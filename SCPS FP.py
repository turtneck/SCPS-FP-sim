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
        print("""
==============NOTICE==============
Some funcs arent theyre complete purpose as mandated"
in reports due to unability to wait apporpriately to another server."

Commands like these have instead been absorbed into others,"
still simulating the result between the two."

EX: ABOR becoming a set function that reacts with STOR"
instead of using ABOR in the middle of STOR's runtime"
==================================""")
        '''
        print("\n==============NOTICE=============="
              "\nSome funcs arent theyre complete purpose as mandated"
              "\nin reports due to unability to wait apporpriately to another server."
              "\n\nCommands like these have instead been absorbed into others,"
              "\nstill simulating the result between the two."
              "\n\nEX: ABOR becoming a set function that reacts with STOR"
              "\ninstead of using ABOR in the middle of STOR's runtime"
              "\n==================================")
          '''

        self.G = None
        self.add_colors=[]

        self.stream_mode = False
        self.autorestart = False    #0: AutoRest off, 1:AutoRest on
        self.abort = 0     #0:off, 1:ABOR, 2:INTR
                    #pg19 table
                    #TODO: STOR forcederror, ABOR, INTR, timeout; ARST, NARS

        #data
        self.curr_datatype = None
        self.data_path = None    #str ./__filename__
        self.data = None
        self.dataname_list = []
        self.partial_data = None

        #build and display ISS graph
        self.build_graph(not(debug))

        self.cmd_ex()
        self.main_loop()

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
            print("==================================")
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
                if len(arr) == 3:
                    self.STOR(arr[0],arr[1],arr[2])
                else:
                    self.STOR(arr[0],arr[1],arr[2],arr[3])
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
        print(
"""Examples:
STOR lol lol.txt ASCII      : send txt file

STOR lol lol.txt ASCII 1    : send txt file w/ timed-out transmittion

ABOR                        : send txt file w/ aborted transmittion
STOR lol lol.txt ASCII

INTR                        : send txt file w/ interupted transmittion
STOR lol lol.txt ASCII
""")

    #actual commands
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

    def STOR(self,data,name,type,forced_TO=False,recurrsion=False):
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
        self.data_path = "./" + name
        self.partial_data = data

        #random delay time take to send
        #if at 1(or over, means ACK didnt come
        d_temp = random.randint(0,99)
        print(F"[[waiting rand trans time: {d_temp/100}]]")
        time.sleep(d_temp/100) #random delay 0.0-1.0 time take to send

        #3&4.)
        #error in transmission
        while not d_temp or self.abort>0 or forced_TO: #1% chance error
            if not self.autorestart:
                #dest file didnt existed at start of transfer
                if "./"+name not in self.dataname_list:
                    if self.abort == 1 or not d_temp:  #ABOR/timeout
                        print("USER-USER: [DELETING PARTIAL FILE]")
                        self.partial_data = None
                    elif self.abort == 2: #INTR
                        print("USER-USER: [KEEPING PARTIAL FILE]")
                #dest file exist
                else:
                    if self.abort == 1 or not d_temp:  #ABOR/timeout
                        print("USER-USER: [RESTORING ORIGINAL FILE, DELETING PARTIAL FILE]")
                        self.partial_data = None
                    elif self.abort == 2: #INTR
                        print("USER-USER: [DELETING ORIGINAL FILE, KEEPING PARTIAL FILE]")
                        self.dataname_list.remove("./"+name)
            #auto rest
            else:
                if not d_temp:
                    if "./" + name not in self.dataname_list:  # dest file didnt existed at start of transfer
                        print("USER-USER: [KEEPING PARTIAL FILE]")
                    else:
                        print("USER-USER: [DELETING ORIGINAL FILE, KEEPING PARTIAL FILE]")
                        self.dataname_list.remove("./" + name)

            if self.abort == 1: #ABORT
                print("SERVER-USER: 226 [ABORT SUCCESSFUL, ABOR]")
                self.abort = 0
                return

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
            self.datalist.append(self.data_path)
            print(F"SERVER-USER: 213 {self.data_path} SIZE {self.SIZE()}")
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
        return

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
        #return user IP?
        return

    def PASS(self):
        '''
        - immediately preceded by user command
        - User-DTP hides sensitive password information
        '''
        return

    def CWD(self):
        '''
        - Server permits working with a different directory
        - Server preserves the user’s login/accounting information
        - Server preserves transfer parameter settings
        '''
        return

    def QUIT(self):
        '''
        - Server takes the effective action of an abort (ABOR) and a
        logout (QUIT) if an unexpected close occurs on the control connection
        '''
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
        #return some kinda port
        return

    def PASV(self):
        '''
        - Server-FP has implemented PASV
        - User-FP sends PASV per transfer
        '''
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
        self.abort = 1
        return

    def DELE(self):
        #delete
        '''
        - Server deletes file specified in the pathname at the server site
        - User-FP provides extra level of protection (‘do you really want to delete’)
        '''
        return

    #TODO:add to STOR :////
    def RMD(self):
        #Server removes directory specified in pathname from server site
        return

    def MKD(self):
        #Server creates the directory specified in pathname at server site
        return

    def LIST(self):
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
        #list files?
        return

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
        return

    def SITE(self):
        #blank on the list of cmd explanation, bruh
        return

    def ACCT(self):
        #Access control command
        #never described
        return

    def CDUP(self):
        #Access control command
        #never described
        return

    def NLST(self):
        #Service command
        #never described
        return

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
        return

    def COPY(self):
        #COPY
        '''
        The COPY command shall cause the server-FP to copy the file specified in the
        first pathname (argument 1) to the file specified in the second pathname
        (argument 2).
        – The server-FP shall report the success or failure of the copy in a reply.
        '''
        #COPY <SP> <pathname> <SP> <pathname> <CRLF>
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
        self.abort = 2
        return

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
        return

    def READ(self):
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
        return

    def SIZE(self,verbose=False):
        #SIZE
        '''
        – The SIZE command shall cause the server-FP to send the size of the file specified
        in the pathname to the user-FP.
        – The server-FP shall communicate the size of the file via the reply message and
        code.
        '''
        #SIZE <SP> <pathname> <CRLF>
        ty = self.TYPE()    #should just get the var but its part of the challenge
        if verbose: print(F"Type: {ty}")
        if ty == "IMAGE" or ty == "ASCII" or ty == "PACKET":
            return sys.getsizeof(self.data)
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
        return

    def UPDT(self):
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
        return

    def HELP(self):
        '''
        - Server sends help information over the control connection
        - If an argument is provided (e.g., a command), more detailed information is provided as the response
        '''
        #ughhhhhhhh
        return
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
    Feebee = FP(True)
    #Feebee.testGraph()
    #Feebee.matplot_test()