import unittest
from datetime import date, time

from Code.Dynamic_War_Manager.Source.Logic import Meteo_Analysis


class TestIsDaylight(unittest.TestCase):
    def test_midday_is_daylight(self):
        self.assertTrue(Meteo_Analysis.is_daylight(time(12, 0)))

    def test_midnight_is_not_daylight(self):
        self.assertFalse(Meteo_Analysis.is_daylight(time(0, 0)))

    def test_boundary_start_hour_is_daylight(self):
        self.assertTrue(Meteo_Analysis.is_daylight(time(Meteo_Analysis.DAY_START_HOUR, 0)))

    def test_boundary_end_hour_is_not_daylight(self):
        self.assertFalse(Meteo_Analysis.is_daylight(time(Meteo_Analysis.DAY_END_HOUR, 0)))

    def test_non_time_raises_type_error(self):
        with self.assertRaises(TypeError):
            Meteo_Analysis.is_daylight("12:00")


class TestHasAdverseWeather(unittest.TestCase):
    def test_summer_month_never_adverse(self):
        for day in range(1, 29):
            self.assertFalse(Meteo_Analysis.has_adverse_weather("Caucasus", date(2026, 7, day)))

    def test_winter_month_is_deterministic(self):
        first = Meteo_Analysis.has_adverse_weather("Caucasus", date(2026, 1, 10))
        second = Meteo_Analysis.has_adverse_weather("Caucasus", date(2026, 1, 10))
        self.assertEqual(first, second)

    def test_different_region_name_can_change_result(self):
        # Non garantito in generale, ma per queste due stringhe la somma dei codici carattere
        # ha parità diversa: verifica che il nome regione entri davvero nel calcolo.
        a = Meteo_Analysis.has_adverse_weather("Caucasus", date(2026, 1, 10))
        b = Meteo_Analysis.has_adverse_weather("Nevada", date(2026, 1, 10))
        self.assertNotEqual(a, b)

    def test_empty_region_name_raises_type_error(self):
        with self.assertRaises(TypeError):
            Meteo_Analysis.has_adverse_weather("", date(2026, 1, 10))

    def test_non_date_raises_type_error(self):
        with self.assertRaises(TypeError):
            Meteo_Analysis.has_adverse_weather("Caucasus", "2026-01-10")


class TestGetMeteoConditions(unittest.TestCase):
    def test_shape_matches_usability_dict(self):
        conditions = Meteo_Analysis.get_meteo_conditions("Caucasus", date(2026, 7, 15), time(12, 0))
        self.assertEqual(set(conditions.keys()), {'day', 'night', 'adverse_weather'})
        self.assertTrue(all(isinstance(v, bool) for v in conditions.values()))

    def test_day_and_night_are_mutually_exclusive(self):
        day_conditions = Meteo_Analysis.get_meteo_conditions("Caucasus", date(2026, 7, 15), time(12, 0))
        night_conditions = Meteo_Analysis.get_meteo_conditions("Caucasus", date(2026, 7, 15), time(2, 0))
        self.assertTrue(day_conditions['day'] and not day_conditions['night'])
        self.assertTrue(night_conditions['night'] and not night_conditions['day'])

    def test_deterministic_across_calls(self):
        first = Meteo_Analysis.get_meteo_conditions("Nevada", date(2026, 12, 20), time(3, 0))
        second = Meteo_Analysis.get_meteo_conditions("Nevada", date(2026, 12, 20), time(3, 0))
        self.assertEqual(first, second)


if __name__ == '__main__':
    unittest.main()
