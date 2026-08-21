from heapq import heappush, heappop
from typing import Optional
from Code.Dynamic_War_Manager.Source.DataType.Edge import Edge
from Code.Dynamic_War_Manager.Source.DataType.Waypoint import Waypoint
from sympy import Point3D
from Code.Dynamic_War_Manager.Source.Context.Context import ROUTE_TYPE
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger

# LOGGING
logger = Logger(module_name=__name__, class_name='Route')


class Route:

    def __init__(self, route_type: str, edges: dict, name: str | None):

        # properties
        self._name = name
        self._route_type = route_type  # air, ground, water
        self._edges = edges            # edges = { (wpA, wpB): Edge }

        # validate before using edges
        check_results = self.checkParam(name=name, route_type=route_type, edges=edges)
        if not check_results[0]:
            raise Exception(check_results[1] + ". Object not instantiated.")

        self._waypoints = self.getWaypoints()

    @staticmethod
    def checkParam(name: str = None, route_type: str = None, edges: dict = None) -> tuple:
        """Return (True, 'OK') if parameters are type-compliant, else (False, error_message)."""
        if name is not None and not isinstance(name, str):
            return (False, "Bad Arg: name must be a str")
        if route_type is not None and route_type not in ROUTE_TYPE:
            return (False, f"Bad Arg: route_type must be one of: {ROUTE_TYPE}")
        if edges is not None and (
            not isinstance(edges, dict) or
            not all(isinstance(v, Edge) for v in edges.values())
        ):
            return (False, "Bad Arg: edges must be a dict with Edge values: { (wpA, wpB): Edge }")
        return (True, "OK")

    def getWaypoints(self) -> list:
        queue = []
        for v in self._edges.values():
            heappush(queue, (v.wpA.name, v.wpA))
            heappush(queue, (v.wpB.name, v.wpB))
        return queue

    # PROPERTIES

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, param):
        check_result = self.checkParam(name=param)
        if not check_result[0]:
            raise Exception(check_result[1])
        self._name = param

    @property
    def route_type(self) -> str:
        return self._route_type

    @route_type.setter
    def route_type(self, param):
        check_result = self.checkParam(route_type=param)
        if not check_result[0]:
            raise Exception(check_result[1])
        self._route_type = param

    @property
    def edges(self) -> dict:
        return self._edges

    @edges.setter
    def edges(self, param):
        check_result = self.checkParam(edges=param)
        if not check_result[0]:
            raise Exception(check_result[1])
        self._edges = param

    # METHODS

    def minDistance(self, point: Point3D) -> float:
        min_distance = float('inf')
        for v in self._edges.values():
            md = v.minDistance(point)
            if md < min_distance:
                min_distance = md
        return min_distance

    def travelTime(self, speed: Optional[float] = None) -> float:
        """Total travel time across all edges. If speed is given, overrides each edge's own speed."""
        return sum(v.calcTravelTime(speed) for v in self._edges.values())

    def travelTimeToEdge(self, edge: Edge) -> float:
        """Cumulative travel time up to (but not including) the given edge."""
        travel_time = 0.0
        for v in self._edges.values():
            if v == edge:
                return travel_time
            travel_time += v.calcTravelTime()
        return travel_time

    def length(self) -> float:
        return sum(v.calcLength() for v in self._edges.values())

    def max_danger_level(self) -> float:
        if not self._edges:
            return 0
        return max(v.danger_level for v in self._edges.values())

    def min_danger_level(self) -> float:
        if not self._edges:
            return 0
        return min(v.danger_level for v in self._edges.values())

    def avg_danger_level(self) -> float:
        danger_values = [v.danger_level for v in self._edges.values() if v.danger_level > 0.0]
        return sum(danger_values) / len(danger_values) if danger_values else 0.0

    def max_speed(self) -> float:
        if not self._edges:
            return 0.0
        return max(v.speed for v in self._edges.values())

    def avg_speed(self) -> float:
        if not self._edges:
            return 0.0
        return sum(v.speed for v in self._edges.values()) / len(self._edges)

    def __str__(self) -> str:
        return (
            f"Route {self.name} - Type: {self.route_type}, "
            f"Length: {self.length():.2f}, "
            f"Travel Time: {self.travelTime():.2f}, "
            f"Max Danger Level: {self.max_danger_level()}, "
            f"Avg Danger Level: {self.avg_danger_level():.2f}, "
            f"Max Speed: {self.max_speed():.2f}, "
            f"Avg Speed: {self.avg_speed():.2f}"
        )

    def __repr__(self) -> str:
        return self.__str__()
