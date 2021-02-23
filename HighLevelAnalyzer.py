# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

SOH = 0x01
STX = 0x02
ETX = 0x03
EOT = 0x04

# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):
    # List of settings that a user can set for this High Level Analyzer.
    # my_string_setting = StringSetting()
    # my_number_setting = NumberSetting(min_value=0, max_value=100)
    # my_choices_setting = ChoicesSetting(choices=('A', 'B'))

    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'mytype': {
            'format': 'Output type: {{type}}, Input type: {{data.input_type}}'
        }
    }

    prefix = StringSetting(label='Message Prefix (optional)')
    frameIndex = 0
    myHlaFrame = None
    # newMsgFlag = True
    # prevStartTime = 0
    etxFlag = False
    chksumFlag = False

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''

        self.result_types["message"] = {
            'format': self.prefix + '{{{data.str}}}'
        }

        # print("Settings:", self.my_string_setting,
        #       self.my_number_setting, self.my_choices_setting)

    def initHlaFrame(self, frame):
        try:
            del self.myHlaFrame
        except:
            pass
        self.myHlaFrame = AnalyzerFrame('message', frame.start_time, frame.end_time, {'str':''})

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''

        # setup initial result, if not present
        first_frame = False
        hlaMsg = "Unknown"
        myRet = self.myHlaFrame

        if self.myHlaFrame is None:
            first_frame = True

        frameValue = frame.data["data"][0]

        if self.frameIndex == 0:
            if frameValue == SOH:
                hlaMsg = "SOH"
                self.initHlaFrame(frame)
        elif self.frameIndex == 1:
            if ord('A') <= frameValue <= ord('V'):
                comment = "~" + str(frameValue-0x37)
            else:
                comment = ""
            hlaMsg = "STA=" + chr(frameValue) + comment
            self.initHlaFrame(frame)
        elif self.frameIndex == 2:
            hlaMsg = "CMD=" + chr(frameValue)
            self.initHlaFrame(frame)
        elif self.frameIndex == 3:
            hlaMsg = chr(frameValue)
            myRet.end_time = frame.end_time
            myRet = None
        elif self.frameIndex == 4:
            if frameValue == STX:
                hlaMsg = "STX"
                self.initHlaFrame(frame)
        elif self.frameIndex == 5:
            hlaMsg = "Data No=" + chr(frameValue)
            self.initHlaFrame(frame)
        elif self.frameIndex == 6:
            hlaMsg = chr(frameValue)
            myRet.end_time = frame.end_time
            myRet = None
        elif self.frameIndex == 7:
            if frameValue == ETX:
                hlaMsg = "ETX"
                self.etxFlag = True
                self.initHlaFrame(frame)
            else:
                hlaMsg = "Data=" + chr(frameValue)
                self.initHlaFrame(frame)
        else:
            if not self.etxFlag:
                if frameValue != ETX:
                    hlaMsg = chr(frameValue)
                    myRet.end_time = frame.end_time
                    myRet = None
                else:
                    hlaMsg = "ETX"
                    self.etxFlag = True
                    self.initHlaFrame(frame)
            else:
                if not self.chksumFlag:
                    hlaMsg = "Chk=" + chr(frameValue)
                    self.initHlaFrame(frame)
                    self.chksumFlag = True
                else:
                    hlaMsg = chr(frameValue)
                    myRet.end_time = frame.end_time


        self.myHlaFrame.data["str"] += hlaMsg
        self.frameIndex +=1

        # Return the data frame itself
        # return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
        #     'input_type': frame.type
        # })
        return myRet
