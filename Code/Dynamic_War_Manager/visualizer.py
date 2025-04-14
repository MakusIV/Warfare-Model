import matplotlib
matplotlib.use('TkAgg')  # oppure 'Qt5Agg' o 'MacOSX' se sei su mac

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class Cylinder:
    def __init__(self, base, radius, height):
        self.base = np.array(base)
        self.radius = radius
        self.height = height

    def get_mesh(self, resolution=30):
        theta = np.linspace(0, 2 * np.pi, resolution)
        z = np.array([0, self.height])
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_grid = self.radius * np.cos(theta_grid) + self.base[0]
        y_grid = self.radius * np.sin(theta_grid) + self.base[1]
        z_grid += self.base[2]
        return x_grid, y_grid, z_grid


class Path3D:
    def __init__(self, points):
        self.points = np.array(points)

    def get_segments(self):
        return self.points


class Space:
    def __init__(self, space_x, space_y, space_z):
        self.origin = (0, 0, 0)
        self.space_x = space_x
        self.space_y = space_y
        self.space_z = space_z
        self.cylinders = []
        self.paths = []

    def add_cylinder(self, cylinder):
        self.cylinders.append(cylinder)

    def add_path(self, path):
        self.paths.append(path)

    def show_3d(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlim(0, self.space_x)
        ax.set_ylim(0, self.space_y)
        ax.set_zlim(0, self.space_z)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("3D View")

        # Draw cylinders
        for cylinder in self.cylinders:
            x, y, z = cylinder.get_mesh()
            ax.plot_surface(x, y, z, alpha=0.6, color='orange', edgecolor='k')

        # Draw paths
        for path in self.paths:
            points = path.get_segments()
            xs, ys, zs = zip(*points)
            ax.plot(xs, ys, zs, marker='o', color='blue')

        plt.show()

    def show_2d_top(self):
        
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.space_x)
        ax.set_ylim(0, self.space_y)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("2D Top View (XY Plane)")

        # Draw cylinders as circles
        for cylinder in self.cylinders:
            circle = plt.Circle((cylinder.base[0], cylinder.base[1]), cylinder.radius, color='orange', alpha=0.6)
            ax.add_patch(circle)

        # Draw paths
        for path in self.paths:
            points = np.array(path.get_segments())
            ax.plot(points[:, 0], points[:, 1], marker='o', color='blue')

        plt.gca().set_aspect('equal', adjustable='box')
        plt.show()


    def show_all_views(self):
        # Vista 3D
        fig3d = plt.figure()
        ax3d = fig3d.add_subplot(121, projection='3d')
        ax3d.set_xlim(0, self.space_x)
        ax3d.set_ylim(0, self.space_y)
        ax3d.set_zlim(0, self.space_z)
        ax3d.set_title("3D View")
        for cylinder in self.cylinders:
            x, y, z = cylinder.get_mesh()
            ax3d.plot_surface(x, y, z, alpha=0.6, color='orange', edgecolor='k')
        for path in self.paths:
            xs, ys, zs = zip(*path.get_segments())
            ax3d.plot(xs, ys, zs, marker='o', color='blue')

        # Vista 2D
        ax2d = fig3d.add_subplot(122)
        ax2d.set_xlim(0, self.space_x)
        ax2d.set_ylim(0, self.space_y)
        ax2d.set_title("2D Top View")
        for cylinder in self.cylinders:
            circle = plt.Circle((cylinder.base[0], cylinder.base[1]), cylinder.radius, color='orange', alpha=0.6)
            ax2d.add_patch(circle)
        for path in self.paths:
            points = np.array(path.get_segments())
            ax2d.plot(points[:, 0], points[:, 1], marker='o', color='blue')
        ax2d.set_aspect('equal', adjustable='box')

        plt.show()

if __name__ == "__main__":

    space = Space(space_x=100, space_y=100, space_z=100)

    #self.cylinder = Cylinder(Point3D(6, 9, 5), 2, 10)
        
    # Crea i segmenti per i test specifici
    #self.edge_A = Segment3D(Point3D(4, 2, 7), Point3D(9, 15, 7)) # interseca
    #self.edge_B = Segment3D(Point3D(6, 2, 7), Point3D(9, 15, 7)) # interseca
    #self.edge_C = Segment3D(Point3D(4, 2, 4), Point3D(9, 15, 4)) # non interseca
    #self.edge_D = Segment3D(Point3D(6, 6, 0), Point3D(9, 15, 6)) # non interseca
    #self.edge_E = Segment3D(Point3D(16, 1, 0), Point3D(4, 11, 6)) # interseca solo in un punto, l'altro passa attraverso la superficie inferiore
    #self.edge_F = Segment3D(Point3D(4, 14, 9), Point3D(5, 6, 14)) # interseca
    #self.edge_G = Segment3D(Point3D(8, 9.1, 5), Point3D(4, 8.9, 15))  # interseca

    # Aggiunta cilindri
    c1 = Cylinder(base=(6, 9, 5), radius=5, height=30)
    #c2 = Cylinder(base=(60, 60, 0), radius=10, height=50)
    space.add_cylinder(c1)
    #space.add_cylinder(c2)

    # Aggiunta percorso
    path1 = Path3D([(4, 2, 7), (9, 15, 7), (30, 50, 20), (70, 80, 90)])
    space.add_path(path1)

    # Visualizzazioni
    #space.show_3d()
    #space.show_2d_top()
    space.show_all_views()
