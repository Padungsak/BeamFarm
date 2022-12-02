import webiopi
import datetime
import sys
import operator
sys.path.append('/home/pi/MyProject/python')
from engine import EngineImp
from WaterValve import WaterValveImp
import threading

GPIO = webiopi.GPIO

g_waterValveDict = {}

g_waterStateList = {'Open':1,'Close':0, 'Auto':3, 'Error':4}

g_waterState = g_waterStateList['Close']

#s_mcp0 = webiopi.deviceInstance("mcp0")
#s_mcp0.setFunction(10, GPIO.IN)
# setup function is automatically called at WebIOPi startup
def setup():
    l_test = 1

# loop function is repeatedly called by WebIOPi 
def loop():
    #if s_mcp0.digitalRead(10) == GPIO.HIGH:
    #    webiopi.debug("1")
    #else:
    #    webiopi.debug("0")
    webiopi.sleep(1)

# destroy function is called at WebIOPi shutdown
def destroy():
    global g_waterValveDict
    g_waterValveDict.clear()

#Add machine
@webiopi.macro
def InitialMachine(a_waterPumpGpioPort):
    EngineImp.getInstance().Initialization(int(a_waterPumpGpioPort))
        
#Add valve macro
@webiopi.macro
def AddWaterValve(a_valveName, a_valvePort, a_executionOrder):
    global g_waterValveDict
    if(a_valveName not in g_waterValveDict):
        g_waterValveDict[a_valveName] = WaterValveImp(a_valveName, int(a_valvePort), int(a_executionOrder))
    
#Open valve macro
@webiopi.macro
def OpenValve(a_valveName):
    #Open valve before start engine
    global g_waterState
    if(a_valveName in g_waterValveDict):
        g_waterValveDict[a_valveName].OpenValve()
        webiopi.sleep(0.5)
        EngineImp.getInstance().OpenWaterPump()
        g_waterState = g_waterStateList['Open']
        return g_waterValveDict[a_valveName].GetValveState()

    return WaterValveImp.m_valveStateList['Error']

#Close valve macro
@webiopi.macro
def CloseValve(a_valveName):
    #Short down engine before closing valve
    global g_waterState
    l_valveCount = 0
    for l_valveName, l_valveObj in g_waterValveDict.items():
        if(int(l_valveObj.GetValveState()) == WaterValveImp.m_valveStateList['Open']):
            l_valveCount = l_valveCount +1

    if(l_valveCount <= 1):
        EngineImp.getInstance().CloseWaterPump()
        g_waterState = g_waterStateList['Close']
    
    if(a_valveName in g_waterValveDict):
        g_waterValveDict[a_valveName].CloseValve()
        return g_waterValveDict[a_valveName].GetValveState()

    return WaterValveImp.m_valveStateList['Error']
        
@webiopi.macro
def GetValveState(a_valveName):
    if(a_valveName in g_waterValveDict):
        return "%d" % g_waterValveDict[a_valveName].GetValveState()

@webiopi.macro
def ExecutionAuto(a_delayTime, a_startOrder):
    #constRate = ConstantRate()
    #constRate.UpdateValue()
    ourThread = threading.Thread(target=DoExecutionAuto, args=[a_delayTime, a_startOrder])
    ourThread.start()
    
def DoExecutionAuto(a_delayTime, a_startOrder):
    global g_waterState
    g_waterState = g_waterStateList['Auto']
    
    for l_valveName, l_valveObj in g_waterValveDict.items():
        l_valveObj.CloseValve()
        webiopi.sleep(0.5)
        if(int(l_valveObj.GetValveState()) == WaterValveImp.m_valveStateList['Error']):
            EngineImp.getInstance().CloseWaterPump()
            g_waterState = g_waterStateList['Error']
            return False
                
    l_orderIndex = int(a_startOrder)
    l_isFound = True
    while l_isFound:
        l_isFound = False
        for l_valveName, l_valveObj in g_waterValveDict.items():
            if(l_valveObj.executionOrder == l_orderIndex):
                l_valveObj.OpenValve()
                webiopi.sleep(0.5)
                if(int(l_valveObj.GetValveState()) == WaterValveImp.m_valveStateList['Error']):
                    EngineImp.getInstance().CloseWaterPump()
                    g_waterState = g_waterStateList['Error']
                    return False
                l_isFound = True
        
        if(l_isFound):
            webiopi.debug('Auto mode found execution!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            l_previousOrderIndex = l_orderIndex - 1
            for l_valveName, l_valveObj in g_waterValveDict.items():
                if(l_valveObj.executionOrder == l_previousOrderIndex):
                    webiopi.sleep(3)
                    l_valveObj.CloseValve()
                    webiopi.sleep(0.5)
                    if(int(l_valveObj.GetValveState()) == WaterValveImp.m_valveStateList['Error']):
                        EngineImp.getInstance().CloseWaterPump()
                        g_waterState = g_waterStateList['Error']
                        return False
                    
            EngineImp.getInstance().OpenWaterPump()
            webiopi.sleep(int(a_delayTime))
        else:
            webiopi.debug('Auto mode not found execution!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            EngineImp.getInstance().CloseWaterPump()

            l_previousOrderIndex = l_orderIndex - 1
            for l_valveName, l_valveObj in g_waterValveDict.items():
                if(l_valveObj.executionOrder == l_previousOrderIndex):
                    l_valveObj.CloseValve()
                    webiopi.sleep(0.5)
            
            g_waterState = g_waterStateList['Close']
            return True

        l_orderIndex = l_orderIndex + 1


@webiopi.macro
def IsAutoModeRunning():
    return (g_waterState == g_waterStateList['Auto'])

@webiopi.macro
def IsMachineOpennig():
    return (g_waterState == g_waterStateList['Open'])

@webiopi.macro
def IsMachineClosing():
    return (g_waterState == g_waterStateList['Close'])

@webiopi.macro
def IsAutoModeError():
    return (g_waterState == g_waterStateList['Error'])



@webiopi.macro
def StopWaterPump():
    global g_waterState
    EngineImp.getInstance().CloseWaterPump()
    if(g_waterState != g_waterStateList['Auto']):
        g_waterState = g_waterStateList['Close']

    

