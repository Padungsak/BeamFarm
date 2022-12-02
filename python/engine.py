import webiopi

GPIO = webiopi.GPIO

class EngineImp:

    s_instance = None
    
    @staticmethod
    def getInstance():
        if EngineImp.s_instance == None:
            EngineImp()
        return EngineImp.s_instance

        
    def __init__(self):
        if EngineImp.s_instance != None:
           raise Exception("This class is singleton Please call getInstance!")
        else:
           EngineImp.s_instance = self
        

    def Initialization(self, a_waterPumpGpioPort):
        self.m_waterPumpGpioPort = a_waterPumpGpioPort
        GPIO.setFunction(self.m_waterPumpGpioPort, GPIO.OUT)
        
        
    def OpenWaterPump(self):
        GPIO.digitalWrite(self.m_waterPumpGpioPort, GPIO.LOW)        

    def CloseWaterPump(self):
        GPIO.digitalWrite(self.m_waterPumpGpioPort, GPIO.HIGH)


        
