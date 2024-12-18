"""
 CLASS Payload
 
 Rappresenta il tipo di dato payload utilizzato in alcunen proprietà e metodi delle classi Block e Asset

"""


class Payload:
    def __init__(self, goods: int, energy: int, hr: int, hc: int, hs: int, hb: int):
        self.goods = goods
        self.energy = energy
        self.hr = hr
        self.hc = hc
        self.hs = hs
        self.hb = hb


