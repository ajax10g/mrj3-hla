#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 clpham <clpham@xps15>
#
# Distributed under terms of the MIT license.

"""

"""
from statemachine import StateMachine, State
from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting

SOH = 0x01
STX = 0x02
ETX = 0x03
EOT = 0x04


class HlaSM(StateMachine):
    """States"""
    Idle = State('Idle', initial=True)
    Soh = State('Soh')
    Stx = State('Stx')
    Etx = State('Etx')
    Eot = State('Eot')
    Sta = State('Sta')
    Cmd = State('Cmd')
    Datano = State('DataNo')
    Data = State('Data')
    Chk = State('Chk')
    Stx2 = State('Stx2')
    Sta2 = State('Sta2')
    Err = State('Err')

    """Transitions"""
    soh = Idle.to(Soh)
    sta = Soh.to(Sta)
    cmd = Sta.to(Cmd)
    stx = Cmd.to(Stx)
    datano = Stx.to(Datano)
    data = Datano.to(Data)
    etx = Data.to(Etx)
    chk = Etx.to(Chk)
    idle = Chk.to(Idle)
    eot = Idle.to(Eot)
    stx2 = Idle.to(Stx2)
    sta2 = Stx2.to(Sta2)
    err = Sta2.to(Err)
    data2 = Err.to(Data)
    idle2 = Eot.to(Idle)
    etx2 = Datano.to(Etx)
    etx3 = Err.to(Etx)

    soh2idle = Soh.to(Idle)
    sta2idle = Sta.to(Idle)
    cmd2idle = Cmd.to(Idle)
    stx2idle = Stx.to(Idle)
    datano2idle = Datano.to(Idle)
    data2idle = Data.to(Idle)
    etx2idle = Etx.to(Idle)
    chk2idle = Chk.to(Idle)
    stx22idle = Stx2.to(Idle)
    sta22idle = Sta2.to(Idle)
    err2idle = Err.to(Idle)

    """"""
    tick = 0
    prev_end_time = 0
    end_of_pkt = True

    def update(self, frame: AnalyzerFrame):
        frameValue = frame.data["data"][0]
        frame_width = frame.end_time - frame.start_time

        protocol_error = False
        if self.prev_end_time == 0:
            pass
        else:
            between_frames_width = frame.start_time - self.prev_end_time
            if float(between_frames_width) > float(frame_width)*2:
                protocol_error = True
                self.end_of_pkt = True

        if self.is_Idle:
            self.prev_end_time = 0
            if self.end_of_pkt:
                self.end_of_pkt = False
                if frameValue == SOH:
                    self.soh()
                elif frameValue == STX:
                    self.stx2()
                elif frameValue == EOT:
                    self.eot()
        elif self.is_Soh:
            self.sta() if not protocol_error else self.soh2idle()
        elif self.is_Sta:
                self.cmd() if not protocol_error else self.sta2idle()
        elif self.is_Cmd:
            if protocol_error:
                self.cmd2idle()
            elif self.tick==0:
                self.tick +=1
            else:
                self.tick =0
                self.stx()
        elif self.is_Stx:
                self.datano() if not protocol_error else self.stx2idle()
        elif self.is_Datano:
            if self.tick==0:
                self.tick +=1
            else:
                self.tick =0
                if frameValue == ETX:
                    self.etx2()
                else:
                    self.data()
        elif self.is_Data:
            if protocol_error:
                self.data2idle()
            else:
                self.tick +=1
                if frameValue == ETX:
                    self.tick =0
                    self.etx()
        elif self.is_Etx:
                self.chk() if not protocol_error else self.etx2idle()
        elif self.is_Chk:
            if protocol_error:
                self.chk2idle()
            elif self.tick==0:
                self.tick +=1
            else:
                self.tick =0
                self.end_of_pkt = True
                self.idle()
        elif self.is_Stx2:
                self.sta2() if not protocol_error else self.stx22idle()
        elif self.is_Sta2:
                self.err() if not protocol_error else self.sta22idle()
        elif self.is_Err:
            if protocol_error:
                self.err2idle()
            elif frameValue == ETX:
                self.etx3()
            else:
                self.data2()
        elif self.is_Eot:
                self.idle2()

        self.prev_end_time = frame.end_time
