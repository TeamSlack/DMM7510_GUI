import pyvisa, time

class DMM7510:
    
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.tempbufferName = ""
        self.tempbuffSize = 0
        self.current_function = ""
        self.err_code_dict()
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
            self.instrVISA.write('*RST')
            self.instrVISA.write('*CLS')
        except:
            None
        print('connected')
        
    def disconnect(self):
        self.Write_command('logout')
        try:
            self.instrVISA.close()
            self.instrVISA.clear()
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
        try:
            self.response=self.instrVISA.query(command)
            self.response=self.instrVISA.query(command)
            #print("Query command = ",self.instrVISA.query(command)) #[Debug only]
            return self.response
        except:
            print("An event has occured on the DMM")
            self.ESR()


    def Write_command(self,command):
        try:
            self.instrVISA.write(command)
            self.ESR()
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

    def set_sampling_rate(self,rate): #for digitize only
        func = self.get_current_function()
        if func[1] == 'STD':
            print("Sampling rate not set for non digitize function")    
        else:
            print(':DIG:%s:SRATE %d' %(func[0],rate))
            #self.Write_command(':DIG:%s:SRATE %d' %(func[0],rate))
            
    def set_buffer_pts(self,points,bufferName=""):
        if bufferName == "":
            self.Write_command(':TRAC:POIN %d' % points)
        else:
            self.Write_command(':TRAC:POIN %d, "%s"' % (points,bufferName))

    def set_meas_pts(self,points):
        self.Write_command(':COUN %d' % points)

    def start_meas(self,func="",bufferName="",timestamp=0,unit=0):
        #reference - :MEAS:<function>? <buffername>, <bufferele1>, <bufferele2>
        #MEAS can operate without defining function
        self.base_string = ':MEAS'
        if func != "":
            self.base_string = self.base_string + (':%s' % func)

            self.base_string = self.base_string + ('?')

        if bufferName != "":
            self.base_string = self.base_string + ('"%s"' % bufferName)
        else:
            self.base_string = self.base_string + (' "defbuffer1"')
                                                 
        if timestamp != 0:
            self.base_string = self.base_string + (',TST')

        if unit != 0:
           self.base_string = self.base_string + (',UNIT')

        print(self.base_string)
        self.Write_command(self.base_string)
        
                                                                   
#---------------------------------------------Read command-----------------------------------------
    def get_current_function(self):
        #function to get the current measurement function used on the DMM
        func = self.Query_command(':FUNC?')
        func = self.Query_command(':FUNC?')
        #print(func)
        if "NONE" in func:
            func = self.Query_command(':DIG:FUNC?')
            func = func.strip()
            func = func.replace('"','')
            meas_type = 'DIG'
            #print(func)
        else:
            func = func.split(':')
            func = func[0]+'"'
            func = func.replace('"','')
            #self.current_function = func
            #print(self.current_function)
            meas_type = 'STD'
        return [func, meas_type]

    def get_active_buffer(self):
        #checks the current buffer used for the measurement
        buffer = self.Query_command(':DISPlay:BUFFer:ACTive?')
        #buffer = self.Query_command(':DISPlay:LIGHt:STATe?')
        return buffer

    def get_buffer_pts(self,bufferName=""):
        base_string = ':TRAC:POIN?'
        if bufferName != "":
            base_string = base_string + (' "%s"' % (bufferName))
        print(base_string) #debug only
        return (self.Query_command(base_string)).strip()

    def read_buffer_data(self,end_index=1,bufferName="",timestamp=0,unit=0):
        base_string = (':TRAC:DATA? 1,%d' % end_index)
        if bufferName != "":
            base_string = base_string + (', "%s"' % (bufferName))
        else:
            base_string = base_string + (', "defbuffer1"')

        if timestamp != 0:
            base_string = base_string + (',TST')

        if unit != 0:
           base_string = base_string + (',UNIT')
           
        print(base_string)
        buffer_data = self.Query_command(base_string)
        print(buffer_data)
        if len(buffer_data) < end_index:
            buffer_data = self.Query_command(base_string)
        return buffer_data
        

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

#------------------------------------------Error code----------------------------------------------
    def ESR(self):
        try:
            self.response = self.instrVISA.read()
        except:
            None
        self.response = self.instrVISA.query(':SYST:ERR:CODE?')
        self.response = (self.response).strip()
        if self.response != "0":
            print(self.response)
            if self.response in self.err_code:
                print(self.err_code[self.response])
            self.instrVISA.write(':SYST:CLE')
        
    def err_code_dict(self):
        self.err_code = {
            "4910":"No readings in buffer",
            "-113":"Undefined header"

        }


dmm = DMM7510()
dmm.connect('USB0::0x05E6::0x7510::04444208::INSTR')
func_array = dmm.get_current_function()

