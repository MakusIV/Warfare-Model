'''
Ship_Data

Singleton Class — analogo a Vehicle_Data.py ma per asset navali.

Chiavi escluse rispetto a Vehicle_Data: 'communication', 'protection', 'hydraulic', 'TVD'
Chiave aggiuntiva: 'ship_class' (classe della nave, es. 'Nimitz-class')

La categoria utilizza i valori dell'enum Sea_Asset_Type definito in Context.py:
    Carrier, Cruiser, Destroyer, Frigate, Corvette,
    Submarine, Amphibious_Assault_Ship, Transport, Civilian

Velocità espressa in nodi (metric='nautical'); range in miglia nautiche (nm).
'''

from typing import Optional, List, Dict, ClassVar
from Code.Dynamic_War_Manager.Source.Context.Context import SEA_TASK, ACTION_TASKS, Sea_Asset_Type
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from dataclasses import dataclass

# ── LOGGING ──────────────────────────────────────────────────────────────────

logger = Logger(module_name=__name__, class_name='Ship_Data').logger

# ── COSTANTI ─────────────────────────────────────────────────────────────────

SHIP_TASK = SEA_TASK
MODES = list(ACTION_TASKS.keys())   # ['ground', 'air', 'sea']

CATEGORY = set(item.value for item in Sea_Asset_Type)

# Quantità di riferimento per il calcolo del factor_ammo_quantity
# (analoga ad AMMO_LOAD_REFERENCE in Vehicle_Data)
AMMO_LOAD_REFERENCE = {
    'MISSILES_SAM':     32,   # celle VLS / missili SAM imbarcati (riferimento)
    'MISSILES_ASM':      8,   # missili anti-nave (riferimento)
    'MISSILES_TORPEDO':  4,   # siluri (riferimento)
    'GUNS':            250,   # colpi per il cannone navale (riferimento)
    'CIWS':              1,   # sistema d'arma ravvicinato (contato come unità)
}

# Score base per ogni tipo di arma navale (analogo a get_weapon_score in Ground_Weapon_Data)
SHIP_WEAPON_SCORE: Dict[str, float] = {
    # ── Missili SAM ────────────────────────────────────────────────────────
    'RIM-162-ESSM':         3.5,
    'RIM-7M-Sea-Sparrow':   3.0,
    'RIM-66-SM-1':          3.0,
    'RIM-66-SM-2':          4.0,
    'RIM-156-SM-2ER':       4.5,
    'SA-N-4-Gecko':         2.5,
    'SA-N-9-Gauntlet':      3.0,
    'S-300F':               5.0,
    'HHQ-7':                2.5,
    'HHQ-9':                4.5,
    'HHQ-16':               3.5,
    'URK-5-Rastrub':        3.0,
    # ── Missili Anti-nave / Cruise ─────────────────────────────────────────
    'RGM-84-Harpoon':       3.5,
    'BGM-109-Tomahawk':     4.5,
    'P-700-Granit':         5.0,
    'P-270-Moskit':         4.5,
    'P-1000-Vulkan':        4.5,
    'YJ-12':                4.0,
    'YJ-18':                4.0,
    'YJ-83':                3.5,
    # ── Siluri ────────────────────────────────────────────────────────────
    'Mk-46':                3.0,
    'Mk-48':                4.0,
    'TEST-71':              3.0,
    'USET-80':              3.5,
    'Type-93':              3.5,
    # ── Cannoni navali ────────────────────────────────────────────────────
    'Mk-45-5in':            2.5,
    'OTO-Melara-76mm':      2.0,
    'AK-100-100mm':         2.5,
    'AK-130-130mm':         3.0,
    'AK-176-76mm':          1.5,
    'Type-79A-100mm':       2.0,
    # ── CIWS ──────────────────────────────────────────────────────────────
    'Mk-15-Phalanx':        2.0,
    'AK-630':               2.0,
    'Type-730':             2.0,
}

SCORES = (
    'combat score',
    'radar score',
    'radar score air',
    'radar score sea',
    'weapon score',
    'speed score',
    'range score',
    'avalaibility',
    'manutenability score (mttr)',
    'reliability score (mtbf)',
)

# ── CLASSE PRINCIPALE ────────────────────────────────────────────────────────

@dataclass
class Ship_Data:

    _registry: ClassVar[Dict[str, 'Ship_Data']] = {}

    def __init__(
        self,
        constructor: str,
        made: str,
        model: str,
        category: str,
        ship_class: str,
        physical_characteristics: Dict,
        start_service: int,
        end_service,
        cost: float,
        range: float,
        roles: List[str],
        engine: Dict,
        weapons: Dict,
        radar,
        speed_data: Dict,
    ):
        _PC_KEYS = {'length', 'width', 'height', 'weight'}
        if not isinstance(physical_characteristics, dict) or not _PC_KEYS.issubset(physical_characteristics):
            raise ValueError(
                f"physical_characteristics must be a dict with keys {_PC_KEYS}, "
                f"got: {physical_characteristics!r}"
            )
        for _k in _PC_KEYS:
            if not isinstance(physical_characteristics[_k], int) or physical_characteristics[_k] <= 0:
                raise ValueError(
                    f"physical_characteristics['{_k}'] must be a positive int, "
                    f"got: {physical_characteristics[_k]!r}"
                )
        self.constructor = constructor
        self.made = made
        self.model = model          # chiave nel registro
        self.category = category    # valore Sea_Asset_Type (es. 'Carrier')
        self.ship_class = ship_class  # classe della nave (es. 'Nimitz-class')
        self.physical_characteristics = physical_characteristics
        self.start_service = start_service
        self.end_service = end_service
        self.cost = cost            # miliardi di $
        self.range = range          # miglia nautiche (nm)
        self.roles = roles
        self.engine = engine
        self.weapons = weapons      # {'MISSILES_SAM': [('model', qty), ...], ...}
        self.radar = radar          # dict con 'capabilities' e 'reliability', oppure False/None
        self.speed_data = speed_data  # velocità in nodi (metric='nautical')

        Ship_Data._registry[self.model] = self

    # ── Getter / Setter ──────────────────────────────────────────────────────

    def get_ship(self, model: str) -> Optional['Ship_Data']:
        return self._registry.get(model)

    # ── Metodi di valutazione privati ────────────────────────────────────────

    def _radar_eval(self, modes: Optional[List] = None) -> float:
        """Valuta le capacità radar della nave.

        Args:
            modes: lista di modalità ('air', 'ground', 'sea'); se None, tutte.

        Returns:
            float: punteggio radar
        """
        if self.radar is False:
            return 0.0
        if self.radar is None:
            logger.warning(f"{self.made} {self.model} (category:{self.category}) - Radar not defined.")
            return 0.0

        if not modes:
            modes = MODES
        elif not isinstance(modes, list) or not all(m in MODES for m in modes):
            raise TypeError(f"modes must be a list with values: {MODES!r}, got {modes!r}.")

        # Valori di riferimento per navi (range molto superiori ai veicoli terrestri)
        reference_values = {
            'tracking_range':     500.0,   # km
            'acquisition_range':  800.0,   # km
            'engagement_range':   400.0,   # km
            'multi_target_capacity': 20,   # numero bersagli
        }
        weights = {
            'tracking_range':      0.2,
            'acquisition_range':   0.1,
            'engagement_range':    0.3,
            'multi_target':        0.4,
        }
        score = 0.0
        for m in modes:
            cap = self.radar['capabilities'].get(m)
            if cap and cap[0]:
                score += cap[1].get('tracking_range',     0) * weights['tracking_range']     / reference_values['tracking_range']
                score += cap[1].get('acquisition_range',  0) * weights['acquisition_range']  / reference_values['acquisition_range']
                score += cap[1].get('engagement_range',   0) * weights['engagement_range']   / reference_values['engagement_range']
                score += cap[1].get('multi_target_capacity', 0) * weights['multi_target']    / reference_values['multi_target_capacity']
        return score

    def _reliability_eval(self) -> float:
        """Valuta l'affidabilità (MTBF) dei sottosistemi della nave (motore + radar).

        Returns:
            float: ore medie tra i guasti (valore composito)
        """
        components = [
            self.engine.get('reliability', {}).get('mtbf', 0) if self.engine and self.engine.get('reliability') else None,
            self.radar.get('reliability', {}).get('mtbf', 0)  if self.radar and self.radar.get('reliability')  else None,
        ]
        filtered = [x for x in components if x is not None]
        if not filtered:
            return 0.0
        return min(filtered) * 0.3 + 0.7 * sum(filtered) / len(filtered)

    def _maintenance_eval(self) -> float:
        """Valuta il carico di manutenzione (MTTR) dei sottosistemi della nave.

        Returns:
            float: ore di lavoro di manutenzione (valore composito)
        """
        components = [
            self.engine.get('reliability', {}).get('mttr', 0) if self.engine and self.engine.get('reliability') else None,
            self.radar.get('reliability', {}).get('mttr', 0)  if self.radar and self.radar.get('reliability')  else None,
        ]
        filtered = [x for x in components if x is not None]
        if not filtered:
            return 0.0
        return min(filtered) * 0.3 + 0.7 * sum(filtered) / len(filtered)

    def _avalaiability_eval(self) -> float:
        """Valuta la disponibilità operativa della nave (MTBF / (MTBF + MTTR)).

        Returns:
            float: disponibilità operativa
        """
        mtbf = self._reliability_eval()
        mttr = self._maintenance_eval()
        if mtbf == 0:
            return 0.0
        return mtbf / mttr if mttr > 0 else 0.0

    def _speed_eval(self) -> float:
        """Valuta la velocità della nave (in nodi, metric='nautical').

        Returns:
            float: punteggio di velocità normalizzato [0, 1] rispetto a 35 nodi di riferimento.
        """
        if not self.speed_data:
            logger.warning(f"{self.made} {self.model} - speed_data not defined.")
            return 0.0

        reference_knots = 35.0   # nodi (fast attack / destroyer class ceiling)
        weights = {'sustained': 0.3, 'max': 0.5, 'flank': 0.2}
        score = 0.0

        for speed_type, weight in weights.items():
            data = self.speed_data.get(speed_type, {})
            if not data:
                continue
            metric = data.get('metric')
            speed = data.get('speed', 0)
            if metric == 'nautical':
                pass   # già in nodi
            elif metric == 'metric':
                speed = speed / 1.852   # km/h → nodi
            elif metric == 'imperial':
                speed = speed * 0.868976   # mph → nodi
            else:
                raise ValueError(f"metric must be 'nautical', 'metric' or 'imperial', got {metric!r}.")
            score += speed * weight

        return (score / sum(weights.values())) / reference_knots

    def _weapon_eval(self) -> float:
        """Valuta l'armamento installato sulla nave.

        Returns:
            float: punteggio armamento
        """
        score = 0.0
        for weapon_type, weapon_list in self.weapons.items():
            ref = AMMO_LOAD_REFERENCE.get(weapon_type, 1)
            for weapon_model, quantity in weapon_list:
                base = SHIP_WEAPON_SCORE.get(weapon_model, 0.0)
                if base == 0.0:
                    logger.warning(f"{self.model}: weapon '{weapon_model}' not found in SHIP_WEAPON_SCORE.")
                factor = quantity / ref
                factor = max(0.80, min(1.2, factor))
                score += base * factor
        return score

    def _range_eval(self) -> float:
        """Valuta l'autonomia operativa della nave.

        Returns:
            float: punteggio di autonomia [0, 1] rispetto a 10 000 nm di riferimento.
        """
        if not self.range:
            logger.warning(f"{self.made} {self.model} - range not defined.")
            return 0.0
        reference_nm = 10_000.0
        return min(self.range / reference_nm, 1.5)   # cap a 1.5 per navi nucleari

    def _combat_eval(self) -> float:
        """Restituisce lo score di combattimento complessivo della nave.

        I pesi per sottosistema variano in funzione della categoria dell'asset.

        Returns:
            float: combat score
        """
        params = {
            'weapon': {
                'score': self._weapon_eval(),
                'weights': {
                    Sea_Asset_Type.CARRIER.value:               5,
                    Sea_Asset_Type.CRUISER.value:               10,
                    Sea_Asset_Type.DESTROYER.value:             10,
                    Sea_Asset_Type.FRIGATE.value:               8,
                    Sea_Asset_Type.CORVETTE.value:              8,
                    Sea_Asset_Type.SUBMARINE.value:             10,
                    Sea_Asset_Type.AMPHIBIOUS_ASSAULT_SHIP.value: 3,
                    Sea_Asset_Type.TRANSPORT.value:             1,
                    Sea_Asset_Type.CIVILIAN.value:              1,
                },
            },
            'radar': {
                'score': self._radar_eval(),
                'weights': {
                    Sea_Asset_Type.CARRIER.value:               3,
                    Sea_Asset_Type.CRUISER.value:               5,
                    Sea_Asset_Type.DESTROYER.value:             7,
                    Sea_Asset_Type.FRIGATE.value:               5,
                    Sea_Asset_Type.CORVETTE.value:              3,
                    Sea_Asset_Type.SUBMARINE.value:             2,
                    Sea_Asset_Type.AMPHIBIOUS_ASSAULT_SHIP.value: 2,
                    Sea_Asset_Type.TRANSPORT.value:             1,
                    Sea_Asset_Type.CIVILIAN.value:              1,
                },
            },
            'speed': {
                'score': self._speed_eval(),
                'weights': {
                    Sea_Asset_Type.CARRIER.value:               5,
                    Sea_Asset_Type.CRUISER.value:               5,
                    Sea_Asset_Type.DESTROYER.value:             7,
                    Sea_Asset_Type.FRIGATE.value:               6,
                    Sea_Asset_Type.CORVETTE.value:              8,
                    Sea_Asset_Type.SUBMARINE.value:             5,
                    Sea_Asset_Type.AMPHIBIOUS_ASSAULT_SHIP.value: 4,
                    Sea_Asset_Type.TRANSPORT.value:             3,
                    Sea_Asset_Type.CIVILIAN.value:              3,
                },
            },
            'range': {
                'score': self._range_eval(),
                'weights': {
                    Sea_Asset_Type.CARRIER.value:               10,
                    Sea_Asset_Type.CRUISER.value:               7,
                    Sea_Asset_Type.DESTROYER.value:             6,
                    Sea_Asset_Type.FRIGATE.value:               6,
                    Sea_Asset_Type.CORVETTE.value:              4,
                    Sea_Asset_Type.SUBMARINE.value:             8,
                    Sea_Asset_Type.AMPHIBIOUS_ASSAULT_SHIP.value: 7,
                    Sea_Asset_Type.TRANSPORT.value:             7,
                    Sea_Asset_Type.CIVILIAN.value:              5,
                },
            },
        }

        tot_weights = sum(data['weights'][self.category] for data in params.values())
        if tot_weights == 0:
            return 0.0
        return sum(data['score'] * data['weights'][self.category] for data in params.values()) / tot_weights

    # ── Metodi di confronto normalizzati ─────────────────────────────────────

    def _normalize(self, value: float, scores: List[float]) -> float:
        """Normalizza un valore nell'intervallo [0, 1].

        Args:
            value: valore da normalizzare
            scores: lista di tutti i valori per il calcolo min/max

        Returns:
            float: valore normalizzato [0, 1]
        """
        if not scores:
            return 0.0
        min_val = min(scores)
        max_val = max(scores)
        if max_val == min_val:
            return 0.5
        return (value - min_val) / (max_val - min_val)

    def _ships_in_category(self, category: Optional[str]) -> List['Ship_Data']:
        """Restituisce le navi del registro filtrate per categoria."""
        if not category:
            return list(Ship_Data._registry.values())
        if category not in CATEGORY:
            raise ValueError(f"category must be one of {CATEGORY!r}, got {category!r}.")
        return [s for s in Ship_Data._registry.values() if s.category == category]

    def get_normalized_combat_score(self, category: Optional[str] = None) -> float:
        """Restituisce il combat score normalizzato [0, 1]."""
        ships = self._ships_in_category(category)
        scores = [s._combat_eval() for s in ships]
        return self._normalize(self._combat_eval(), scores)

    def get_normalized_weapon_score(self, category: Optional[str] = None) -> float:
        """Restituisce il weapon score normalizzato [0, 1]."""
        ships = self._ships_in_category(category)
        scores = [s._weapon_eval() for s in ships]
        return self._normalize(self._weapon_eval(), scores)

    def get_normalized_radar_score(self, modes: Optional[List] = None, category: Optional[str] = None) -> float:
        """Restituisce il radar score normalizzato [0, 1]."""
        ships = self._ships_in_category(category)
        scores = [s._radar_eval(modes=modes) for s in ships]
        return self._normalize(self._radar_eval(modes=modes), scores)

    def get_normalized_speed_score(self, category: Optional[str] = None) -> float:
        """Restituisce lo speed score normalizzato [0, 1]."""
        ships = self._ships_in_category(category)
        scores = [s._speed_eval() for s in ships]
        return self._normalize(self._speed_eval(), scores)

    def get_normalized_range_score(self, category: Optional[str] = None) -> float:
        """Restituisce il range score normalizzato [0, 1]."""
        ships = self._ships_in_category(category)
        scores = [s._range_eval() for s in ships]
        return self._normalize(self._range_eval(), scores)

    def get_normalized_reliability_score(self, category: Optional[str] = None) -> float:
        """Restituisce il reliability score (MTBF) normalizzato [0, 1]."""
        ships = self._ships_in_category(category)
        scores = [s._reliability_eval() for s in ships]
        return self._normalize(self._reliability_eval(), scores)

    def get_normalized_maintenance_score(self, category: Optional[str] = None) -> float:
        """Restituisce il maintenance score (MTTR) normalizzato [0, 1].

        Invertito: score alto = manutenzione più rapida.
        """
        ships = self._ships_in_category(category)
        scores = [s._maintenance_eval() for s in ships]
        return 1 - self._normalize(self._maintenance_eval(), scores)

    def get_normalized_avalaiability_score(self, category: Optional[str] = None) -> float:
        """Restituisce l'avalaibility score normalizzato [0, 1]."""
        ships = self._ships_in_category(category)
        scores = [s._avalaiability_eval() for s in ships]
        return self._normalize(self._avalaiability_eval(), scores)


# ── DATI NAVI ─────────────────────────────────────────────────────────────────
#
# metric = 'nautical'  → velocità in nodi, range in miglia nautiche (nm)
# radar capabilities   → range in km
# cost                 → miliardi di $ (B$)
# Categoria dal dizionario navi in Initial_Context → valore Sea_Asset_Type

# =============================================================================
# CARRIERS  (Sea_Asset_Type.CARRIER = 'Carrier')
# =============================================================================

# ── CVN-70 Carl Vinson (Nimitz-class, USA) ───────────────────────────────────
CVN70_data = {
    'constructor':   'Newport News Shipbuilding',
    'model':         'CVN-70 Carl Vinson',
    'made':          'USA',
    'ship_class':    'Nimitz-class',
    'category':      Sea_Asset_Type.CARRIER.value,
    'physical_characteristics': {'length': 333, 'width': 77, 'height': 76, 'weight': 104000},
    'start_service': 1982,
    'end_service':   None,
    'cost':          4.5,    # B$ (approx costruzione)
    'range':         20_000, # nm (propulsione nucleare — praticamente illimitata, convenzionalmente 20 000)
    'roles':         ['Carrier', 'Power_Projection', 'Air_Wing_Command'],
    'engine': {
        'model':        '2x A4W Nuclear Reactor',
        'capabilities': {'thrust': 280_000, 'fuel_efficiency': 1.0, 'type': 'nuclear'},
        'reliability':  {'mtbf': 500, 'mttr': 24},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-162-ESSM', 32), ('RIM-7M-Sea-Sparrow', 8)],
        'CIWS':         [('Mk-15-Phalanx', 3)],
    },
    'radar': {
        'model':        'AN/SPS-49 + AN/SPS-67',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 450, 'tracking_range': 400, 'engagement_range': 0, 'multi_target_capacity': 15}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80,  'tracking_range': 60,  'engagement_range': 0, 'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 200, 'mttr': 6},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.4},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.7},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.0},
    },
}

# ── CVN-71 Theodore Roosevelt (Nimitz-class, USA) ────────────────────────────
CVN71_data = {
    'constructor':   'Newport News Shipbuilding',
    'model':         'CVN-71 Theodore Roosevelt',
    'made':          'USA',
    'ship_class':    'Nimitz-class',
    'category':      Sea_Asset_Type.CARRIER.value,
    'physical_characteristics': {'length': 333, 'width': 77, 'height': 76, 'weight': 104000},
    'start_service': 1986,
    'end_service':   None,
    'cost':          4.5,
    'range':         20_000,
    'roles':         ['Carrier', 'Power_Projection', 'Air_Wing_Command'],
    'engine': {
        'model':        '2x A4W Nuclear Reactor',
        'capabilities': {'thrust': 280_000, 'fuel_efficiency': 1.0, 'type': 'nuclear'},
        'reliability':  {'mtbf': 500, 'mttr': 24},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-162-ESSM', 32), ('RIM-7M-Sea-Sparrow', 8)],
        'CIWS':         [('Mk-15-Phalanx', 3)],
    },
    'radar': {
        'model':        'AN/SPS-49 + AN/SPS-67',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 450, 'tracking_range': 400, 'engagement_range': 0, 'multi_target_capacity': 15}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80,  'tracking_range': 60,  'engagement_range': 0, 'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 200, 'mttr': 6},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.4},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.7},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.0},
    },
}

# ── CVN-72 Abraham Lincoln (Nimitz-class, USA) ───────────────────────────────
CVN72_data = {
    'constructor':   'Newport News Shipbuilding',
    'model':         'CVN-72 Abraham Lincoln',
    'made':          'USA',
    'ship_class':    'Nimitz-class',
    'category':      Sea_Asset_Type.CARRIER.value,
    'physical_characteristics': {'length': 333, 'width': 77, 'height': 76, 'weight': 104000},
    'start_service': 1989,
    'end_service':   None,
    'cost':          4.7,
    'range':         20_000,
    'roles':         ['Carrier', 'Power_Projection', 'Air_Wing_Command'],
    'engine': {
        'model':        '2x A4W Nuclear Reactor',
        'capabilities': {'thrust': 280_000, 'fuel_efficiency': 1.0, 'type': 'nuclear'},
        'reliability':  {'mtbf': 500, 'mttr': 24},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-162-ESSM', 32), ('RIM-7M-Sea-Sparrow', 8)],
        'CIWS':         [('Mk-15-Phalanx', 3)],
    },
    'radar': {
        'model':        'AN/SPS-49 + AN/SPS-67',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 450, 'tracking_range': 400, 'engagement_range': 0, 'multi_target_capacity': 15}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80,  'tracking_range': 60,  'engagement_range': 0, 'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 200, 'mttr': 6},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.4},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.7},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.0},
    },
}

# ── CVN-73 George Washington (Nimitz-class, USA) ─────────────────────────────
CVN73_data = {
    'constructor':   'Newport News Shipbuilding',
    'model':         'CVN-73 George Washington',
    'made':          'USA',
    'ship_class':    'Nimitz-class',
    'category':      Sea_Asset_Type.CARRIER.value,
    'physical_characteristics': {'length': 333, 'width': 77, 'height': 76, 'weight': 104000},
    'start_service': 1992,
    'end_service':   None,
    'cost':          4.7,
    'range':         20_000,
    'roles':         ['Carrier', 'Power_Projection', 'Air_Wing_Command'],
    'engine': {
        'model':        '2x A4W Nuclear Reactor',
        'capabilities': {'thrust': 280_000, 'fuel_efficiency': 1.0, 'type': 'nuclear'},
        'reliability':  {'mtbf': 500, 'mttr': 24},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-162-ESSM', 32), ('RIM-7M-Sea-Sparrow', 8)],
        'CIWS':         [('Mk-15-Phalanx', 3)],
    },
    'radar': {
        'model':        'AN/SPS-49 + AN/SPS-67',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 450, 'tracking_range': 400, 'engagement_range': 0, 'multi_target_capacity': 15}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80,  'tracking_range': 60,  'engagement_range': 0, 'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 200, 'mttr': 6},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.4},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.7},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.0},
    },
}

# ── CVN-74 John C. Stennis (Nimitz-class, USA) ───────────────────────────────
CVN74_data = {
    'constructor':   'Newport News Shipbuilding',
    'model':         'CVN-74 John C. Stennis',
    'made':          'USA',
    'ship_class':    'Nimitz-class',
    'category':      Sea_Asset_Type.CARRIER.value,
    'physical_characteristics': {'length': 333, 'width': 77, 'height': 76, 'weight': 104000},
    'start_service': 1995,
    'end_service':   None,
    'cost':          4.5,
    'range':         20_000,
    'roles':         ['Carrier', 'Power_Projection', 'Air_Wing_Command'],
    'engine': {
        'model':        '2x A4W Nuclear Reactor',
        'capabilities': {'thrust': 280_000, 'fuel_efficiency': 1.0, 'type': 'nuclear'},
        'reliability':  {'mtbf': 500, 'mttr': 24},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-162-ESSM', 32), ('RIM-7M-Sea-Sparrow', 8)],
        'CIWS':         [('Mk-15-Phalanx', 3)],
    },
    'radar': {
        'model':        'AN/SPS-49 + AN/SPS-67',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 450, 'tracking_range': 400, 'engagement_range': 0, 'multi_target_capacity': 15}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80,  'tracking_range': 60,  'engagement_range': 0, 'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 200, 'mttr': 6},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.4},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.7},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.0},
    },
}

# ── CVN-75 Harry S. Truman (Nimitz-class, USA) ───────────────────────────────
CVN75_data = {
    'constructor':   'Newport News Shipbuilding',
    'model':         'CVN-75 Harry S. Truman',
    'made':          'USA',
    'ship_class':    'Nimitz-class',
    'category':      Sea_Asset_Type.CARRIER.value,
    'physical_characteristics': {'length': 333, 'width': 77, 'height': 76, 'weight': 104000},
    'start_service': 1998,
    'end_service':   None,
    'cost':          4.5,
    'range':         20_000,
    'roles':         ['Carrier', 'Power_Projection', 'Air_Wing_Command'],
    'engine': {
        'model':        '2x A4W Nuclear Reactor',
        'capabilities': {'thrust': 280_000, 'fuel_efficiency': 1.0, 'type': 'nuclear'},
        'reliability':  {'mtbf': 500, 'mttr': 24},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-162-ESSM', 32), ('RIM-7M-Sea-Sparrow', 8)],
        'CIWS':         [('Mk-15-Phalanx', 3)],
    },
    'radar': {
        'model':        'AN/SPS-49 + AN/SPS-67',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 450, 'tracking_range': 400, 'engagement_range': 0, 'multi_target_capacity': 15}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80,  'tracking_range': 60,  'engagement_range': 0, 'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 200, 'mttr': 6},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.4},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.7},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.0},
    },
}

# ── CV-59 USS Forrestal (Forrestal-class, USA) ───────────────────────────────
CV59_data = {
    'constructor':   'Newport News Shipbuilding',
    'model':         'CV-59 USS Forrestal',
    'made':          'USA',
    'ship_class':    'Forrestal-class',
    'category':      Sea_Asset_Type.CARRIER.value,
    'physical_characteristics': {'length': 331, 'width': 76, 'height': 57, 'weight': 79000},
    'start_service': 1955,
    'end_service':   1993,
    'cost':          0.22,   # B$ costo storico
    'range':         8_000,  # nm (convenzionale, turbine a vapore)
    'roles':         ['Carrier', 'Power_Projection'],
    'engine': {
        'model':        '4x Westinghouse Steam Turbine',
        'capabilities': {'thrust': 260_000, 'fuel_efficiency': 0.5, 'type': 'steam'},
        'reliability':  {'mtbf': 80, 'mttr': 20},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-7M-Sea-Sparrow', 8)],
        'CIWS':         [('Mk-15-Phalanx', 2)],
    },
    'radar': {
        'model':        'AN/SPS-43 + AN/SPS-30',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 350, 'tracking_range': 280, 'engagement_range': 0, 'multi_target_capacity': 8}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 60,  'tracking_range': 50,  'engagement_range': 0, 'multi_target_capacity': 5}),
        },
        'reliability': {'mtbf': 100, 'mttr': 10},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 30, 'consume': 0.6},
        'max':       {'metric': 'nautical', 'speed': 33, 'consume': 1.0},
        'flank':     {'metric': 'nautical', 'speed': 34, 'consume': 1.5},
    },
}

# ── CV 1143.5 Admiral Kuznetsov (Russia) ─────────────────────────────────────
KuznetsovAdmiral_data = {
    'constructor':   'Nosenko Black Sea Shipyard',
    'model':         'CV 1143.5 Admiral Kuznetsov',
    'made':          'Russia',
    'ship_class':    'Admiral Kuznetsov-class',
    'category':      Sea_Asset_Type.CARRIER.value,
    'physical_characteristics': {'length': 305, 'width': 75, 'height': 64, 'weight': 59000},
    'start_service': 1990,
    'end_service':   None,
    'cost':          1.2,
    'range':         8_500,
    'roles':         ['Carrier', 'Power_Projection', 'Anti-Ship'],
    'engine': {
        'model':        '4x Steam Turbine + 9x Boiler',
        'capabilities': {'thrust': 200_000, 'fuel_efficiency': 0.45, 'type': 'steam'},
        'reliability':  {'mtbf': 30, 'mttr': 40},   # storia di guasti ai propulsori
    },
    'weapons': {
        'MISSILES_SAM': [('SA-N-9-Gauntlet', 192), ('S-300F', 4)],
        'MISSILES_ASM': [('P-700-Granit', 12)],
        'CIWS':         [('AK-630', 4)],
        'GUNS':         [('AK-100-100mm', 120)],
    },
    'radar': {
        'model':        'Sky Watch Phased Array + Fregat-MA',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 400, 'tracking_range': 350, 'engagement_range': 200, 'multi_target_capacity': 12}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 100, 'tracking_range': 80,  'engagement_range': 50,  'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 60, 'mttr': 12},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 22, 'consume': 0.7},
        'max':       {'metric': 'nautical', 'speed': 27, 'consume': 1.0},
        'flank':     {'metric': 'nautical', 'speed': 29, 'consume': 1.5},
    },
}


# =============================================================================
# DESTROYERS  (Sea_Asset_Type.DESTROYER = 'Destroyer')
# =============================================================================

# ── USS Arleigh Burke IIa (USA) ───────────────────────────────────────────────
ArleighBurke_data = {
    'constructor':   'Bath Iron Works / Ingalls Shipbuilding',
    'model':         'USS Arleigh Burke IIa',
    'made':          'USA',
    'ship_class':    'Arleigh Burke-class',
    'category':      Sea_Asset_Type.DESTROYER.value,
    'physical_characteristics': {'length': 155, 'width': 20, 'height': 28, 'weight': 9100},
    'start_service': 1991,
    'end_service':   None,
    'cost':          1.8,
    'range':         4_400,
    'roles':         ['AAW', 'ASuW', 'ASW', 'Strike'],
    'engine': {
        'model':        '4x General Electric LM2500',
        'capabilities': {'thrust': 100_000, 'fuel_efficiency': 0.7, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 120, 'mttr': 8},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-156-SM-2ER', 74), ('RIM-162-ESSM', 16)],
        'MISSILES_ASM': [('RGM-84-Harpoon', 8), ('BGM-109-Tomahawk', 12)],
        'MISSILES_TORPEDO': [('Mk-46', 6)],
        'GUNS':         [('Mk-45-5in', 600)],
        'CIWS':         [('Mk-15-Phalanx', 1)],
    },
    'radar': {
        'model':        'AN/SPY-1D(V) AEGIS',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 500, 'tracking_range': 450, 'engagement_range': 320, 'multi_target_capacity': 20}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 120, 'tracking_range': 100, 'engagement_range': 80,  'multi_target_capacity': 12}),
        },
        'reliability': {'mtbf': 150, 'mttr': 5},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.8},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.2},
    },
}

# ── Type 052B Guangzhou-class (China) ─────────────────────────────────────────
Type052B_data = {
    'constructor':   'Jiangnan Shipyard',
    'model':         'Type 052B Guangzhou-class',
    'made':          'China',
    'ship_class':    'Luyang I-class',
    'category':      Sea_Asset_Type.DESTROYER.value,
    'physical_characteristics': {'length': 154, 'width': 17, 'height': 30, 'weight': 6500},
    'start_service': 2004,
    'end_service':   None,
    'cost':          0.6,
    'range':         4_000,
    'roles':         ['AAW', 'ASuW', 'ASW'],
    'engine': {
        'model':        'CODOG (2x LM2500 + 2x MTU)',
        'capabilities': {'thrust': 58_000, 'fuel_efficiency': 0.65, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 90, 'mttr': 10},
    },
    'weapons': {
        'MISSILES_SAM': [('HHQ-7', 8)],
        'MISSILES_ASM': [('YJ-12', 16)],
        'MISSILES_TORPEDO': [('Mk-46', 6)],
        'GUNS':         [('AK-100-100mm', 200)],
        'CIWS':         [('Type-730', 2)],
    },
    'radar': {
        'model':        'Type 381 3D Air Search',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 250, 'tracking_range': 200, 'engagement_range': 100, 'multi_target_capacity': 10}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80,  'tracking_range': 60,  'engagement_range': 40,  'multi_target_capacity': 6}),
        },
        'reliability': {'mtbf': 80, 'mttr': 8},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 25, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 29, 'consume': 0.8},
        'flank':     {'metric': 'nautical', 'speed': 30, 'consume': 1.2},
    },
}

# ── Type 052C (China) ─────────────────────────────────────────────────────────
Type052C_data = {
    'constructor':   'Jiangnan Shipyard',
    'model':         'Type 052C',
    'made':          'China',
    'ship_class':    'Luyang II-class',
    'category':      Sea_Asset_Type.DESTROYER.value,
    'physical_characteristics': {'length': 157, 'width': 17, 'height': 32, 'weight': 7000},
    'start_service': 2004,
    'end_service':   None,
    'cost':          0.9,
    'range':         4_500,
    'roles':         ['AAW', 'ASuW', 'ASW', 'Area_Air_Defense'],
    'engine': {
        'model':        'CODOG (2x LM2500 + 2x MTU 20V 956)',
        'capabilities': {'thrust': 60_000, 'fuel_efficiency': 0.68, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 100, 'mttr': 9},
    },
    'weapons': {
        'MISSILES_SAM': [('HHQ-9', 48)],
        'MISSILES_ASM': [('YJ-12', 8)],
        'MISSILES_TORPEDO': [('Type-93', 6)],
        'GUNS':         [('Type-79A-100mm', 200)],
        'CIWS':         [('Type-730', 2)],
    },
    'radar': {
        'model':        'Type 346 Dragon Eye AESA',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 400, 'tracking_range': 350, 'engagement_range': 200, 'multi_target_capacity': 15}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 100, 'tracking_range': 80,  'engagement_range': 60,  'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 110, 'mttr': 7},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 25, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 29, 'consume': 0.8},
        'flank':     {'metric': 'nautical', 'speed': 30, 'consume': 1.2},
    },
}


# =============================================================================
# CRUISERS  (Sea_Asset_Type.CRUISER = 'Cruiser')
# =============================================================================

# ── CG-65 Chosin (Ticonderoga-class, USA) ────────────────────────────────────
CG65_data = {
    'constructor':   'Bath Iron Works',
    'model':         'CG-65',
    'made':          'USA',
    'ship_class':    'Ticonderoga-class',
    'category':      Sea_Asset_Type.CRUISER.value,
    'physical_characteristics': {'length': 173, 'width': 17, 'height': 28, 'weight': 9800},
    'start_service': 1992,
    'end_service':   None,
    'cost':          1.1,
    'range':         6_000,
    'roles':         ['AAW', 'ASuW', 'ASW', 'Strike', 'Battle_Group_Command'],
    'engine': {
        'model':        '4x General Electric LM2500',
        'capabilities': {'thrust': 80_000, 'fuel_efficiency': 0.68, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 110, 'mttr': 9},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-156-SM-2ER', 80), ('RIM-162-ESSM', 16)],
        'MISSILES_ASM': [('RGM-84-Harpoon', 8), ('BGM-109-Tomahawk', 26)],
        'MISSILES_TORPEDO': [('Mk-46', 6)],
        'GUNS':         [('Mk-45-5in', 600), ('Mk-45-5in', 600)],   # 2 cannoni
        'CIWS':         [('Mk-15-Phalanx', 2)],
    },
    'radar': {
        'model':        'AN/SPY-1A AEGIS',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 550, 'tracking_range': 500, 'engagement_range': 350, 'multi_target_capacity': 20}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 130, 'tracking_range': 110, 'engagement_range': 90,  'multi_target_capacity': 12}),
        },
        'reliability': {'mtbf': 140, 'mttr': 6},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.55},
        'max':       {'metric': 'nautical', 'speed': 32, 'consume': 0.9},
        'flank':     {'metric': 'nautical', 'speed': 33, 'consume': 1.3},
    },
}

# ── CGN 1144.2 Piotr Velikiy (Kirov-class, Russia) ───────────────────────────
PiotrVelikiy_data = {
    'constructor':   'Baltic Shipyard',
    'model':         'CGN 1144.2 Piotr Velikiy',
    'made':          'Russia',
    'ship_class':    'Kirov-class',
    'category':      Sea_Asset_Type.CRUISER.value,
    'physical_characteristics': {'length': 252, 'width': 29, 'height': 59, 'weight': 24000},
    'start_service': 1998,
    'end_service':   None,
    'cost':          2.0,
    'range':         14_000,  # nm (propulsione nucleare)
    'roles':         ['AAW', 'ASuW', 'ASW', 'Strike', 'Fleet_Flagship'],
    'engine': {
        'model':        '2x KN-3 Nuclear Reactor + 2x Steam Turbine',
        'capabilities': {'thrust': 140_000, 'fuel_efficiency': 0.9, 'type': 'nuclear'},
        'reliability':  {'mtbf': 200, 'mttr': 30},
    },
    'weapons': {
        'MISSILES_SAM': [('S-300F', 96), ('SA-N-9-Gauntlet', 128)],
        'MISSILES_ASM': [('P-700-Granit', 20)],
        'MISSILES_TORPEDO': [('USET-80', 10)],
        'GUNS':         [('AK-130-130mm', 500), ('AK-100-100mm', 300)],
        'CIWS':         [('AK-630', 6)],
    },
    'radar': {
        'model':        'Fregat-MA + Podkat + Top Pair',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 500, 'tracking_range': 450, 'engagement_range': 280, 'multi_target_capacity': 18}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 120, 'tracking_range': 100, 'engagement_range': 70,  'multi_target_capacity': 10}),
        },
        'reliability': {'mtbf': 80, 'mttr': 15},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 25, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.85},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.2},
    },
}

# ── CG 1164 Moskva (Slava-class, Russia) ─────────────────────────────────────
Moskva_data = {
    'constructor':   'Nosenko Black Sea Shipyard',
    'model':         'CG 1164 Moskva',
    'made':          'Russia',
    'ship_class':    'Slava-class',
    'category':      Sea_Asset_Type.CRUISER.value,
    'physical_characteristics': {'length': 186, 'width': 21, 'height': 34, 'weight': 11500},
    'start_service': 1983,
    'end_service':   None,
    'cost':          0.75,
    'range':         9_000,
    'roles':         ['AAW', 'ASuW', 'Strike', 'Fleet_Flagship'],
    'engine': {
        'model':        'COGAG (4x M70 Gas Turbine)',
        'capabilities': {'thrust': 120_000, 'fuel_efficiency': 0.55, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 60, 'mttr': 18},
    },
    'weapons': {
        'MISSILES_SAM': [('S-300F', 64)],
        'MISSILES_ASM': [('P-1000-Vulkan', 16)],
        'MISSILES_TORPEDO': [('TEST-71', 10)],
        'GUNS':         [('AK-130-130mm', 500)],
        'CIWS':         [('AK-630', 6)],
    },
    'radar': {
        'model':        'MR-800 Voskhod + Top Dome',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 450, 'tracking_range': 400, 'engagement_range': 250, 'multi_target_capacity': 16}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 110, 'tracking_range': 90,  'engagement_range': 60,  'multi_target_capacity': 8}),
        },
        'reliability': {'mtbf': 50, 'mttr': 20},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 24, 'consume': 0.65},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 1.0},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.4},
    },
}


# =============================================================================
# FRIGATES  (Sea_Asset_Type.FRIGATE = 'Frigate')
# =============================================================================

# ── FFG-46 Rentz (Oliver Hazard Perry-class, USA) ────────────────────────────
FFG46_data = {
    'constructor':   'Todd Pacific Shipyards',
    'model':         'FFG-46',
    'made':          'USA',
    'ship_class':    'Oliver Hazard Perry-class',
    'category':      Sea_Asset_Type.FRIGATE.value,
    'physical_characteristics': {'length': 135, 'width': 14, 'height': 18, 'weight': 4100},
    'start_service': 1984,
    'end_service':   2010,
    'cost':          0.35,
    'range':         4_500,
    'roles':         ['AAW', 'ASW', 'ASuW'],
    'engine': {
        'model':        '1x General Electric LM2500',
        'capabilities': {'thrust': 41_000, 'fuel_efficiency': 0.72, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 100, 'mttr': 8},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-66-SM-1', 36)],
        'MISSILES_ASM': [('RGM-84-Harpoon', 4)],
        'MISSILES_TORPEDO': [('Mk-46', 6)],
        'GUNS':         [('OTO-Melara-76mm', 300)],
        'CIWS':         [('Mk-15-Phalanx', 1)],
    },
    'radar': {
        'model':        'AN/SPS-49 + AN/SPS-55',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 350, 'tracking_range': 300, 'engagement_range': 150, 'multi_target_capacity': 8}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 70,  'tracking_range': 55,  'engagement_range': 30,  'multi_target_capacity': 5}),
        },
        'reliability': {'mtbf': 90, 'mttr': 8},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 25, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 29, 'consume': 0.8},
        'flank':     {'metric': 'nautical', 'speed': 30, 'consume': 1.1},
    },
}

# ── FF 1135M Rezky (Krivak II-class, Russia) ─────────────────────────────────
FF1135M_data = {
    'constructor':   'Yantar Shipyard',
    'model':         'FF 1135M Rezky',
    'made':          'Russia',
    'ship_class':    'Krivak II-class',
    'category':      Sea_Asset_Type.FRIGATE.value,
    'physical_characteristics': {'length': 123, 'width': 14, 'height': 20, 'weight': 3600},
    'start_service': 1974,
    'end_service':   None,
    'cost':          0.15,
    'range':         4_000,
    'roles':         ['ASW', 'ASuW'],
    'engine': {
        'model':        'COGAG (2x M8K + 2x M62)',
        'capabilities': {'thrust': 72_000, 'fuel_efficiency': 0.5, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 55, 'mttr': 15},
    },
    'weapons': {
        'MISSILES_SAM': [('SA-N-4-Gecko', 40)],
        'MISSILES_ASM': [('URK-5-Rastrub', 4)],
        'MISSILES_TORPEDO': [('USET-80', 8)],
        'GUNS':         [('AK-100-100mm', 320)],
        'CIWS':         [('AK-630', 2)],
    },
    'radar': {
        'model':        'Head Net-C + Eye Bowl',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 250, 'tracking_range': 200, 'engagement_range': 100, 'multi_target_capacity': 6}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 60,  'tracking_range': 50,  'engagement_range': 30,  'multi_target_capacity': 4}),
        },
        'reliability': {'mtbf': 40, 'mttr': 18},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 26, 'consume': 0.55},
        'max':       {'metric': 'nautical', 'speed': 30, 'consume': 0.9},
        'flank':     {'metric': 'nautical', 'speed': 32, 'consume': 1.3},
    },
}

# ── FFG 11540 Neustrashimy (Russia) ──────────────────────────────────────────
FFG11540_data = {
    'constructor':   'Yantar Shipyard',
    'model':         'FFG 11540 Neustrashimy',
    'made':          'Russia',
    'ship_class':    'Neustrashimy-class',
    'category':      Sea_Asset_Type.FRIGATE.value,
    'physical_characteristics': {'length': 131, 'width': 15, 'height': 22, 'weight': 4400},
    'start_service': 1993,
    'end_service':   None,
    'cost':          0.30,
    'range':         3_500,
    'roles':         ['ASW', 'ASuW', 'AAW'],
    'engine': {
        'model':        'COGAG (2x M70 + 2x M62)',
        'capabilities': {'thrust': 56_000, 'fuel_efficiency': 0.6, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 70, 'mttr': 12},
    },
    'weapons': {
        'MISSILES_SAM': [('SA-N-9-Gauntlet', 32)],
        'MISSILES_ASM': [('URK-5-Rastrub', 8)],
        'MISSILES_TORPEDO': [('USET-80', 6)],
        'GUNS':         [('AK-100-100mm', 320)],
        'CIWS':         [('AK-630', 2)],
    },
    'radar': {
        'model':        'Fregat-MA + Mineral-ME',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 300, 'tracking_range': 250, 'engagement_range': 140, 'multi_target_capacity': 10}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80,  'tracking_range': 65,  'engagement_range': 40,  'multi_target_capacity': 6}),
        },
        'reliability': {'mtbf': 60, 'mttr': 14},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 25, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 28, 'consume': 0.8},
        'flank':     {'metric': 'nautical', 'speed': 30, 'consume': 1.2},
    },
}

# ── Type 054A (Jiangkai II-class, China) ─────────────────────────────────────
Type054A_data = {
    'constructor':   'Hudong-Zhonghua Shipbuilding',
    'model':         'Type 054A',
    'made':          'China',
    'ship_class':    'Jiangkai II-class',
    'category':      Sea_Asset_Type.FRIGATE.value,
    'physical_characteristics': {'length': 134, 'width': 16, 'height': 20, 'weight': 4000},
    'start_service': 2008,
    'end_service':   None,
    'cost':          0.35,
    'range':         3_800,
    'roles':         ['AAW', 'ASW', 'ASuW'],
    'engine': {
        'model':        'CODAD (4x MTU 20V 956 diesel)',
        'capabilities': {'thrust': 29_000, 'fuel_efficiency': 0.68, 'type': 'diesel'},
        'reliability':  {'mtbf': 90, 'mttr': 10},
    },
    'weapons': {
        'MISSILES_SAM': [('HHQ-16', 32)],
        'MISSILES_ASM': [('YJ-83', 8)],
        'MISSILES_TORPEDO': [('Type-93', 6)],
        'GUNS':         [('OTO-Melara-76mm', 300)],
        'CIWS':         [('Type-730', 1)],
    },
    'radar': {
        'model':        'Type 382 + MR-36 Podkat',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 280, 'tracking_range': 230, 'engagement_range': 120, 'multi_target_capacity': 10}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 70,  'tracking_range': 55,  'engagement_range': 35,  'multi_target_capacity': 6}),
        },
        'reliability': {'mtbf': 80, 'mttr': 11},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 22, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 25, 'consume': 0.75},
        'flank':     {'metric': 'nautical', 'speed': 27, 'consume': 1.1},
    },
}


# =============================================================================
# CORVETTES  (Sea_Asset_Type.CORVETTE = 'Corvette')
# corrispondono alla categoria 'Fast Attack' nel dizionario navi
# =============================================================================

# ── FFL 1124.4 Grisha (Grisha V-class, Russia) ───────────────────────────────
FFL1124_data = {
    'constructor':   'Zelenodolsk Shipyard',
    'model':         'FFL 1124.4 Grisha',
    'made':          'Russia',
    'ship_class':    'Grisha V-class',
    'category':      Sea_Asset_Type.CORVETTE.value,
    'physical_characteristics': {'length': 71, 'width': 10, 'height': 15, 'weight': 950},
    'start_service': 1975,
    'end_service':   None,
    'cost':          0.08,
    'range':         2_000,
    'roles':         ['ASW', 'Patrol'],
    'engine': {
        'model':        'CODAG (1x Gas Turbine + 2x Diesel)',
        'capabilities': {'thrust': 15_000, 'fuel_efficiency': 0.65, 'type': 'codag'},
        'reliability':  {'mtbf': 50, 'mttr': 12},
    },
    'weapons': {
        'MISSILES_SAM': [('SA-N-4-Gecko', 20)],
        'MISSILES_TORPEDO': [('USET-80', 4)],
        'GUNS':         [('AK-176-76mm', 350)],
        'CIWS':         [('AK-630', 2)],
    },
    'radar': {
        'model':        'Strut Curve + Muff Cob',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 150, 'tracking_range': 120, 'engagement_range': 70,  'multi_target_capacity': 4}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 40,  'tracking_range': 30,  'engagement_range': 20,  'multi_target_capacity': 3}),
        },
        'reliability': {'mtbf': 35, 'mttr': 16},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 26, 'consume': 0.6},
        'max':       {'metric': 'nautical', 'speed': 32, 'consume': 0.9},
        'flank':     {'metric': 'nautical', 'speed': 34, 'consume': 1.4},
    },
}

# ── FSG 1241.1MP Molniya (Tarantul III-class, Russia) ────────────────────────
FSG1241_data = {
    'constructor':   'Rybinsk Shipyard',
    'model':         'FSG 1241.1MP Molniya',
    'made':          'Russia',
    'ship_class':    'Tarantul III-class',
    'category':      Sea_Asset_Type.CORVETTE.value,
    'physical_characteristics': {'length': 56, 'width': 11, 'height': 12, 'weight': 455},
    'start_service': 1981,
    'end_service':   None,
    'cost':          0.05,
    'range':         1_500,
    'roles':         ['ASuW', 'Patrol'],
    'engine': {
        'model':        'COGAG (2x NK-12MV Gas Turbine)',
        'capabilities': {'thrust': 24_000, 'fuel_efficiency': 0.55, 'type': 'gas_turbine'},
        'reliability':  {'mtbf': 40, 'mttr': 14},
    },
    'weapons': {
        'MISSILES_ASM': [('P-270-Moskit', 4)],
        'MISSILES_SAM': [('SA-N-4-Gecko', 16)],
        'GUNS':         [('AK-176-76mm', 300)],
        'CIWS':         [('AK-630', 2)],
    },
    'radar': {
        'model':        'Band Stand + Bass Tilt',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 130, 'tracking_range': 100, 'engagement_range': 60,  'multi_target_capacity': 3}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 50,  'tracking_range': 40,  'engagement_range': 25,  'multi_target_capacity': 2}),
        },
        'reliability': {'mtbf': 30, 'mttr': 18},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 28, 'consume': 0.7},
        'max':       {'metric': 'nautical', 'speed': 34, 'consume': 1.0},
        'flank':     {'metric': 'nautical', 'speed': 36, 'consume': 1.5},
    },
}


# =============================================================================
# SUBMARINES  (Sea_Asset_Type.SUBMARINE = 'Submarine')
# =============================================================================

# ── Type 093 (Shang-class, China) ─────────────────────────────────────────────
Type093_data = {
    'constructor':   'Huludao Shipyard',
    'model':         'Type 093',
    'made':          'China',
    'ship_class':    'Shang-class',
    'category':      Sea_Asset_Type.SUBMARINE.value,
    'physical_characteristics': {'length': 107, 'width': 11, 'height': 10, 'weight': 6000},
    'start_service': 2006,
    'end_service':   None,
    'cost':          1.5,
    'range':         20_000,   # nm (nucleare)
    'roles':         ['ASW', 'ASuW', 'Strike', 'Intelligence'],
    'engine': {
        'model':        '1x Nuclear Reactor + 2x Steam Turbine',
        'capabilities': {'thrust': 50_000, 'fuel_efficiency': 1.0, 'type': 'nuclear'},
        'reliability':  {'mtbf': 200, 'mttr': 20},
    },
    'weapons': {
        'MISSILES_ASM': [('YJ-18', 6)],
        'MISSILES_TORPEDO': [('Type-93', 20), ('Mk-48', 4)],
    },
    'radar': {
        'model':        'None (passive sonar primary)',
        'capabilities': {
            'air':    (False, {}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 80, 'tracking_range': 60, 'engagement_range': 40, 'multi_target_capacity': 4}),
        },
        'reliability': {'mtbf': 150, 'mttr': 10},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 18, 'consume': 0.4},  # submerged
        'max':       {'metric': 'nautical', 'speed': 28, 'consume': 0.8},
        'flank':     {'metric': 'nautical', 'speed': 30, 'consume': 1.2},
    },
}


# =============================================================================
# AMPHIBIOUS ASSAULT SHIPS  (Sea_Asset_Type.AMPHIBIOUS_ASSAULT_SHIP = 'Amphibious_Assault_Ship')
# =============================================================================

# ── LHA-1 Tarawa (Tarawa-class, USA) ─────────────────────────────────────────
LHA1_data = {
    'constructor':   'Ingalls Shipbuilding',
    'model':         'LHA-1 Tarawa',
    'made':          'USA',
    'ship_class':    'Tarawa-class',
    'category':      Sea_Asset_Type.AMPHIBIOUS_ASSAULT_SHIP.value,
    'physical_characteristics': {'length': 250, 'width': 32, 'height': 50, 'weight': 39000},
    'start_service': 1976,
    'end_service':   2011,
    'cost':          0.25,
    'range':         10_000,
    'roles':         ['Amphibious_Assault', 'STOVL_Carrier', 'Command'],
    'engine': {
        'model':        '2x Westinghouse Steam Turbine',
        'capabilities': {'thrust': 70_000, 'fuel_efficiency': 0.5, 'type': 'steam'},
        'reliability':  {'mtbf': 75, 'mttr': 18},
    },
    'weapons': {
        'MISSILES_SAM': [('RIM-7M-Sea-Sparrow', 8)],
        'GUNS':         [('OTO-Melara-76mm', 300), ('Mk-45-5in', 250)],
        'CIWS':         [('Mk-15-Phalanx', 2)],
    },
    'radar': {
        'model':        'AN/SPS-52 + AN/SPS-67',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 300, 'tracking_range': 250, 'engagement_range': 0, 'multi_target_capacity': 6}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 60,  'tracking_range': 50,  'engagement_range': 0, 'multi_target_capacity': 4}),
        },
        'reliability': {'mtbf': 80, 'mttr': 12},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 20, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 23, 'consume': 0.75},
        'flank':     {'metric': 'nautical', 'speed': 24, 'consume': 1.1},
    },
}

# ── Type 071 (Yuzhao-class, China) ───────────────────────────────────────────
Type071_data = {
    'constructor':   'Hudong-Zhonghua Shipbuilding',
    'model':         'Type 071',
    'made':          'China',
    'ship_class':    'Yuzhao-class',
    'category':      Sea_Asset_Type.AMPHIBIOUS_ASSAULT_SHIP.value,
    'physical_characteristics': {'length': 210, 'width': 28, 'height': 35, 'weight': 20000},
    'start_service': 2007,
    'end_service':   None,
    'cost':          0.30,
    'range':         6_000,
    'roles':         ['Amphibious_Assault', 'Troop_Transport', 'Command'],
    'engine': {
        'model':        '4x SEMT Pielstick 16 PC2.6 diesel',
        'capabilities': {'thrust': 48_000, 'fuel_efficiency': 0.62, 'type': 'diesel'},
        'reliability':  {'mtbf': 80, 'mttr': 12},
    },
    'weapons': {
        'MISSILES_SAM': [('HHQ-7', 8)],
        'GUNS':         [('AK-176-76mm', 300)],
        'CIWS':         [('Type-730', 1)],
    },
    'radar': {
        'model':        'Type 360 + Type 364',
        'capabilities': {
            'air':    (True,  {'acquisition_range': 200, 'tracking_range': 160, 'engagement_range': 0, 'multi_target_capacity': 5}),
            'ground': (False, {}),
            'sea':    (True,  {'acquisition_range': 50,  'tracking_range': 40,  'engagement_range': 0, 'multi_target_capacity': 3}),
        },
        'reliability': {'mtbf': 70, 'mttr': 13},
    },
    'speed_data': {
        'sustained': {'metric': 'nautical', 'speed': 18, 'consume': 0.5},
        'max':       {'metric': 'nautical', 'speed': 20, 'consume': 0.75},
        'flank':     {'metric': 'nautical', 'speed': 21, 'consume': 1.1},
    },
}


# ── ISTANZIAZIONE ────────────────────────────────────────────────────────────
# Carrier
Ship_Data(**CVN70_data)
Ship_Data(**CVN71_data)
Ship_Data(**CVN72_data)
Ship_Data(**CVN73_data)
Ship_Data(**CVN74_data)
Ship_Data(**CVN75_data)
Ship_Data(**CV59_data)
Ship_Data(**KuznetsovAdmiral_data)
# Destroyer
Ship_Data(**ArleighBurke_data)
Ship_Data(**Type052B_data)
Ship_Data(**Type052C_data)
# Cruiser
Ship_Data(**CG65_data)
Ship_Data(**PiotrVelikiy_data)
Ship_Data(**Moskva_data)
# Frigate
Ship_Data(**FFG46_data)
Ship_Data(**FF1135M_data)
Ship_Data(**FFG11540_data)
Ship_Data(**Type054A_data)
# Corvette (Fast Attack)
Ship_Data(**FFL1124_data)
Ship_Data(**FSG1241_data)
# Submarine
Ship_Data(**Type093_data)
# Amphibious Assault Ship
Ship_Data(**LHA1_data)
Ship_Data(**Type071_data)


# ── CALCOLO SCORE ────────────────────────────────────────────────────────────

SHIP: Dict[str, Dict] = {}

for ship in Ship_Data._registry.values():
    model = ship.model
    SHIP[model] = {
        'combat score':                 {'global_score': ship.get_normalized_combat_score(),       'category_score': ship.get_normalized_combat_score(category=ship.category)},
        'weapon score':                 {'global_score': ship.get_normalized_weapon_score(),        'category_score': ship.get_normalized_weapon_score(category=ship.category)},
        'radar score':                  {'global_score': ship.get_normalized_radar_score(),         'category_score': ship.get_normalized_radar_score(category=ship.category)},
        'radar score air':              {'global_score': ship.get_normalized_radar_score(modes=['air']),        'category_score': ship.get_normalized_radar_score(modes=['air'], category=ship.category)},
        'radar score sea':              {'global_score': ship.get_normalized_radar_score(modes=['sea']),        'category_score': ship.get_normalized_radar_score(modes=['sea'], category=ship.category)},
        'speed score':                  {'global_score': ship.get_normalized_speed_score(),         'category_score': ship.get_normalized_speed_score(category=ship.category)},
        'range score':                  {'global_score': ship.get_normalized_range_score(),         'category_score': ship.get_normalized_range_score(category=ship.category)},
        'avalaibility':                 {'global_score': ship.get_normalized_avalaiability_score(), 'category_score': ship.get_normalized_avalaiability_score(category=ship.category)},
        'manutenability score (mttr)':  {'global_score': ship.get_normalized_maintenance_score(),   'category_score': ship.get_normalized_maintenance_score(category=ship.category)},
        'reliability score (mtbf)':     {'global_score': ship.get_normalized_reliability_score(),   'category_score': ship.get_normalized_reliability_score(category=ship.category)},
    }


# ── API PUBBLICHE ─────────────────────────────────────────────────────────────

def get_ship_data(model: str) -> Dict:
    """Restituisce tutti gli score calcolati per una specifica nave.

    Args:
        model: nome del modello (chiave nel registro)

    Raises:
        ValueError: se il modello non è presente nel registro

    Returns:
        Dict: score della nave
    """
    if model not in SHIP:
        raise ValueError(f"model unknown. Available models: {list(SHIP.keys())}")
    return SHIP[model]


def get_ship_scores(model: str, scores: Optional[List] = None) -> Dict:
    """Restituisce gli score specificati per una nave.

    Args:
        model:  nome del modello
        scores: lista di score da restituire (default: tutti i SCORES)

    Raises:
        ValueError: modello o score non riconosciuto

    Returns:
        Dict: score richiesti
    """
    if model not in SHIP:
        raise ValueError(f"model unknown. Available models: {list(SHIP.keys())}")

    if scores is None:
        scores = list(SCORES)

    invalid = [s for s in scores if s not in SCORES]
    if invalid:
        raise ValueError(f"Unknown scores: {invalid!r}. Valid scores: {SCORES!r}")

    return {score: SHIP[model][score] for score in scores}
