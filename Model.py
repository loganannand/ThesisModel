import nengo

model = nengo.Network()
with model:
    bg = nengo.networks.BasalGanglia(dimensions=1)
    tha = nengo.networks.Thalamus(dimensions=1)

    cortex = nengo.Network()
    with cortex:
        M1 = nengo.Ensemble(n_neurons=100, dimensions=1)

        SensoryInfo = nengo.Network()
        with SensoryInfo:
            pre_SMA = nengo.Ensemble(n_neurons=100, dimensions=1)
            rIFC = nengo.Ensemble(n_neurons=100, dimensions=1)
            output = nengo.Node(size_in=1)

            nengo.Connection(pre_SMA, output)
            nengo.Connection(rIFC, output)

    nengo.Connection(tha.actions.input, M1)
    # nengo.Connection(SensoryInfo.output, bg.STN.output)  # fix this connectoin
    nengo.Connection(bg.output, tha.actions.input)
    nengo.Connection(output, bg.input)



