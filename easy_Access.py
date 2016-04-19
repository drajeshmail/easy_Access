from Tkinter import *
import ttk
from ttk import Notebook
from ScrolledText import ScrolledText
from twisted.conch.insults.window import Border
import tkMessageBox
import paramiko
from imghdr import what

class easy_Access_GUI (Frame) :
    
    def __init__(self):
        self.config_file = "easy_Access_Config.bin"
        
        self.hostlist = []
        self.connections = {}
        self.statusLED_dict = {}
        self.activeServers = {"CMTS" : "CMTS1" , "SNMP" : "SNMP1"}
        
        self.readFromConfiguration(self.config_file)
        self.connect_servers( self.hostlist, "CMTS1")
        self.connect_servers( self.hostlist, "CMTS2")
        self.connect_servers( self.hostlist, "SNMP1")
        
        self.printDict(self.connections)
        
        self.frame = Tk()
        self.content = Frame( self.frame)
        self.tabbedFrame = Frame ( self.content ) 
        self.tabbed = Notebook( self.tabbedFrame, width = 500, height = 500)
          
        self.statusFrame = Frame ( self.content) 
        
        self.cmtsTab = Frame ( self.tabbed )
        self.snmpTab = Frame ( self.tabbed )
        
      
        self.tabbed.add ( self.cmtsTab, text = "CMTS")
        self.tabbed.add ( self.snmpTab, text = "SNMP")
        
        
        #####CMTS TAB items 
        self.CMTSMacaddrFrame = LabelFrame ( self.cmtsTab, text = " Enter the MAC addr of the GW")
        self.CMTSConfigureFrame    = LabelFrame ( self.cmtsTab, text = "Configure CMTS")
        self.CMTSSubmitFrame       = Frame ( self.cmtsTab)
        self.CMTSScrolledTextFrame = LabelFrame ( self.cmtsTab, text = "Output from CMTS")
        
        ####$ Status Frame Items
        self.connCMTS1_Stat = Canvas ( self.statusFrame, height = 20, width = 20) 
        self.connCMTS1_Label = Label ( self.statusFrame, text = " CMTS1 ")
        self.statusLED_dict["CMTS1"] = self.connCMTS1_Stat 
        self.connCMTS2_Stat = Canvas ( self.statusFrame, height = 20, width = 20) 
        self.connCMTS2_Label = Label ( self.statusFrame, text = " CMTS2 ")
        self.statusLED_dict["CMTS2"] = self.connCMTS2_Stat
        self.connSNMP_Stat = Canvas ( self.statusFrame, height = 20, width = 20)
        self.connSNMP_Label = Label ( self.statusFrame, text = " SNMP ")
        self.statusLED_dict["SNMP1"] = self.connSNMP_Stat
        
        ####CMTS Tab Items
  
        
        valMacEntry = (self.frame.register(self.onValidate),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.macAddr_entry = Entry ( self.CMTSMacaddrFrame , validate = 'focus' , validatecommand = valMacEntry)
        self.cmtsTabSubmit = Button ( self.CMTSSubmitFrame, text = "Submit", command = lambda:self.cmtsTabButtonSubmit())
        self.resultFromCMTS_text = ScrolledText ( self.CMTSScrolledTextFrame, width = 65)
        
        self.CMTSSelectVal =  StringVar()
        self.CMTSSelectVal.set("CMTS1")
        self.CMTS1Radio    =  Radiobutton(self.CMTSConfigureFrame, text = "CMTS1", variable = self.CMTSSelectVal, value = "CMTS1", command = lambda : self.setActiveServer("CMTS", self.CMTSSelectVal.get()))
        self.CMTS2Radio    =  Radiobutton(self.CMTSConfigureFrame, text = "CMTS2", variable = self.CMTSSelectVal, value = "CMTS2", command = lambda : self.setActiveServer("CMTS", self.CMTSSelectVal.get()))
        self.CMTSConfigureButton = Button ( self.CMTSConfigureFrame, text = "Configure")

        for led in self.statusLED_dict:
          self.status = self.statusLED_dict[led].create_oval(10,10,20,20, fill = "red" )
        
        #self.status = self.connCMTS1_Stat.create_oval(10,10,20,20, fill = "red" )
        #self.status = self.connCMTS2_Stat.create_oval(10,10,20,20, fill = "red" )
        #self.status = self.connSNMP_Stat.create_oval(10,10,20,20, fill = "red" )
        
        #####SNMP TAB items
        self.SNMPInterfaceFrame = LabelFrame ( self.snmpTab, text = "Interface", padx = 10, pady = 10)
        self.SNMPFuntionFrame   = LabelFrame ( self.snmpTab, text = "SNMP Function", padx = 10, pady = 10)
        self.SNMPCommunityStringFrame = LabelFrame ( self.snmpTab, text = "Community String", padx = 10, pady = 10)
        self.SNMPScrolledTextFrame = LabelFrame ( self.snmpTab , text = "SNMP Output", padx = 10, pady = 10)
        
        #####SNMPInterfaceFrame
        self.SNMPIFCMVal = StringVar()
        self.SNMPIFCMVal.set("MTA")
        self.SNMPIFCM_Radiobutton = Radiobutton(self.SNMPInterfaceFrame, text = "CM", variable = self.SNMPIFCMVal, value = "CM")
        self.SNMPIFMTA_Radiobutton = Radiobutton(self.SNMPInterfaceFrame, text = "MTA", variable = self.SNMPIFCMVal, value = "MTA")
        self.SNMPIFCM_entry = Entry ( self.SNMPInterfaceFrame)
        self.SNMPIFMTA_entry= Entry ( self.SNMPInterfaceFrame)
        
        #####SNMPFuntionFrame
        self.snmpFuncVal = StringVar()
        self.snmpFuncVal.set("snmpwalk")
        self.SNMPgetradio = Radiobutton ( self.SNMPFuntionFrame, text = 'SNMPSET', variable = self.snmpFuncVal, value = "snmpset")
        self.SNMPwalkradio = Radiobutton ( self.SNMPFuntionFrame, text = "SNMPWALK", variable = self.snmpFuncVal, value = "snmpwalk")
        
        #####SNMPCommunityStringFrame
        self.SNMPCSentryState = ['disabled','disabled', 'normal']
        self.snmpCSVal = IntVar()

        self.snmpCSVal.set(1)
        self.SNMPCSCustomEntry = Entry ( self.SNMPCommunityStringFrame, state = self.SNMPCSentryState[self.snmpCSVal.get()])
        self.SNMPCSPublic = Radiobutton ( self.SNMPCommunityStringFrame, text = 'PUBLIC', variable = self.snmpCSVal, value = 0, command = lambda:self.changedSNMPCS())
        self.SNMPCSPrivate = Radiobutton ( self.SNMPCommunityStringFrame, text = "PRIVATE", variable = self.snmpCSVal, value = 1, command = lambda:self.changedSNMPCS())
        self.SNMPCSCustom = Radiobutton ( self.SNMPCommunityStringFrame, text = "CUSTOM", variable = self.snmpCSVal, value = 2, command = lambda:self.changedSNMPCS())
        self.SNMPCSCustomEntry = Entry ( self.SNMPCommunityStringFrame, state = self.SNMPCSentryState[self.snmpCSVal.get()])
        #self.snmpCSVal.trace("w", self.changedSNMPCS())
        print  self.SNMPCSentryState[self.snmpCSVal.get()]
        
        ####SNMPScrolledText
        self.resultFromSNMP_text = ScrolledText ( self.SNMPScrolledTextFrame)
                
        
        self.content.pack() 
        self.tabbedFrame.pack()
        self.tabbed.pack()
        self.statusFrame.pack()
        
        self.CMTSMacaddrFrame.pack(fill = 'x', ipady = 5)
        self.CMTSConfigureFrame.pack( fill = 'x', ipady = 5)
        self.CMTSSubmitFrame.pack(fill = 'x')
        self.CMTSScrolledTextFrame.pack(fill = 'x')
        self.SNMPInterfaceFrame.pack(fill = 'x')
        self.SNMPFuntionFrame.pack(fill = 'x')
        self.SNMPCommunityStringFrame.pack( fill = 'x')
        self.SNMPScrolledTextFrame.pack( fill = 'x')
        
        self.connCMTS1_Stat.pack(side = LEFT )
        self.connCMTS1_Label.pack(side = LEFT)
        self.connCMTS2_Stat.pack(side = LEFT )
        self.connCMTS2_Label.pack(side = LEFT)
        self.connSNMP_Stat.pack(side = LEFT)
        self.connSNMP_Label.pack(side = LEFT)
        
        self.macAddr_entry.pack()
        self.cmtsTabSubmit.pack(ipadx = 30)
        self.resultFromCMTS_text.pack(fill = 'x', anchor = S )
        self.CMTS1Radio.pack(side = LEFT, padx = 30)
        self.CMTS2Radio.pack(side = LEFT, padx = 30)
        self.CMTSConfigureButton.pack(side=LEFT, padx = 30)
        
         
        self.SNMPIFCM_Radiobutton.pack( side = LEFT)
        self.SNMPIFCM_entry.pack( side = LEFT)
        self.SNMPIFMTA_Radiobutton.pack(side = LEFT)
        self.SNMPIFMTA_entry.pack(side = LEFT)
        
        self.SNMPgetradio.pack(side = LEFT , padx = 60)
        self.SNMPwalkradio.pack(side = LEFT , padx = 60)
        
        self.SNMPCSPrivate.pack(side = LEFT, padx = 10)
        self.SNMPCSPublic.pack(side = LEFT, padx = 20)
        self.SNMPCSCustom.pack(side = LEFT, padx= 20)
        self.SNMPCSCustomEntry.pack(side = LEFT)
        
        self.resultFromSNMP_text.pack ( side = LEFT)
        self.change_StatusLED()

        self.frame.update()
#        self.frame.mainloop()
        
        
    def change_StatusLED (self):
      for host, hostConnection in self.connections.items():
        if hostConnection != "FAILED":
          self.statusLED_dict[host].itemconfig( self.status, fill = "green")
        else:
          self.statusLED_dict[host].itemconfig( self.status, fill = "red")  
        
    #def cmtsTabButtonSubmit (self):  
        
    def readFromConfiguration (self, configFile):
        fileConfig = open( configFile, 'rw+')
        for line in fileConfig:
           hoststr = line.split("###")
           for singleHost in hoststr: 
             hostline = singleHost.split(",")
             print hostline
             self.hostlist.append(hostline)
        fileConfig.close()    
        
    def connect_servers(self, hostlist, hosttoConnect):
        for host in hostlist:
           if host[0] == hosttoConnect:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            try:
                client.connect(host[1], username=host[2], password=host[3])
            except :
                client = str ( "FAILED") 
                print sys.exc_info()[0]  
            self.connections[hosttoConnect] = client
            
    def printList (self , MyList):
        for i in MyList:
            print i 
            
    def printDict (self , dicttoPrint):      
        for connectName, connectStr in dicttoPrint.items():
           print connectName + "-->" + str(connectStr)
           
    def changedSNMPCS(self):
        self.SNMPCSCustomEntry.configure(state = self.SNMPCSentryState[self.snmpCSVal.get()])
        
    def setActiveServer(self, server, serverName):    
        self.activeServers[server] = serverName
        
   # def submitToCMTS(self):
    def onValidate ( self, d, i, P, s, S, v, V, W): 
        print self.resultFromCMTS_text.insert("end", "d=%s\n" % d) 
        print self.resultFromCMTS_text.insert("end", "i=%s\n" % i) 
        print self.resultFromCMTS_text.insert("end", "d=%s\n" % P) 
        print self.resultFromCMTS_text.insert("end", "d=%s\n" % s) 
        print self.resultFromCMTS_text.insert("end", "d=%s\n" % S)   
        print self.resultFromCMTS_text.insert("end", "d=%s\n" % v)  
        print self.resultFromCMTS_text.insert("end", "d=%s\n" % V)  
        print self.resultFromCMTS_text.insert("end", "d=%s\n" % W)  
              

           

               
    
if __name__ == '__main__' :
    c = easy_Access_GUI()
    c.frame.mainloop()
