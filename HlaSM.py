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

    """"""
    tick = 0

    def update(self, frame: AnalyzerFrame):
        frameValue = frame.data["data"][0]

        if self.is_Idle:
            if frameValue == SOH:
                self.soh()
            elif frameValue == STX:
                self.stx2()
            elif frameValue == EOT:
                self.eot()
        elif self.is_Soh:
            self.sta()
        elif self.is_Sta:
                self.cmd()
        elif self.is_Cmd:
            if self.tick==0:
                self.tick +=1
            else:
                self.tick =0
                self.stx()
        elif self.is_Stx:
                self.datano()
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
            self.tick +=1
            if frameValue == ETX:
                self.tick =0
                self.etx()
        elif self.is_Etx:
                self.chk()
        elif self.is_Chk:
            if self.tick==0:
                self.tick +=1
            else:
                self.tick =0
                self.idle()
        elif self.is_Stx2:
                self.sta2()
        elif self.is_Sta2:
                self.err()
        elif self.is_Err:
            if frameValue == ETX:
                self.etx3()
            else:
                self.data2()
        elif self.is_Eot:
                self.idle2()
