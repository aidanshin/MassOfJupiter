from __future__ import print_function
from fitting import *
import pylab as pl
import math

MOON_ANG_DIA = 0.009075712
MOON_PIX_DIA = 4110

U_PIX_DIA = 10
U_DIS_MOON = 10
ganymede, io, europa, callisto, time_over, D_ej = np.genfromtxt('JupiterData.txt', unpack=True)

def CalcAngle(x):
    return np.multiply(x, MOON_ANG_DIA/MOON_PIX_DIA)

D_ej_m = np.multiply(D_ej, 1.496E+11)

def X_seperation(x):
    return np.multiply(x, D_ej_m)

def U_X_seperation(x):
    part1 = D_ej_m * U_DIS_MOON * MOON_ANG_DIA / MOON_PIX_DIA
    part2 = np.multiply(D_ej_m, x) * U_PIX_DIA * MOON_ANG_DIA / MOON_PIX_DIA**2
    return np.sqrt(np.add(np.power(part1, 2), np.power(part2, 2)))

g_ang = CalcAngle(ganymede)
i_ang = CalcAngle(io)
e_ang = CalcAngle(europa)
c_ang = CalcAngle(callisto)

g_sep = X_seperation(g_ang)
i_sep = X_seperation(i_ang)
e_sep = X_seperation(e_ang)
c_sep = X_seperation(c_ang)

U_g_sep = U_X_seperation(ganymede)
U_i_sep = U_X_seperation(io)
U_e_sep = U_X_seperation(europa)
U_c_sep = U_X_seperation(callisto)

def Moon(moon,moon_uncertainty,moon_name,time_over, amplitude, y_int, period, time_offset):
    moonData = []
    timeData = []
    U_moonData = []
    def fitfunc(x, a,b, T, t):
        return a*(sin(((2*pi/T)*(x-t))))+b

    for i in range(len(moon)):
        if moon[i] != 0:
            moonData.append(moon[i])
            timeData.append(time_over[i])
            U_moonData.append(moon_uncertainty[i])

    x = np.array(timeData)
    y = np.array(moonData)
    yerr = np.array(U_moonData)

    p0 = [amplitude,y_int,period, time_offset]
    popt, punc, rchi2, dof = general_fit(fitfunc, x, y, p0, yerr)
    print(moon_name,' optimal parameters: ', popt)
    print(moon_name,' uncertainties of parameters: ', punc)
    

    xf = pl.linspace(min(x),max(x),1000)
    yf = fitfunc(xf,*popt)

    pl.figure(figsize=(8,5))
    pl.scatter(x,y,s=15,label='Data')
    pl.errorbar(x, y, yerr, ls='None', capsize=2)
    pl.plot(xf,yf,"r-",label='Best-Fit Curve')
    pl.title(f'Distance from Jupiter to {moon_name} vs. Time')
    pl.xlabel('Time (s)')
    pl.ylabel(f'Distance from Jupiter to {moon_name} (m)')
    pl.legend(loc='upper right')

    return (popt[0], punc[0], popt[2], punc[2])

def Mass(radius, period, U_radius, U_period):
    y = np.power(period, 2)
    yerr = 2*period*U_period
    x = np.power(radius, 3)
    xerr = 3*(radius**2)*U_radius

    a, b, sa, sb, rchi2_2, dof2 = linear_fit(x,y, yerr, xerr)#,yerr,xerr)

    print('y = ax + b')
    print('a = ', a, ' +/- ', sa)
    print('b = ', b, ' +/- ', sb)
    
    JupiterMass = (4*pi**2)/(6.6743E-11 * a)
    U_JupiterMass = sa*(4*pi**2)/(6.6743E-11 *a**2)
    
    print(f"Jupiter Mass: {JupiterMass} +/- {U_JupiterMass}")
    
    xf = pl.linspace(min(x),max(x),100)
    yf = a*xf + b
    pl.figure(figsize=(8,5))
    pl.scatter(x,y,label='data')  # plot data
    pl.errorbar(x, y, yerr, xerr, ls='None', capsize=2)  # add error bars to data
    pl.plot(xf,yf,"r-",label='best-fit line')  # plot best-fit line
    pl.title('Mass of Jupiter')
    pl.ylabel('Period^2 (s^2)')
    pl.xlabel('Radius^3 (m^3)')
    pl.legend(loc='upper left')
    pl.annotate("Ganymede", (x[0], y[0]))
    pl.annotate("Io", (x[1], y[1]))
    pl.annotate("Europa", (x[2], y[2]))
    pl.annotate("Callisto", (x[3], y[3]))

g_R, g_U_R, g_T, g_U_T = Moon(g_sep, U_g_sep,"Ganymede", time_over, 6.06386328e+10, -5.76465208e+08, 6.08445496e+05, -2.44337228e+05)
i_R, i_U_R, i_T, i_U_T = Moon(i_sep, U_i_sep,"Io", time_over, -2.40497796e+10,  20,  1.49596674e+05, -6.82836150e+04)
e_R, e_U_R, e_T, e_U_T = Moon(e_sep, U_e_sep,"Europa", time_over, 3.5e+10, 50, 306000, 2.19739610e+05)
c_R, c_U_R, c_T, c_U_T = Moon(c_sep, U_c_sep,"Callisto", time_over, 1.07E11 ,100, 1.469e+6, 0)


period = np.array([g_T, i_T, e_T, c_T])
U_period = np.array([g_U_T, i_U_T, e_U_T, c_U_T])

radius = np.array([g_R, abs(i_R), e_R, c_R])
U_radius = np.array([g_U_R, i_U_R, e_U_R, c_U_R])

Mass(radius, period, U_radius, U_period)
pl.show()
