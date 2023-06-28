import pyvisa, time

class DMM7510:
    
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.tempbufferName = ""
        self.tempbuffSize = 0
        self.current_function = ""
        #self.dynamicState()
        #self.CCstate()
        #self.CRstate()
        #self.expState()
        #self.seqState()
        #self.ABState()
        #self.mode = 'CCL'
        #self.chnl = 'CHAN 1'
        #self.setStringA = ""
        #self.setStringB = ""

    def list_ports(self):
        self.port_list = self.rm.list_resources()
        return(self.port_list)
    
    def connect(self,port_name,baudrate=9600):
        try:
            self.instrVISA = self.rm.open_resource(port_name)
            self.instrVISA.baud_rate = baudrate
            self.response = ""
        except:
            None
        print('connected')
        
    def disconnect(self):
        self.Write_command('logout')
        print(self.Query_command(':SYST:ACC?'))
        try:
            self.instrVISA.close()
        except:
            None
            
    def fulldisconnect(self):
        self.disconnect()
        try:
            self.rm.close()
        except:
            None
        
#----------------------------------------General Write read command------------------------------------
    def Query_command(self,command):
        self.response=self.instrVISA.query(command)
        #print("Query command = ",self.instrVISA.query(command)) #[Debug only]
        return self.response

    def Write_command(self,command):
        try:
            self.instrVISA.write(command)
        except:
            None
        print("Write command =", command) #[Debug only]

#-----------------------------------------------Set command--------------------------------------------
    #bypass is used for setting when sequence is used.
    #1 = no bypass command
    #0 = bypass the command

    def digitize_curr(self):
        self.Write_command(':SENS:DIG:FUNC "CURR"')

    def digitize_volt(self):
        self.Write_command(':SENS:DIG:FUNC "VOLT"')

    def meas_curr(self):
        self.Write_command(':SENSE:FUNC "CURR" ')

    def meas_volt(self):
        self.Write_command(':SENSE:FUNC "VOLT" ')
        
    def del_buffer(self,buffName):
        self.Write_command(':TRACe:DEL "%s"' % buffName)

    def clr_buffer(self,buffName=""):
        if buffName == "":
            self.Write_command(':TRAC:CLE')
        else:
            self.Write_command(':TRAC:CLE "%s"' % bufferName)
            
    def set_measure_count(self,count):
        self.Write_command(":DIG:COUN %d" % count)

    def set_buffer(self,buffName,buffSize):
        self.Write_command('TRACe:MAKE "%s", %d' %(buffName, buffSize))
        self.tempbufferName = buffName
        self.tempbuffSize = buffSize
        print(buffName,buffSize)

    def set_sampling_rate(self,func,rate): #for digitize only
        
        if self.get_current_function() == "NONE":
            print("Sampling rate not set for non digitize function")    
        else:
            self.Write_command(':DIG:%s:SRATE %d' %(func,rate))

    def set_buffer_points(self,points,bufferName=""):
        if bufferName == "":
            self.Write_command(':TRAC:POIN %d' % points)
        else:
            self.Write_command(':TRAC:POIN %d, "%s"' % (points,bufferName))

    def start_meas(self,type="",bufferName="",func="",timestamp=0,unit=0):
        #reference - :MEAS:<function>? <buffername>, <bufferele1>, <bufferele2>
        #MEAS can operate without defining function
        self.base_string = ':MEAS'
        if func != "":
            self.base_string = self.base_string + (':"%s"' % func)

        self.base_string = self.base_string + ('?')

        if bufferName != "":
            self.base_string = self.base_string + ('"%s"' % bufferName)
        else:
            self.base_string = self.base_string + ('"defbuffer1"')
                                                 
        if timestap != 0:
            self.base_string = self.base_string + (',TST')

        if unit != 0:
           self.base_string = self.base_string + (',UNIT') 
                                                                   
#---------------------------------------------Read command-----------------------------------------
    def get_current_function(self):
        func = self.Query_command(':FUNC?')
        func = self.Query_command(':FUNC?')
        print(func)
        if "NONE" in func:
            print("I'm here")
            func = self.Query_command(':DIG:FUNC?')
            print(func)
            return func
        else:
            func = func.split(':')
            func = func[0]+'"'
            self.current_function = func
            print(self.current_function)
            return func

    def get_buffer_function(self,bufferName=""):
        if bufferName == "":
            self.Write_command(':TRAC:POIN?' % points)
        else:
            self.Write_command(':TRAC:POIN? "%s"' % (points,bufferName))
        

#------------------------------------------Data holding function-----------------------------------
    def dynamicState(self,state=False):
        self.dynstate = state
        
    def CCstate(self,state=False):
        self.currstate = state
        
    def CRstate(self,state=False):
        self.resstate = state
        
    def expState(self,state=False):
        self.expstate = state
        
    def seqState(self,state=False):
        self.seqstate = state
        
    def ABState(self,state='A'):
        self.ABstate = state

        


# ELOAD = ELOAD()
# ELOAD.connect("ASRL91::INSTR")
# ELOAD.set_channel('CHAN 1',1)
# ELOAD.set_mode('CV',1)
# ELOAD.ABState('B')
# ELOAD.set_load_val('CV',3,2)
# #ELOAD.Write_command("CURR:STAT:L1 2;L2 2")
# ELOAD.fulldisconnect()
