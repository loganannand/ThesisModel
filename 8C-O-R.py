import importlib
import numpy as np

import nengo
import nengo_spa as spa

from REACH import arm; importlib.reload(arm)
from REACH import M1; importlib.reload(M1)
from REACH import CB; importlib.reload(CB)
from REACH import S1; importlib.reload(S1)
from REACH import framework; importlib.reload(framework)


def generate():
    kp = 50
    kv = np.sqrt(kp) * 1.5

    n_reaches = 8
    dist = .25
    center = [0, 1.25]
    end_points = [[dist * np.cos(theta) + center[0],
                dist * np.sin(theta) + center[1]]
                for theta in np.linspace(0, 2*np.pi, n_reaches+1)][:-1]
    targets = []
    for ep in end_points:
        targets.append(center)
        targets.append(ep)
    targets = np.array(targets)

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
        nengo.Connection(net.S1.output[net.dim*2:], net.error, transform=-1)

        # create a PMC substitute -------------------------------------------------
        net.PMC = nengo.Network('PMC')
        with net.PMC:
            def PMC_func(t):
                """ every 1 seconds change target """
                return targets[int(t) % len(targets)]
            net.PMC.output = nengo.Node(output=PMC_func, label='PMC')
        # send target for calculating control signal
        nengo.Connection(net.PMC.output, net.error)
        # send target (x,y) for plotting
        nengo.Connection(net.PMC.output, net.xy)

        # create  a CB model ------------------------------------------------------
        net.CB = CB.generate(arm_sim, kv=kv,
                             means=[0.6, 2.2, 0, 0],
                             scales=[.125, .25, 1, 1.5])

    model = framework.generate(net=net, probes_on=False)
    return model

# Check to see if it's open in the GUI
from nengo.simulator import Simulator as NengoSimulator
if nengo.Simulator is not NengoSimulator or __name__ == '__main__':
    # connect up the models we've defined, set up the functions, probes, etc
    model = generate()