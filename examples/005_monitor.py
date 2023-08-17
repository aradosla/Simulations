# %%

import json
import numpy as np
import xtrack as xt
import xpart as xp
import xobjects as xo
# %%
context = xo.ContextCpu()

#with open('/home/sterbini/2023_08_10_for_Anna/xtrack/test_data/hllhc15_noerrors_nobb/line_and_particle.json') as f:
#with open('../data/collider_thin.json') as f:
#    dct = json.load(f)
collider = xt.Multiline.from_json('../data/collider_thin.json')

line = collider['lhcb1']
for ii in line.elements:
   # if ii is a type 'multipole' 
    if type(ii) == xt.beam_elements.elements.Multipole:
        if len(ii.knl)>2:
            print(ii)
            ii.knl[2] = 0

line.vars['i_oct_b1'] = 0

line_edited = line.copy()
# %%
my_particle = xp.Particles(
                    mass0=xp.PROTON_MASS_EV, q0=1, energy0=7000e9)
line.particle_ref = my_particle

num_particles = 1
monitor_ip3 = xt.ParticlesMonitor(start_at_turn=0, stop_at_turn=15,
                                    num_particles=num_particles)
monitor_ip5 = xt.ParticlesMonitor(start_at_turn=0, stop_at_turn=15,
                                    num_particles=num_particles)
monitor_ip8 = xt.ParticlesMonitor(start_at_turn=0, stop_at_turn=15,
                                    num_particles=num_particles)
line.insert_element(index='ip3', element=monitor_ip3, name='mymon3')
line.insert_element(index='ip5', element=monitor_ip5, name='mymon5')
line.insert_element(index='ip8', element=monitor_ip8, name='mymon8')

line.build_tracker()

particles = xp.Particles(
                    mass0=xp.PROTON_MASS_EV, q0=1, energy0=7000e9, x=0.003)

num_turns = 10000
monitor = xt.ParticlesMonitor(_context=context,
                              start_at_turn=0, stop_at_turn=15,
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
#plt.plot(monitor_ip3.x, monitor_ip3.px, '.g')
plt.plot(monitor_ip5.x, monitor_ip5.px, '.b', label='ip5')
plt.plot(monitor_ip8.x, monitor_ip8.px, '.r', label='ip8')
plt.xlabel('x [m]')
plt.ylabel('px [rad]')
#plt.legend()
plt.show()
plt.figure(2)
#plt.plot(monitor_ip3.y, monitor_ip3.py, '.g')
plt.plot(monitor_ip5.y, monitor_ip5.py, '.b', label='ip5')
plt.plot(monitor_ip8.y, monitor_ip8.py, '.r', label='ip8')
plt.xlabel('y [m]')
plt.ylabel('py [rad]')
#plt.legend()
# %%

#line.vars['i_oct_b1'] = 0

line.twiss()['s','mymon5']
line.twiss()['s','mymon8']
# %%
aux = line.twiss()
# %%
for jj,ii in enumerate(aux[:, 'bpm.*']['name']):
    print(jj)
    exec(f'''monitor_{ii.replace('.','_')}  = xt.ParticlesMonitor(start_at_turn=0, stop_at_turn=15,
                                    num_particles=num_particles)''')
    eval(f'''line_edited.insert_element(index='{ii}', 
         element=monitor_{ii.replace('.','_')}, 
         name='mymon_{ii.replace('.','_')}')''')
# %%
line_edited.discard_tracker()
line_edited.particle_ref = particles

line_edited.build_tracker()


# %%
#line.discard_tracker()
# %%

line_edited.twiss()[:, 'mymon_bpm_.*']
# %%
# Here you can add the initial conditions, e.g. x, px, y, py, etc.
# When changing the initial conditions, the amplitude of the oscillations is changing
# Px and Py are the momenta in the horizontal and vertical plane, respectively and their
# change is affecting the amplitude of the oscillations
particles = xp.Particles(
                    mass0=xp.PROTON_MASS_EV, q0=1, energy0=7000e9, x =3e-3,  y = 0.00, px = 0.000, py = 0.0000)
line_edited.track(particles, num_turns=num_turns)

# %%
s_list = []
mux_list = []
x_list = []
y_list = []
px_list = []
twiss_edited = line_edited.twiss()
for jj,ii in enumerate(aux[:, 'bpm.*']['name']):
    myname = f'mymon_{ii.replace(".","_")}'
    eval(f"s_list.append(twiss_edited['s','{myname}'])")
    myx = eval(f"monitor_{ii.replace('.','_')}.x[0][0]")
    myy = eval(f"monitor_{ii.replace('.','_')}.y[0][0]")
    mypx = eval(f"monitor_{ii.replace('.','_')}.px[0][0]")
    mypy = eval(f"monitor_{ii.replace('.','_')}.py[0][0]")
    eval(f"px_list.append({mypx})")
    eval(f"y_list.append({myy})")
    #mux = myx/twiss_edited['mux', f'{myname}']
    #print(mux)
    #eval(f"mux_list.append(mux)")
    eval(f"x_list.append({myx})")
# %%

plt.plot(s_list, y_list, '.-r') 
plt.show()
fig, ax = plt.subplots()
ax.plot(s_list, x_list, '.-b')
ax.set_xlabel('s [m]')
ax.set_ylabel('x [m]', color='b')
ax1 = ax.twinx()
#plt.plot(s_list, x_list, '.-b')
ax1.plot(s_list, twiss_edited[:, 'bpm.*']['betx'], '.-r')
ax1.set_ylabel('betx [m]', color='r')
plt.title('x [m] and betx [m] vs s [m]')
plt.show()
#plt.plot(s_list, px_list, '.-g', label='px')
#plt.plot(s_list[50:], mux_list[50:], '.-r')

#plt.show()
# %%

# %%
plt.plot(s_list, twiss_edited[:, 'bpm.*']['mux'], '.-b')

# %%
# You have to remember that ip3 is the starting point of the lattice
# twiss_edited[:, 'ip3']['betx']
import math
phase1 = twiss_edited[:, 'ip3']['mux']   # initial phase
phase2 = twiss_edited[:, 'ip8']['mux']   # final phase
phase = (phase2-phase1)*2*np.pi

alpha1 = twiss_edited[:, 'ip3']['alfx'] # initial alpha
beta1 = twiss_edited[:, 'ip3']['betx']  # initial beta

alpha2 = twiss_edited[:, 'ip8']['alfx'] # final alpha
beta2 = twiss_edited[:, 'ip8']['betx']  # final beta
# %%


m11 = np.sqrt(beta2/beta1)*(np.cos(phase)+alpha1*np.sin(phase))
print(m11.shape)
print(type(m11))

m12 = np.sqrt(beta1*beta2)*np.sin(phase)

m21 = -(1+alpha1*alpha2)/np.sqrt(beta1*beta2)*np.sin(phase) + (alpha1-alpha2)/np.sqrt(beta1*beta2)*np.cos(phase)
#print(m21)

m22 = np.sqrt(beta1/beta2)*(np.cos(phase)-alpha2*np.sin(phase))

M = np.array([[m11[0],m12[0]],[m21[0],m22[0]]])
#print(M.reshape(2,2).shape)

input_vector = np.array([[monitor_ip3.x[0][0]],[monitor_ip3.px[0][0]]])


print(input_vector)
print(input_vector.shape)
x2 = M @ input_vector


#x2 = m11*monitor_ip3.x[0][0] 

print('IP8_matrix',x2)
print('IP8x' , monitor_ip8.x[0][0])
print('IP8px', monitor_ip8.px[0][0])
#check if the phase is correct -> m12 and m11 are correct
#math.degrees(np.arctan(m12/(beta1*m11- alpha1*m12)))

# %%
plt.plot(s_list, twiss_edited[:, 'bpm.*']['alfx'], '.-b')


# %%
# IP8_matrix [7.0380056e-05]
# IP8 6.667365146559886e-05
# %%
twiss_edited.cols
dir(twiss_edited)

        

# %%
plt.plot(s_list, twiss_edited[:, 'bpm.*']['energy'], '.-b')
# %%
