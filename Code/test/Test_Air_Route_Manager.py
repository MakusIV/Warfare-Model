import sys
import os
import pytest
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# Aggiungi il percorso della directory principale del progetto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from Code.Dynamic_War_Manager.Air_Route_Manager import *



# Configurazione delle minacce
threats = [
    ThreatAA(0.7, 0, Cylinder(Point2D(1,4), 2, 6)),
    ThreatAA(0.7, 0, Cylinder(Point2D(3,7), 3, 20)),
    ThreatAA(0.5, 4, Cylinder(Point2D(6,9), 2, 25)),
    ThreatAA(0.9, 30, Cylinder(Point2D(4,7), 1, 18))
]

# Parametri comuni
params = {
    'range_max': 1000,
    'speed_max': 300,
    'altitude_max': 15,
    'altitude_min': 1
}

def plot_2d_route(route, threats):
    plt.figure(figsize=(10, 8))
    
    # Plot minacce
    colors = ['red', 'orange', 'yellow', 'purple']
    for i, threat in enumerate(threats):
        circle = plt.Circle((threat.cylinder.center.x, threat.cylinder.center.y), 
                          threat.cylinder.radius, color=colors[i], alpha=0.3,
                          label=f'ThreatAA_{i+1}')
        plt.gca().add_patch(circle)
    
    # Plot percorso
    waypoints = route.getWaypoints()
    x = [wp.point.x for wp in waypoints]
    y = [wp.point.y for wp in waypoints]
    plt.plot(x, y, 'bo-', linewidth=2, markersize=8, label='Route')
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('2D Route Map')
    plt.legend()
    plt.grid(True)
    plt.axis('equal')
    plt.show()

def plot_3d_route(route, threats):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot minacce
    for i, threat in enumerate(threats):
        x = threat.cylinder.center.x
        y = threat.cylinder.center.y
        z = 0
        height = threat.cylinder.height
        
        # Base del cilindro
        theta = np.linspace(0, 2*np.pi, 100)
        x_c = x + threat.cylinder.radius * np.cos(theta)
        y_c = y + threat.cylinder.radius * np.sin(theta)
        ax.plot(x_c, y_c, z, color='r', alpha=0.3)
        
        # Superficie laterale
        z_c = np.linspace(z, height, 10)
        theta, z_c = np.meshgrid(theta, z_c)
        x_c = x + threat.cylinder.radius * np.cos(theta)
        y_c = y + threat.cylinder.radius * np.sin(theta)
        ax.plot_surface(x_c, y_c, z_c, color='r', alpha=0.1)
    
    # Plot percorso
    waypoints = route.getWaypoints()
    x = [wp.point.x for wp in waypoints]
    y = [wp.point.y for wp in waypoints]
    z = [wp.point.z for wp in waypoints]
    ax.plot(x, y, z, 'bo-', linewidth=2, markersize=8)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Altitude')
    ax.set_title('3D Route Visualization')
    plt.show()

@pytest.mark.parametrize("start,end", [
    ((3,0,5), (8,10,5)),
    ((3,0,5), (4,3,2))
])
def test_route_creation(start, end):
    # Creazione waypoint
    start_wp = Waypoint("START", Point3D(*start))
    end_wp = Waypoint("END", Point3D(*end))
    grid_step = 1
    grid_alt_step = 1
    
    # Creazione rotta
    route = createRoute(start_wp, end_wp, threats, grid_step, grid_alt_step, **params)

    # Verifiche base
    assert route is not None
    assert len(route.edges) > 0
    assert route.getWaypoints()[0] == start_wp
    assert route.getWaypoints()[-1] == end_wp
    
    # Verifica parametri di sicurezza
    total_danger = sum(edge.danger for edge in route.edges.values())
    assert total_danger < 10  # Valore da calibrare
    
    # Visualizzazione
    plot_2d_route(route, threats)
    plot_3d_route(route, threats)
    
    # Verifica vincoli altitudine
    for wp in route.getWaypoints():
        assert params['altitude_min'] <= wp.point.z <= params['altitude_max']
    
    # Verifica tempi di intercettazione
    for edge in route.edges.values():
        for threat in threats:
            in_range, _ = threat.inRange(edge.wpA.point)
            if in_range:
                assert edge.travel_time < threat.interceptTime(edge.wpA.point)

def test_waypoint_equality():
    p1 = Waypoint("A", Point3D(1,2,3))
    p2 = Waypoint("B", Point3D(1,2,3))
    assert p1 == p2
    assert hash(p1) == hash(p2)

if __name__ == "__main__":
    pytest.main(["-v", __file__])