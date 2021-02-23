# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
from HlaSM import HlaSM

SOH = 0x01
STX = 0x02
ETX = 0x03
EOT = 0x04
sm = HlaSM()

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
    myHlaFrame = None

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

    def bracketed(self, string):
        ret = "[" + string + "]"
        return ret

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

        """"""
        sm.update(frame)

        """"""

        if sm.is_Soh:
                hlaMsg = "SOH"
                self.initHlaFrame(frame)
        elif sm.is_Sta:
            if ord('A') <= frameValue <= ord('V'):
                comment = "~" + str(frameValue-0x37)
            else:
                comment = ""
            hlaMsg = "STA=" + self.bracketed(chr(frameValue)) + comment
            self.initHlaFrame(frame)
        elif sm.is_Cmd:
            if sm.tick == 0:
                hlaMsg = "CMD=" + self.bracketed(chr(frameValue))
                self.initHlaFrame(frame)
            else:
                hlaMsg = self.bracketed(chr(frameValue))
                myRet.end_time = frame.end_time
                myRet = None
        elif sm.is_Stx:
            hlaMsg = "STX"
            self.initHlaFrame(frame)
        elif sm.is_Datano:
            if sm.tick == 0:
                hlaMsg = "Data No=" + self.bracketed(chr(frameValue))
                self.initHlaFrame(frame)
            else:
                hlaMsg = self.bracketed(chr(frameValue))
                myRet.end_time = frame.end_time
                myRet = None
        elif sm.is_Data:
            if sm.tick == 0:
                hlaMsg = "Data=" + self.bracketed(chr(frameValue))
                self.initHlaFrame(frame)
            else:
                hlaMsg = self.bracketed(chr(frameValue))
                myRet.end_time = frame.end_time
                myRet = None
        elif sm.is_Etx:
                hlaMsg = "ETX"
                self.initHlaFrame(frame)
        elif sm.is_Chk:
            if sm.tick == 0:
                hlaMsg = "Chk=" + self.bracketed(chr(frameValue))
                self.initHlaFrame(frame)
            else:
                hlaMsg = self.bracketed(chr(frameValue))
                myRet.end_time = frame.end_time
        elif sm.is_Stx2:
            hlaMsg = "STX"
            self.initHlaFrame(frame)
        elif sm.is_Sta2:
            if ord('A') <= frameValue <= ord('V'):
                comment = "~" + str(frameValue-0x37)
            else:
                comment = ""
            hlaMsg = "STA=" + self.bracketed(chr(frameValue)) + comment
            self.initHlaFrame(frame)
        elif sm.is_Err:
            hlaMsg = "ERR=" + self.bracketed(chr(frameValue))
            self.initHlaFrame(frame)

        try:
            self.myHlaFrame.data["str"] += hlaMsg
        except:
            pass
        # self.frameIndex +=1

        # Return the data frame itself
        # return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
        #     'input_type': frame.type
        # })
        return myRet
