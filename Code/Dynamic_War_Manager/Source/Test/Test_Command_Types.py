import unittest
from datetime import date, time

from sympy import Point2D

from Code.Dynamic_War_Manager.Source.Command.Command_Types import RegionInfoReport
from Code.Dynamic_War_Manager.Source.DataType.Payload import Payload


class TestRegionInfoReport(unittest.TestCase):
    def _make_report(self, **overrides):
        defaults = dict(
            region_name="Caucasus",
            side="Blue",
            date=date(2026, 9, 18),
            time=time(12, 0),
            priority={},
            meteo=[{'day': True, 'night': False, 'adverse_weather': False}],
            block_state=[],
            routes={},
            limes=[],
            logistic_center=None,
            combat_power_center={},
            warehouse=Payload(),
            production=Payload(),
            morale=0.0,
        )
        defaults.update(overrides)
        return RegionInfoReport(**defaults)

    def test_construction_holds_all_fields(self):
        report = self._make_report(morale=0.75, logistic_center=Point2D(1, 2))
        self.assertEqual(report.region_name, "Caucasus")
        self.assertEqual(report.side, "Blue")
        self.assertEqual(report.morale, 0.75)
        self.assertEqual(report.logistic_center, Point2D(1, 2))

    def test_is_a_plain_dataclass_not_a_computation(self):
        # RegionInfoReport non deve avere metodi propri oltre a quelli generati da dataclass:
        # ogni calcolo vive in Region.build_info_report / Region stessa.
        own_methods = [
            name for name in vars(RegionInfoReport)
            if not name.startswith('__') and callable(getattr(RegionInfoReport, name))
        ]
        self.assertEqual(own_methods, [])


if __name__ == '__main__':
    unittest.main()
