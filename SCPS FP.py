'''
In this report, we are assessing two things
Ability to conduct independent research, organize information and cite appropriate sources
Ability to apply knowledge gained to an engineering problem.
    This is through simulating (at least part of) the system and demonstrating how you set up the simulation and why,
    and analyzing the observations from the simulation in a clear way.
    The observations from the simulation should reflect the theory.
    You can use any information in the course in addition to what you learned independently.
'''

#TOD0: graph out nodes as different things in space station that would need the internet and how they would be connected
    #involves more research

try:
    import math
    import networkx as nx
    import matplotlib.pyplot as plt
    import numpy as np
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
class FP():
    def __init__(self):
        #https://web.archive.org/web/20130423142305/http://public.ccsds.org/publications/archive/717x0b1s.pdf
        print("init")
        self.G = nx.Graph()
        self.stream_mode = False
        self.curr_datatype = None

        #datatypes
        self.IMAGE = None
        self.ASCII = ""
        self.file = None
        self.packet = []

    def testGraph(self):
        self.G.add_nodes_from(
            [(1, {"color": "red"}),
             (2, {"color": "green"})])
        self.G.add_edge(1, 2)
        nx.draw(self.G, node_color=['red','blue'], with_labels=True)
        #nx.draw(self.G, with_labels=True, font_weight='bold')
        plt.show()

    def matplot_test(self):
        self.G = nx.petersen_graph()
        subax1 = plt.subplot(121)
        nx.draw(self.G, with_labels=True, font_weight='bold')
        subax2 = plt.subplot(122)
        nx.draw_shell(self.G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
        plt.show()

    def restart(self):
        return

    def STRU(self):
        return

    def TYPE(self):
        return self.curr_datatype

    def STOR(self):
        '''
        user-to-server transfer (e.g., STOR):
        1) the user-FP shall send ‘SIZE pathname’ to the receiving server-FP;
        2) the server-FP shall send ‘213 pathname SIZE rrrr’ to the user-FP, where rrrr is the
        size of the file (indicated by pathname) stored locally at the server;
        3) to restart the transfer, the user-FP shall reposition its local file system using restart
        marker rrrr and send the command ‘REST rrrr’ to the server-FP;
        4) the server-FP shall save restart marker rrrr for restart;
        '''
        return

    def RETR(self):
        '''
        1) the user-FP shall determine the size (rrrr) of the file as stored by the local file system;
        2) to restart the transfer, the user-FP shall reposition its local file system using restart
        marker rrrr and send the command ‘REST rrrr’ to the server-FP;
        3) the server-FP shall save restart marker rrrr for restart;
        '''
        return

    def PROXY(self):
        return

    def INTR(self):
        return

    def REST(self):
        return

'''
funtions to add
USER
PASS
CWD
QUIT
PORT
PASV
TYPE
STRU
MODE
RETR
STOR
RNFR
RNTO
REST
ABOR
DELE
RMD
MKD
LIST
STAT
SITE
ACCT
CDUP
NLST
NOOP
PWD
STOU
SYST
APPE
HELP

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
    Feebee = FP()
    Feebee.testGraph()
    #Feebee.matplot_test()

    while True:
        inp = input("command:")
        #pass command to FP