from __future__ import annotations

import json
import pathlib
from datetime import date as _date, time as _time
from typing import Any, Dict, List, Optional, Tuple

from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

logger = Logger(module_name=__name__, class_name='CampaignHistory').logger


class CampaignHistory:
    """
    Stores status_report snapshots for every block in every region, indexed by mission.

    La usi per le valutazioni strategiche e tattiche dopo ogni missione, per tenere traccia dell'evoluzione della campagna e per analizzare trend e pattern nei dati storici.

    Internal structure:
        _history: {
            mission_id: {
                "date":    str,    # ISO 8601 "YYYY-MM-DD"
                "time":    str,    # "HH:MM" or "HH:MM:SS"
                "regions": {
                    region_name: {
                        block_id: status_report_dict
                    }
                }
            }
        }

      ---
  Context/Campaign_History.py

  Struttura dati interna

  _history[mission_id] → { date, time, regions → { region_name → { block_id →
  status_report } } }                                                           
   
  API Write                                                                     

  ┌────────────────────────────────────────┬────────────────────────────────┐
  │                 Metodo                 │          Descrizione           │
  ├────────────────────────────────────────┼────────────────────────────────┤
  │                                        │ Aggiunge il report di un       │
  │ add_block_snapshot(mission_id, date,   │ singolo blocco; crea la        │
  │ time, region, block_id, report)        │ missione se non esiste; rileva │
  │                                        │  conflitti di data/ora         │
  ├────────────────────────────────────────┼────────────────────────────────┤
  │ add_region_snapshot(mission_id, date,  │ Aggiunge tutti i blocchi di    │
  │ time, region, blocks)                  │ una regione in un colpo        │
  │                                        │ ({block_id: report})           │
  └────────────────────────────────────────┴────────────────────────────────┘

  API Read

  ┌─────────────────────────────────────┬───────────────────────────────────┐
  │               Metodo                │              Ritorna              │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ missions                            │ Lista di mission_id in ordine di  │
  │                                     │ inserimento                       │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ get_mission(mission_id)             │ Snapshot completo della missione  │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ get_region_snapshot(mission_id,     │ {block_id: report} per una        │
  │ region)                             │ regione                           │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ get_block_snapshot(mission_id,      │ Report singolo o None             │
  │ region, block_id)                   │                                   │
  ├─────────────────────────────────────┼───────────────────────────────────┤
  │ get_block_history(region, block_id) │ Lista (mission_id, date, time,    │
  │                                     │ report) ordinata cronologicamente │
  ├─────────────────────────────────────┼───────────────────────────────────┤   
  │ get_field_trend(region, block_id,   │ Lista (mission_id, date, time,    │
  │ field)                              │ valore) per analisi trend (es.    │   
  │                                     │ "efficiency", "state")            │   
  └─────────────────────────────────────┴───────────────────────────────────┘
                                                                                
  Persistenza                                               

  ch.save("campaign_history.json")          # serializza su file JSON
  ch2 = CampaignHistory.load("campaign_history.json")  # ricarica      







    """

    def __init__(self) -> None:
        self._history: Dict[str, Dict] = {}

    # ------------------------------------------------------------------ #
    # Write API                                                            #
    # ------------------------------------------------------------------ #

    def add_block_snapshot(
        self,
        mission_id: str,
        date: str,
        time: str,
        region_name: str,
        block_id: str,
        status_report: Dict[str, Any],
    ) -> None:
        """Register the status_report of one block for a given mission.

        If the mission does not yet exist it is created with the supplied
        date/time.  Supplying a different date or time for an already
        registered mission raises ValueError.
        """
        self._validate_mission_id(mission_id)
        self._validate_date(date)
        self._validate_time(time)
        self._validate_str(region_name, "region_name")
        self._validate_str(block_id, "block_id")
        self._validate_status_report(status_report)

        if mission_id not in self._history:
            self._history[mission_id] = {"date": date, "time": time, "regions": {}}
        else:
            entry = self._history[mission_id]
            if entry["date"] != date or entry["time"] != time:
                raise ValueError(
                    f"Mission '{mission_id}' is already registered with "
                    f"date={entry['date']} time={entry['time']}. "
                    f"Conflicting values: date={date} time={time}."
                )

        regions = self._history[mission_id]["regions"]
        if region_name not in regions:
            regions[region_name] = {}
        regions[region_name][block_id] = status_report
        logger.debug(
            "Snapshot added: mission=%s region=%s block=%s", mission_id, region_name, block_id
        )

    def add_region_snapshot(
        self,
        mission_id: str,
        date: str,
        time: str,
        region_name: str,
        blocks: Dict[str, Dict[str, Any]],
    ) -> None:
        """Register status_reports for all blocks in a region at once.

        Args:
            blocks: mapping {block_id: status_report}.
        """
        if not isinstance(blocks, dict):
            raise TypeError(f"blocks must be a dict, got {type(blocks).__name__}.")
        for block_id, report in blocks.items():
            self.add_block_snapshot(mission_id, date, time, region_name, block_id, report)

    # ------------------------------------------------------------------ #
    # Read API                                                             #
    # ------------------------------------------------------------------ #

    @property
    def missions(self) -> List[str]:
        """Mission IDs in insertion order."""
        return list(self._history.keys())

    def get_mission(self, mission_id: str) -> Dict:
        """Return the full snapshot dict for a mission.

        Raises:
            KeyError: if mission_id is not in history.
        """
        self._validate_mission_id(mission_id)
        if mission_id not in self._history:
            raise KeyError(f"Mission '{mission_id}' not found in history.")
        return self._history[mission_id]

    def get_region_snapshot(self, mission_id: str, region_name: str) -> Dict[str, Dict]:
        """Return {block_id: status_report} for a region in a mission.

        Returns an empty dict if the region was not recorded for that mission.
        """
        self._validate_str(region_name, "region_name")
        return self.get_mission(mission_id)["regions"].get(region_name, {})

    def get_block_snapshot(
        self, mission_id: str, region_name: str, block_id: str
    ) -> Optional[Dict[str, Any]]:
        """Return the status_report of a block in a given mission, or None."""
        self._validate_str(block_id, "block_id")
        return self.get_region_snapshot(mission_id, region_name).get(block_id)

    def get_block_history(
        self, region_name: str, block_id: str
    ) -> List[Tuple[str, str, str, Dict[str, Any]]]:
        """Return all snapshots of a block across missions, sorted by date then time.

        Returns:
            List of (mission_id, date, time, status_report).
        """
        self._validate_str(region_name, "region_name")
        self._validate_str(block_id, "block_id")
        result = [
            (mid, data["date"], data["time"], data["regions"][region_name][block_id])
            for mid, data in self._history.items()
            if block_id in data["regions"].get(region_name, {})
        ]
        result.sort(key=lambda x: (x[1], x[2]))
        return result

    def get_field_trend(
        self, region_name: str, block_id: str, field: str
    ) -> List[Tuple[str, str, str, Any]]:
        """Return the value of one report field across all missions, sorted chronologically.

        Returns:
            List of (mission_id, date, time, field_value).
        """
        if not isinstance(field, str) or not field:
            raise TypeError("field must be a non-empty string.")
        return [
            (mid, d, t, report.get(field))
            for mid, d, t, report in self.get_block_history(region_name, block_id)
        ]

    def __len__(self) -> int:
        return len(self._history)

    def __contains__(self, mission_id: str) -> bool:
        return mission_id in self._history

    def __repr__(self) -> str:
        return f"CampaignHistory(missions={len(self)}, ids={self.missions})"

    # ------------------------------------------------------------------ #
    # Persistence                                                          #
    # ------------------------------------------------------------------ #

    def save(self, path: str) -> None:
        """Serialize the full history to a JSON file (UTF-8)."""
        if not isinstance(path, str) or not path:
            raise TypeError("path must be a non-empty string.")
        pathlib.Path(path).write_text(
            json.dumps(self._history, default=str, indent=2), encoding="utf-8"
        )
        logger.info("CampaignHistory saved to %s (%d missions).", path, len(self))

    @classmethod
    def load(cls, path: str) -> "CampaignHistory":
        """Load a CampaignHistory from a JSON file produced by save().

        Returns a new CampaignHistory instance.
        """
        if not isinstance(path, str) or not path:
            raise TypeError("path must be a non-empty string.")
        instance = cls()
        instance._history = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        logger.info("CampaignHistory loaded from %s (%d missions).", path, len(instance))
        return instance

    # ------------------------------------------------------------------ #
    # Validation helpers                                                   #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_mission_id(mission_id: str) -> None:
        if not isinstance(mission_id, str) or not mission_id:
            raise TypeError("mission_id must be a non-empty string.")

    @staticmethod
    def _validate_date(date: str) -> None:
        try:
            _date.fromisoformat(date)
        except (TypeError, ValueError):
            raise ValueError(
                f"date must be ISO 8601 format 'YYYY-MM-DD', got: {date!r}."
            )

    @staticmethod
    def _validate_time(time: str) -> None:
        try:
            _time.fromisoformat(time)
        except (TypeError, ValueError):
            raise ValueError(
                f"time must be 'HH:MM' or 'HH:MM:SS' format, got: {time!r}."
            )

    @staticmethod
    def _validate_str(value: str, name: str) -> None:
        if not isinstance(value, str) or not value:
            raise TypeError(f"{name} must be a non-empty string.")

    @staticmethod
    def _validate_status_report(report: Any) -> None:
        if not isinstance(report, dict):
            raise TypeError(
                f"status_report must be a dict, got {type(report).__name__}."
            )
