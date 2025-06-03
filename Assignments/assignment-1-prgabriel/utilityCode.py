import numpy as np
from math import sin, cos
import matplotlib.pyplot as plt
from PIL import Image
import os
import imageio
import copy

def get_plane_mesh(in_plane, grid_n):

    """ Given the four corners of a plane in homogeneous coordinates,
    return the corner locations of individual checkerboard squares. 
    Each output row consists of four points which are the corners of each grid square.

    Input: plane corner points, number of checkerboard squares
    Output: Nx4 matrix containing 3D homogenous points for each square on the plane """
    
    # the two edges of the square
    X = np.linspace(in_plane[0, 0], in_plane[1, 0], grid_n)
    Y = np.linspace(in_plane[1, 1], in_plane[2, 1], grid_n)

    # use meshgrid to get the points
    U, V = np.meshgrid(X, Y)
    
    # reshape the points to a Nx4 matrix
    out = np.concatenate( (U[:, :, np.newaxis], V[:, :, np.newaxis], 
                           np.zeros_like(U)[:, :, np.newaxis],
                            np.ones_like(U)[:, :, np.newaxis]), axis=2)
    return out


def draw_plane(in_ax, in_pts, patternoffset):
    """ Given a matplotlib axis and grid point locations in *sensor* coordinates, draw a checkerboard for a single plane
    The pattern offset determines whether grid squares start with white or black """
    c = 0
    for i in range(in_pts.shape[0] - 1):
        for j in range(in_pts.shape[1] - 1):
            if c % 2 == patternoffset: # this offsets the planes to ensure checkboard pattern at the edges
                in_ax.fill([in_pts[i, j, 0], in_pts[i+1, j, 0], in_pts[i+1, j+1, 0], in_pts[i, j+1, 0]],
                           [in_pts[i, j, 1], in_pts[i+1, j, 1], in_pts[i+1, j+1, 1], in_pts[i, j+1, 1]], 'k-')
            else:
                in_ax.fill([in_pts[i, j, 0], in_pts[i+1, j, 0], in_pts[i+1, j+1, 0], in_pts[i, j+1, 0]],
                           [in_pts[i, j, 1], in_pts[i+1, j, 1], in_pts[i+1, j+1, 1], in_pts[i, j+1, 1]], 'w-')
            c = c + 1

            

def visualize_scene(in_scene, grid_count, draw = True, full_scene = True):
    """ given one scene parameters in a scene dictionary, visualize the scene """

    # draw
    my_dpi = 96
    fig = plt.figure( figsize=(800/my_dpi, 400/my_dpi), dpi=my_dpi)
    ax = fig.add_subplot()
    
    # plot the ground plane
    xy = in_scene['ground_plane']['points']
    cur_proj = np.concatenate((np.reshape(xy[:, 0], (grid_count, grid_count, 1)), 
                               np.reshape(xy[:, 1], (grid_count, grid_count, 1))), axis=2)
    draw_plane(ax, cur_proj, 0) 

    # plot the right plane
    xy = in_scene['right_plane']['points']
    cur_proj = np.concatenate((np.reshape(xy[:, 0], (grid_count, grid_count, 1)), 
                               np.reshape(xy[:, 1], (grid_count, grid_count, 1))), axis=2)
    draw_plane(ax, cur_proj, 1)

    if full_scene == True:

        # plot the left plane
        xy = in_scene['left_plane']['points']
        cur_proj = np.concatenate((np.reshape(xy[:, 0], (grid_count, grid_count, 1)), 
                                np.reshape(xy[:, 1], (grid_count, grid_count, 1))), axis=2)
        draw_plane(ax, cur_proj, 1)

        # plot the back plane
        xy = in_scene['back_plane']['points']
        cur_proj = np.concatenate((np.reshape(xy[:, 0], (grid_count, grid_count, 1)), 
                                np.reshape(xy[:, 1], (grid_count, grid_count, 1))), axis=2)
        draw_plane(ax, cur_proj, 0)

        # plot the cube
        xy = in_scene['cube']['points']
        x = xy[:, 0].copy()
        y = xy[:, 1].copy()

        # draw six faces of the cube
        facecolor = [0.7,0.7,0.7,0.5]
        plt.fill([x[0], x[1], x[2], x[3]], [y[0], y[1], y[2], y[3]], color=facecolor)
        plt.fill([x[4], x[5], x[6], x[7]], [y[4], y[5], y[6], y[7]], color=facecolor)
        plt.fill([x[0], x[1], x[5], x[4]], [y[0], y[1], y[5], y[4]], color=facecolor)
        plt.fill([x[1], x[2], x[6], x[5]], [y[1], y[2], y[6], y[5]], color=facecolor)
        plt.fill([x[2], x[3], x[7], x[6]], [y[2], y[3], y[7], y[6]], color=facecolor)
        plt.fill([x[3], x[0], x[4], x[7]], [y[3], y[0], y[4], y[7]], color=facecolor)

        # draw six edges of the cube
        edgecolor = 'ro-'
        plt.plot([x[0], x[1]], [y[0], y[1]], edgecolor)
        plt.plot([x[1], x[2]], [y[1], y[2]], edgecolor)
        plt.plot([x[2], x[3]], [y[2], y[3]], edgecolor)
        plt.plot([x[3], x[0]], [y[3], y[0]], edgecolor)

        plt.plot([x[4], x[5]], [y[4], y[5]], edgecolor)
        plt.plot([x[5], x[6]], [y[5], y[6]], edgecolor)
        plt.plot([x[6], x[7]], [y[6], y[7]], edgecolor)
        plt.plot([x[7], x[4]], [y[7], y[4]], edgecolor)

        plt.plot([x[0], x[4]], [y[0], y[4]], edgecolor)
        plt.plot([x[1], x[5]], [y[1], y[5]], edgecolor)
        plt.plot([x[2], x[6]], [y[2], y[6]], edgecolor)
        plt.plot([x[3], x[7]], [y[3], y[7]], edgecolor)

    ax.set_aspect('equal', adjustable='box')
    plt.xlim([-0.2, 0.2])
    plt.ylim([-0.1, 0.1])
    plt.xticks(ticks=[])
    plt.yticks(ticks=[])

    # flag to suppress image display
    if draw: plt.draw()
    
    plt.tight_layout()
    
    #save the current plot and return this image
    plt.savefig('temp.png', dpi=my_dpi)
    image = imageio.imread('temp.png')
    os.remove('temp.png')
    return image
