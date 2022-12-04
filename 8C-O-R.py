"""
PMC generates the trajectory
BG-THA-M1 pathway decides whether or not to execute that trajectory
Thus, there are two actions, "go" and "nogo", where the go action is the
specified trajectory.
BG-THA control similar to inhib control on SYDE556 LEC 11 @ 1:38:00
"""

import importlib
import numpy as np

import nengo
from nengo.dists import Uniform

from REACH import arm;

importlib.reload(arm)
from REACH import M1;

importlib.reload(M1)
from REACH import CB;

importlib.reload(CB)
from REACH import S1;

importlib.reload(S1)
from REACH import PMC;

importlib.reload(PMC)
from REACH import framework;

importlib.reload(framework)


def generate():
    kp = 50
    kv = np.sqrt(kp) * 1.5

    n_reaches = 8
    dist = .25
    center = [0, 1.25]
    end_points = [[dist * np.cos(theta) + center[0],
                   dist * np.sin(theta) + center[1]]
                  for theta in np.linspace(0, 2 * np.pi, n_reaches + 1)][:-1]
    targets = []
    for ep in end_points:
        targets.append(center)
        targets.append(ep)
    targets = np.array(targets)

    # Individualize the 8 reaches
    # Reach 1
    reach1_start = targets[0]
    reach1_stop = targets[1]
    reach1_startx = targets[0][0]
    reach1_stopx = targets[1][0]
    reach1_starty = targets[0][1]
    reach1_stopy = targets[1][1]
    reach1_trajx = np.linspace(reach1_startx, reach1_stopx, 100)
    reach1_trajy = np.linspace(reach1_starty, reach1_stopy, 100)
    reach1_traj = np.vstack([reach1_trajx, reach1_trajy])
    # Reach 2
    print(targets)
    reach2_start = targets[2]
    reach2_stop = targets[3]
    reach2_startx = reach2_start[0]
    reach2_stopx = reach2_stop[0]
    reach2_starty = reach2_start[1]
    reach2_stopy = reach2_stop[1]
    reach2_trajx = np.linspace(reach2_startx, reach2_stopx, 100)
    reach2_trajy = np.linspace(reach2_starty, reach2_stopy, 100)
    reach2_traj = np.vstack([reach2_trajx, reach2_trajy])

    arm_sim = arm.Arm2Link(dt=1e-3)
    # set the initial position of the arm
    arm_sim.init_q = arm_sim.inv_kinematics(center)
    arm_sim.reset()

    net = nengo.Network(seed=0)
    with net:
        net.dim = arm_sim.DOF
        net.arm_node = arm_sim.create_nengo_node()
        net.error = nengo.Ensemble(500, 2)
        net.xy = nengo.Node(size_in=2)

        # create an M1 model ------------------------------------------------------
        net.M1 = M1.generate(arm_sim, kp=kp,
                             operational_space=True,
                             inertia_compensation=True,
                             means=[0.6, 2.2, 0, 0],
                             scales=[.25, .25, .25, .25])

        # create an S1 model ------------------------------------------------------
        net.S1 = S1.generate(arm_sim,
                             means=[.6, 2.2, -.5, 0, 0, 1.25],
                             scales=[.5, .5, 1.7, 1.5, .75, .75])

        # subtract out current position to get desired task space direction
        nengo.Connection(net.S1.output[net.dim * 2:], net.error, transform=-1)

        # generate circle trajectory
        center = np.array([0.0, 1.25])
        x = np.linspace(0.0, 2.0 * np.pi, 100)
        circle_traj = np.vstack([np.cos(x) * .5, np.sin(x) * .5])
        circle_traj += center[:, None]

        # create a PMC model ------------------------------------------------------
        net.PMC = PMC.generate(targets, speed=1)
        nengo.Connection(net.PMC.output, net.error)
        nengo.Connection(net.PMC.output, net.xy)

        # create  a CB model ------------------------------------------------------
        net.CB = CB.generate(arm_sim, kv=kv,
                             means=[0.6, 2.2, 0, 0],
                             scales=[.125, .25, 1, 1.5])

        # create  a BG & THA model -------------------------------------------------
        bg = nengo.networks.BasalGanglia(1)
        tha = nengo.networks.Thalamus(1)

    model = framework.generate(net=net, probes_on=False)
    return model

model = generate()
