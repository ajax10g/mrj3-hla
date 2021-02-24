# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting
from HlaSM import HlaSM

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
    myHlaFrame = None
    listHlaFrame = []
    sm = None

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
        
        self.sm = HlaSM()

    def initHlaFrame(self, frame):
        try:
            del self.myHlaFrame
        except:
            pass
        self.myHlaFrame = AnalyzerFrame('message', frame.start_time, frame.end_time, {'str':''})
        return self.myHlaFrame

    def bracketed(self, string):
        ret = "[" + string + "]"
        return ret

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''

        # setup initial result, if not present
        hlaMsg = "Unknown"
        myRet = None

        frameValue = frame.data["data"][0]

        """"""
        self.sm.update(frame)

        """"""

        if self.sm.is_Soh:
                hlaMsg = "SOH"
                self.listHlaFrame.clear() 
                _frame = self.initHlaFrame(frame)
                _frame.data["str"] += hlaMsg
                self.listHlaFrame.append(_frame)
        elif self.sm.is_Sta:
            if ord('A') <= frameValue <= ord('V'):
                comment = "~" + str(frameValue-0x37)
            else:
                comment = ""
            hlaMsg = "STA=" + self.bracketed(chr(frameValue)) + comment
            _frame = self.initHlaFrame(frame)
            _frame.data["str"] += hlaMsg
            self.listHlaFrame.append(_frame)
        elif self.sm.is_Cmd:
            if self.sm.tick == 0:
                hlaMsg = "CMD=" + self.bracketed(chr(frameValue))
                _frame = self.initHlaFrame(frame)
                _frame.data["str"] += hlaMsg
                self.listHlaFrame.append(_frame)
            else:
                hlaMsg = self.bracketed(chr(frameValue))
                _frame = self.listHlaFrame[-1]
                _frame.end_time = frame.end_time
                _frame.data["str"] += hlaMsg
        elif self.sm.is_Stx:
            hlaMsg = "STX"
            _frame = self.initHlaFrame(frame)
            _frame.data["str"] += hlaMsg
            self.listHlaFrame.append(_frame)
        elif self.sm.is_Datano:
            if self.sm.tick == 0:
                hlaMsg = "Data No=" + self.bracketed(chr(frameValue))
                _frame = self.initHlaFrame(frame)
                _frame.data["str"] += hlaMsg
                self.listHlaFrame.append(_frame)
            else:
                hlaMsg = self.bracketed(chr(frameValue))
                _frame = self.listHlaFrame[-1]
                _frame.end_time = frame.end_time
                _frame.data["str"] += hlaMsg
        elif self.sm.is_Data:
            if self.sm.tick == 0:
                hlaMsg = "Data=" + self.bracketed(chr(frameValue))
                _frame = self.initHlaFrame(frame)
                _frame.data["str"] += hlaMsg
                self.listHlaFrame.append(_frame)
            else:
                hlaMsg = self.bracketed(chr(frameValue))
                _frame = self.listHlaFrame[-1]
                _frame.end_time = frame.end_time
                _frame.data["str"] += hlaMsg
        elif self.sm.is_Etx:
                hlaMsg = "ETX"
                _frame = self.initHlaFrame(frame)
                _frame.data["str"] += hlaMsg
                self.listHlaFrame.append(_frame)
        elif self.sm.is_Chk:
            if self.sm.tick == 0:
                hlaMsg = "Chk=" + self.bracketed(chr(frameValue))
                _frame = self.initHlaFrame(frame)
                _frame.data["str"] += hlaMsg
                self.listHlaFrame.append(_frame)
            else:
                hlaMsg = self.bracketed(chr(frameValue))
                _frame = self.listHlaFrame[-1]
                _frame.end_time = frame.end_time
                _frame.data["str"] += hlaMsg
                myRet = self.listHlaFrame
        elif self.sm.is_Stx2:
            hlaMsg = "STX"
            self.listHlaFrame.clear() 
            _frame = self.initHlaFrame(frame)
            _frame.data["str"] += hlaMsg
            self.listHlaFrame.append(_frame)
        elif self.sm.is_Sta2:
            if ord('A') <= frameValue <= ord('V'):
                comment = "~" + str(frameValue-0x37)
            else:
                comment = ""
            hlaMsg = "STA=" + self.bracketed(chr(frameValue)) + comment
            _frame = self.initHlaFrame(frame)
            _frame.data["str"] += hlaMsg
            self.listHlaFrame.append(_frame)
        elif self.sm.is_Err:
            hlaMsg = "ERR=" + self.bracketed(chr(frameValue))
            _frame = self.initHlaFrame(frame)
            _frame.data["str"] += hlaMsg
            self.listHlaFrame.append(_frame)
        elif self.sm.is_Eot:
            hlaMsg = "EOT"
            _frame = self.initHlaFrame(frame)
            _frame.data["str"] += hlaMsg
            myRet = (_frame)

        # Return the data frame itself
        # return AnalyzerFrame('mytype', frame.start_time, frame.end_time, {
        #     'input_type': frame.type
        # })

        if myRet != None:
            self.sm.update(frame)

        return myRet
