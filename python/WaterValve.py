import webiopi
#from enum import Enum
import time,sys
sys.path.append('/home/pi/MyProject/python')

GPIO = webiopi.GPIO

class WaterValveImp:
    m_valveStateList = {'Open':1,'Close':0,'Error':2}
    
    def __init__(self, a_name, a_valvePort, a_executionOrder):
        webiopi.debug('WaterValveImp  was added')
        self.m_name = a_name
        self.m_valvePort = int(a_valvePort)
        self.executionOrder = int(a_executionOrder)
        GPIO.setFunction(self.m_valvePort, GPIO.OUT)
        GPIO.digitalWrite(self.m_valvePort, GPIO.HIGH)
        self.valveState = WaterValveImp.m_valveStateList['Close']
        #self.CloseValve()
        
    def OpenValve(self):
        webiopi.sleep(1)
        webiopi.debug('*******************************************OpenValve2 called %d' % self.m_valvePort)
        GPIO.digitalWrite(self.m_valvePort, GPIO.LOW)
        self.valveState = WaterValveImp.m_valveStateList['Open']

    def CloseValve(self):
        webiopi.sleep(1)
        webiopi.debug('CloseValve2 called')
        GPIO.digitalWrite(self.m_valvePort, GPIO.HIGH)
        self.valveState = WaterValveImp.m_valveStateList['Close']
        
    def GetValveState(self):
        return self.valveState
