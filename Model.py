import nengo
import nengo_spa as spa
import numpy as np
from nengo.processes import Piecewise

"""
The Stop-Signal task measures how effectively someone can inhibit habitual 
responses in favor of more deliberate actions. It is an example of "reactive
stopping". 
----------
Key behaviour to measure is the models ability to withhold a response 
to the no-go trials. One parameter which can be manipulated is the 
stop signal delay (SSD) time. Also the ratio of go and no-go trials 
can vary which affects performance. 
----------
How the task works: Knowledge of task before hand, i.e., preplanned movement
is to go on a Go-trial but withhold that response on occation. Thus, what is
needed are multiple "trials" for Go and No-Go. 
----------
Short SSD time = More likely to inhibit the preplanned response. Response time
distribution allows us to estimate the latency of action stopping. The stop 
signal reaction time (SSRT). 
----------
Direct pathway: Supports actoins by inhibiting the BG output, thus disinhibiting
thalamic output to the cortex. 

Indirect pathway: May halp to supporess actoins by increasing inhibitory 
control over the BG output nuclei. 

Hyperdirect pathway: Offers a fsat route for stopping because of the sohrt-latency
monosynaptic connections between the cottex and STN. 
"""

model = nengo.Network()
with model:
    bg = nengo.networks.BasalGanglia(dimensions=1)  # Provide tonic
    # inhibition of thalamic outputs that facilitate motor cortical areas
    tha = nengo.networks.Thalamus(dimensions=1)  #

    cortex = nengo.Network()
    with cortex:
        M1 = nengo.Network()
        with M1:
            M1ens = nengo.Ensemble(n_neurons=100, dimensions=1)
            # Preplanned action
            motor_output = nengo.Node(size_in=1)
            nengo.Connection(M1ens, motor_output)

        SensoryInfo = nengo.Network()
        with SensoryInfo:
            pre_SMA = nengo.Ensemble(n_neurons=100, dimensions=1)
            rIFC = nengo.Ensemble(n_neurons=100, dimensions=1)
            output = nengo.Node(size_in=1)
            # Inhibitory control
            input = nengo.Node(size_in=1)

            nengo.Connection(pre_SMA, output)
            nengo.Connection(rIFC, output)

    Task = nengo.Network()
    with Task:
        Preplanned = nengo.Node(Piecewise({0: 1}))  # Fix this to control trials
        Inhib = nengo.Node(size_in=1)
        Signal = nengo.Node(0)
        Go = nengo.Ensemble(n_neurons=100, dimensions=1)

        # nengo.Connection(Go, M1ens)  # Drive has to come from thal right?
        nengo.Connection(input, rIFC)
        nengo.Connection(input, pre_SMA)
        nengo.Connection(Preplanned, Go)  # Preplanned movement
        nengo.Connection(Inhib, Go.neurons, transform=[[-2.5]] * 100)

    nengo.Connection(Signal, Inhib)
    nengo.Connection(Signal, input)
    nengo.Connection(tha.actions.output, M1ens)
    # nengo.Connection(SensoryInfo.output, bg.STN.output)  # fix this connection
    nengo.Connection(bg.output, tha.actions.input)
    nengo.Connection(output, bg.input)
    # nengo.Connection(Signal, Inhib)  # Fix this connection
    nengo.Connection(Go, tha.input)  # Is this physiologically accurate though?
    nengo.Connection(output, bg.stn.input)






