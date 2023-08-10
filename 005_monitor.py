# %%

# import xtrack as xt
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# import xpart as xp
# import xobjects as xo

import json

import xtrack as xt
import xpart as xp
import xobjects as xo

context = xo.ContextCpu()

#with open('/home/sterbini/2023_08_10_for_Anna/xtrack/test_data/hllhc15_noerrors_nobb/line_and_particle.json') as f:
with open('../data/collider_thin.json') as f:
    dct = json.load(f)
# collider = xt.Multiline.from_json('../data/collider_thin.json')


line = xt.Line.from_dict(dct['lines']['lhcb1'])
# %%
my_particle = xp.Particles(
                    mass0=xp.PROTON_MASS_EV, q0=1, energy0=7000e9)
line.particle_ref = my_particle

num_particles = 1
monitor_ip5 = xt.ParticlesMonitor(start_at_turn=5, stop_at_turn=15,
                                    num_particles=num_particles)
monitor_ip8 = xt.ParticlesMonitor(start_at_turn=5, stop_at_turn=15,
                                    num_particles=num_particles)

line.insert_element(index='ip5', element=monitor_ip5, name='mymon5')
line.insert_element(index='ip8', element=monitor_ip8, name='mymon8')

line.build_tracker()

particles = xp.Particles(
                    mass0=xp.PROTON_MASS_EV, q0=1, energy0=7000e9, x=0.001)

num_turns = 30
monitor = xt.ParticlesMonitor(_context=context,
                              start_at_turn=5, stop_at_turn=15,
                              num_particles=num_particles)
line.track(particles, num_turns=num_turns)

# monitor_ip5 contains the data recorded in before the element 'ip5', while
# monitor_ip8 contains the data recorded in before the element 'ip8'
# The element index at which the recording is made can be inspected in
# monitor_ip5.at_element.
# %%
from matplotlib import pyplot as plt
plt.close('all')
plt.figure(1)
plt.plot(monitor_ip5.x, monitor_ip5.px, '.b')
plt.plot(monitor_ip8.x, monitor_ip8.px, '.r')


# %%
line.twiss()['s','mymon5']
line.twiss()['s','mymon8']