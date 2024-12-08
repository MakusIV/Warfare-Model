
# Classi 

from enum import Enum
from typing import List


# Classe Payload
class Payload:
    def __init__(self, goods: int, energy: int, hr: int, hc: int, hs: int, hb: int):
        self.goods = goods
        self.energy = energy
        self.hr = hr
        self.hc = hc
        self.hs = hs
        self.hb = hb

    def method(self, arg_type):
        # Metodo generico
        pass


# Classe Point
class Point:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def distance(self, p: "Point", is_3D: bool) -> float:
        # Calcola la distanza
        pass

    def vector(self, p: "Point", is_3D: bool):
        # Calcola il vettore
        pass

    def tangent(self, sphere: "Sphere") -> "Segment":
        # Calcola la tangente
        pass


# Classe Segment
class Segment:
    def __init__(self, point_a: Point, point_b: Point, length: float, direction: "Vector"):
        self.point_a = point_a
        self.point_b = point_b
        self.length = length
        self.direction = direction

    def method(self, arg_type):
        # Metodo generico
        pass


# Classe Block
class Block:
    def __init__(self, name: str, description: str, category: Enum, function: str, 
                 damage: float, operational: float, state: Enum, component_status: float,
                 value: int, cost: int, position: Point, acs: Payload, rcs: Payload, payload: Payload):
        self.name = name
        self.description = description
        self.category = category
        self.function = function
        self.damage = damage
        self.operational = operational
        self.state = state
        self.component_status = component_status
        self.value = value
        self.cost = cost
        self.position = position
        self.acs = acs
        self.rcs = rcs
        self.payload = payload
        self.assets: List["Asset"] = []  # Riferimento agli Asset associati

    def add_asset(self, asset: "Asset"):
        """Aggiunge un Asset associato a questo Block."""
        if asset not in self.assets:
            self.assets.append(asset)
            asset.set_block(self)

    def remove_asset(self, asset: "Asset"):
        """Rimuove un Asset associato a questo Block."""
        if asset in self.assets:
            self.assets.remove(asset)
            asset.set_block(None)


# Classe Asset che estende Block
class Asset(Block):
    def __init__(self, crytical: bool, activation_timer: int, repair_time: int, **kwargs):
        super().__init__(**kwargs)
        self.crytical = crytical
        self.activation_timer = activation_timer
        self.repair_time = repair_time
        self.block: Block = None  # Riferimento al Block associato

    def set_block(self, block: Block):
        """Imposta il riferimento al Block associato."""
        if self.block is not block:
            if self.block:
                self.block.remove_asset(self)
            self.block = block
            if block:
                block.add_asset(self)

    def updt_timer(self):
        # Metodo per aggiornare il timer
        pass

    def start_timer(self):
        # Metodo per avviare il timer
        pass


# Classi derivate da Block
class Production(Block):
    def getProd(self) -> Payload:
        # Ottiene la produzione
        pass

    def production(self) -> Payload:
        # Calcola la produzione
        pass


class Urban(Block):
    def consume(self):
        # Consumo di risorse
        pass


class Storage(Block):
    def getPayload(self) -> Payload:
        # Ottiene il payload
        pass

    def setPayload(self, payload: Payload):
        # Imposta il payload
        pass

    def updateAcs(self, payload: Payload):
        # Aggiorna ACS
        pass


class Transport(Block):
    def getPayload(self) -> Payload:
        # Ottiene il payload
        pass

    def setPayload(self, payload: Payload):
        # Imposta il payload
        pass

    def updateAcs(self, payload: Payload):
        # Aggiorna ACS
        pass


class Military(Block):
    def __init__(self, combat_state: float, **kwargs):
        super().__init__(**kwargs)
        self.combat_state = combat_state

    def getPayload(self) -> Payload:
        # Ottiene il payload
        pass

    def setPayload(self, payload: Payload):
        # Imposta il payload
        pass

    def updateAcs(self, payload: Payload):
        # Aggiorna ACS
        pass

    def productionHr(self) -> Payload:
        # Produzione oraria
        pass

    def combat_state(self) -> float:
        return self.combat_state

    def consume(self) -> Payload:
        # Consumo di risorse
        pass
