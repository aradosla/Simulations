# %%

import json
import numpy as np
import xtrack as xt
import xpart as xp
import xobjects as xo
# %%
context = xo.ContextCpu()

#with open('/home/sterbini/2023_08_10_for_Anna/xtrack/test_data/hllhc15_noerrors_nobb/line_and_particle.json') as f:
with open('../data/collider_thin.json') as f:
    dct = json.load(f)
# collider = xt.Multiline.from_json('../data/collider_thin.json')


line = xt.Line.from_dict(dct['lines']['lhcb1'])
line_edited =line.copy()
# %%
my_particle = xp.Particles(
                    mass0=xp.PROTON_MASS_EV, q0=1, energy0=7000e9)
line.particle_ref = my_particle

num_particles = 1
monitor_ip3 = xt.ParticlesMonitor(start_at_turn=5, stop_at_turn=15,
                                    num_particles=num_particles)
monitor_ip5 = xt.ParticlesMonitor(start_at_turn=5, stop_at_turn=15,
                                    num_particles=num_particles)
monitor_ip8 = xt.ParticlesMonitor(start_at_turn=5, stop_at_turn=15,
                                    num_particles=num_particles)
line.insert_element(index='ip3', element=monitor_ip3, name='mymon3')
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
# %%
aux = line.twiss()
# %%
for jj,ii in enumerate(aux[:, 'bpm.*']['name']):
    print(jj)
    exec(f'''monitor_{ii.replace('.','_')}  = xt.ParticlesMonitor(start_at_turn=5, stop_at_turn=15,
                                    num_particles=num_particles)''')
    eval(f'''line_edited.insert_element(index='{ii}', 
         element=monitor_{ii.replace('.','_')}, 
         name='mymon_{ii.replace('.','_')}')''')
# %%
line_edited.particle_ref = my_particle

line_edited.build_tracker()
# %%

line_edited.twiss()[:, 'mymon_bpm_.*']
# %%
particles = xp.Particles(
                    mass0=xp.PROTON_MASS_EV, q0=1, energy0=7000e9, x=-0.001)
line_edited.track(particles, num_turns=num_turns)
# %%
s_list = []
x_list = []
twiss_edited = line_edited.twiss()
for jj,ii in enumerate(aux[:, 'bpm.*']['name']):
    myname = f'mymon_{ii.replace(".","_")}'
    eval(f"s_list.append(twiss_edited['s','{myname}'])")
    myx = eval(f"monitor_{ii.replace('.','_')}.x[0][0]")
    eval(f"x_list.append({myx})")
# %
plt.plot(s_list, x_list, '.-b')

# %%
plt.plot(s_list, twiss_edited[:, 'bpm.*']['betx'], '.-b')
# %%
plt.plot(s_list, twiss_edited[:, 'bpm.*']['mux'], '.-b')

# %%
# You have to remember that ip3 is the starting point of the lattice
# twiss_edited[:, 'ip3']['betx']
import math
phase1 = twiss_edited[:, 'ip3']['mux']   # initial phase
phase2 = twiss_edited[:, 'ip3']['mux']   # final phase
#phase = (phase2-phase1)*np.pi/180
# from degrees to radians
phase = math.radians(phase2-phase1)

alpha1 = twiss_edited[:, 'ip3']['alfx'] # initial alpha
beta1 = twiss_edited[:, 'ip3']['betx']  # initial beta

alpha2 = twiss_edited[:, 'ip3']['alfx'] # final alpha
beta2 = twiss_edited[:, 'ip3']['betx']  # final beta
# %%
m11 = np.sqrt(beta2/beta1)*(np.cos(phase)+alpha1*np.sin(phase))
#print(m11)

m12 = np.sqrt(beta1*beta2)*np.sin(phase)

m21 = -(1+alpha1*alpha2)/np.sqrt(beta1*beta2)*np.sin(phase) + (alpha1-alpha2)/np.sqrt(beta1*beta2)*np.cos(phase)
#print(m21)

m22 = np.sqrt(beta1/beta2)*(np.cos(phase)-alpha2*np.sin(phase))

x2 = m11*monitor_ip3.x[0][0] 

print('IP8_matrix',x2)
print('IP8', monitor_ip8.x[0][0])

#check if the phase is correct -> m12 and m11 are correct
math.degrees(np.arctan(m12/(beta1*m11- alpha1*m12)))

# %%
plt.plot(s_list, twiss_edited[:, 'bpm.*']['alfx'], '.-b')

