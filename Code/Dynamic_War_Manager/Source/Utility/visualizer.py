"""
Utility di debug per la visualizzazione 2D/3D delle minacce (ThreatAA/Cylinder) e delle
rotte (Route) calcolate da Air_Route_Manager. Serve per definire/verificare a colpo
d'occhio gli scenari usati nei test (vedi Test_Air_Route_Manager.py) prima di scriverli.
"""
import os
import matplotlib
import matplotlib.pyplot as plt

# Prova un backend interattivo per la visualizzazione a schermo; se nessuno e'
# disponibile nell'ambiente corrente (es. ne' tkinter ne' Qt installati) ripiega su
# 'Agg' (sempre disponibile, non interattivo: figure() e savefig() funzionano comunque,
# show() diventa un no-op) invece di rompere l'import del modulo o lasciare che
# matplotlib tenti da solo, in modo rumoroso, altri backend a caso al primo utilizzo.
# matplotlib.use() puo' "riuscire" senza sollevare eccezioni ma fallire solo dopo,
# alla prima vera creazione di una figura (import differito del toolkit grafico) -
# quindi la verifica va fatta creando e chiudendo davvero una figura di prova.
for _backend in ("TkAgg", "Qt5Agg", "QtAgg", "Agg"):
    try:
        matplotlib.use(_backend)
        _fig = plt.figure()
        plt.close(_fig)
        break
    except Exception:
        continue

import numpy as np


def _cylinder_geometry(cylinder, resolution=30):
    """Estrae la geometria di plotting (base, raggio, altezza) da un DataType.Cylinder reale."""
    base = np.array([float(cylinder.bottom_center.x), float(cylinder.bottom_center.y), float(cylinder.bottom_center.z)])
    theta = np.linspace(0, 2 * np.pi, resolution)
    z = np.array([0, float(cylinder.height)])
    theta_grid, z_grid = np.meshgrid(theta, z)
    x_grid = float(cylinder.radius) * np.cos(theta_grid) + base[0]
    y_grid = float(cylinder.radius) * np.sin(theta_grid) + base[1]
    z_grid = z_grid + base[2]
    return base, x_grid, y_grid, z_grid


def _route_points(route_or_points):
    """Accetta una Route di Air_Route_Manager (via getPoints()) o una lista di punti (x, y, z)."""
    if hasattr(route_or_points, 'getPoints'):
        points = route_or_points.getPoints()
        return [(float(p.x), float(p.y), float(p.z)) for p in points]
    return [(float(p[0]), float(p[1]), float(p[2])) for p in route_or_points]


class Space:
    """Spazio di visualizzazione: raccoglie minacce/cilindri e rotte di uno scenario."""

    def __init__(self, space_x, space_y, space_z):
        self.space_x = space_x
        self.space_y = space_y
        self.space_z = space_z
        self.cylinders = []  # DataType.Cylinder reali
        self.paths = []      # liste di punti (x, y, z)

    def add_threat(self, threat):
        """Aggiunge una minaccia (ThreatAA di Air_Route_Manager) tramite il suo cylinder."""
        self.cylinders.append(threat.cylinder)

    def add_cylinder(self, cylinder):
        """Aggiunge direttamente un DataType.Cylinder reale."""
        self.cylinders.append(cylinder)

    def add_route(self, route):
        """Aggiunge una Route di Air_Route_Manager (via getPoints()) o una lista di punti (x, y, z)."""
        self.paths.append(_route_points(route))

    def _show_or_save(self, fig, out_name):
        """Mostra la figura a schermo se il backend e' interattivo, altrimenti la
        salva su file (nessun ambiente grafico disponibile, es. TkAgg/Qt mancanti)."""
        if matplotlib.get_backend().lower() == 'agg':
            fig.savefig(out_name, dpi=150)
            print(f"Backend non interattivo ({matplotlib.get_backend()}): figura salvata in {os.path.abspath(out_name)}")
        else:
            plt.show()

    def show_3d(self, out_name='visualizer_3d.png'):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        self._draw_3d(ax)
        self._show_or_save(fig, out_name)

    def show_2d_top(self, out_name='visualizer_2d.png'):
        fig, ax = plt.subplots()
        self._draw_2d(ax)
        self._show_or_save(fig, out_name)

    def show_all_views(self, out_name='visualizer_all_views.png'):
        fig = plt.figure()
        ax3d = fig.add_subplot(121, projection='3d')
        self._draw_3d(ax3d)
        ax2d = fig.add_subplot(122)
        self._draw_2d(ax2d)
        self._show_or_save(fig, out_name)

    def _draw_3d(self, ax):
        ax.set_xlim(0, self.space_x)
        ax.set_ylim(0, self.space_y)
        ax.set_zlim(0, self.space_z)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("3D View")

        for cylinder in self.cylinders:
            _, x, y, z = _cylinder_geometry(cylinder)
            ax.plot_surface(x, y, z, alpha=0.6, color='orange', edgecolor='k')

        for points in self.paths:
            xs, ys, zs = zip(*points)
            ax.plot(xs, ys, zs, marker='o', color='blue')

    def _draw_2d(self, ax):
        ax.set_xlim(0, self.space_x)
        ax.set_ylim(0, self.space_y)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("2D Top View (XY Plane)")

        for cylinder in self.cylinders:
            base, _, _, _ = _cylinder_geometry(cylinder)
            circle = plt.Circle((base[0], base[1]), float(cylinder.radius), color='orange', alpha=0.6)
            ax.add_patch(circle)

        for points in self.paths:
            arr = np.array(points)
            ax.plot(arr[:, 0], arr[:, 1], marker='o', color='blue')

        ax.set_aspect('equal', adjustable='box')


if __name__ == "__main__":
    # Esegui questo file direttamente (es. `python visualizer.py`) da qualunque cartella:
    # aggiunge la root del repo a sys.path perche' i moduli del progetto si importano
    # sempre con il path assoluto Code.Dynamic_War_Manager.Source... (vedi CLAUDE.md /
    # feedback_test_patterns), che altrimenti risolve solo quando lo script e' lanciato
    # con `python -m` dalla root del repo.
    import os
    import sys
    _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../'))
    if _repo_root not in sys.path:
        sys.path.insert(0, _repo_root)
    # Logger/Utility.py risolvono la cartella logs/ come 'os.getcwd()/logs' (bug noto,
    # non specifico a questo file - vedi project_fase2_design_decisions.md): ci si
    # sposta sulla root del repo prima di importare qualunque modulo di progetto,
    # cosi' il logging risolve sempre logs/ della repo invece di crashare o crearne
    # una nuova nella cartella da cui e' stato lanciato lo script.
    os.chdir(_repo_root)

    # Esempio: visualizza uno scenario reale calcolato da Air_Route_Manager.RoutePlanner
    from sympy import Point3D
    from Code.Dynamic_War_Manager.Source.Logic.Air_Route_Manager import ThreatAA, RoutePlanner
    from Code.Dynamic_War_Manager.Source.DataType.Cylinder import Cylinder

    start = Point3D(0, 0, 10)
    end = Point3D(80, 80, 10)
    threat = ThreatAA(
        danger_level=2.0, interception_speed=600, min_fire_time=1.0, min_detection_time=7,
        cylinder=Cylinder(Point3D(40, 40, 0), 15, 30)
    )

    planner = RoutePlanner(start, end, [threat])
    route = planner.calcRoute(
        start, end, [threat], aircraft_altitude_route=10,
        aircraft_altitude_min=5, aircraft_altitude_max=20,
        aircraft_speed_max=3, aircraft_speed=2,
        aircraft_range_max=1000, aircraft_time_to_inversion=20,
        change_alt_option="no_change", intersecate_threat=False,
        consider_aircraft_altitude_route=True
    )

    space = Space(space_x=100, space_y=100, space_z=100)
    space.add_threat(threat)
    if route:
        space.add_route(route)

    space.show_all_views()
