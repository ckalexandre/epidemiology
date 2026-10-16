import numpy as np
import pandas
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import scipy.optimize as optimize


def precipitation(t):
    x = 4.80*np.sin(0.053*(t+165)-4.39) + 5.03
    return x

def reproduction_rate(t):
    x = precipitation(t) + precipitation(t-1) + precipitation(t-2)
    y = 0.003181208*x - 0.01115436
    if y <= 0:
        return 0
    else:
        return y
    

#p_ht proba que l'habitant qui travaille se fasse infecter par un moustique (11)
#p_nht proba que le non habitant qui travaille dans la ville se fasse infecter par un moustique (21)
#p_hnt proba que l'habitant qui ne travaille pas dans la ville se fasse infecter par un moustique (12)

#inverse pour t_ht, t_nht, t_hnt: transmissibilité de l'humain au moustique
def deriv(Y, t, c, gamma_h, rho, mu_m,p_h, p_m, p_ht, p_nht, p_hnt, t_ht, t_nht, t_hnt): 
    Sh, Ih, Dh, Rh, Sm, Im, workers  = Y
    
    lambda_m = reproduction_rate(t)
    dSh = -c*Sh*Im* p_h *p_ht /(Im+ Sm+1e-9)
    dIh = c*Sh*Im/(Im + Sm+1e-9) *p_h- gamma_h*Ih
    dDh = rho * gamma_h * Ih
    dRh = (1-rho) * gamma_h * Ih
    dSm = lambda_m*(Sm +Im) - c * Sm * Ih * p_m /(Ih + Rh+ Sh+1e-9)- mu_m * Sm
    dIm = c * Sm * Ih *p_m /(Ih + Rh+ Sh) - mu_m * Im

    # Retourner les dérivées sous forme de liste
    return [dSh, dIh, dDh, dRh, dSm, dIm]

dico = {'no': [3907.6, 5.275, 0.0, 0.0, 11630.76923076923, 100], 's': [8789.68, 4.845000000000001, 0.0, 0.0, 9969.23076923077, 0], 'ne': [5506.72, 0.88, 0.0, 0.0, 0, 0]}

def deriv_workers(Y, t, c, gamma_h, rho, mu_m,p_h, p_m, p_11, p_21, p_12, t_11, t_21, t_12):
    w00,w01,w02,w10,w11,w12,w20,w21,w22,i00,i01,i02,i10,i11,i12,i20,i21,i22,r00,r01,r02,r10,r11,r12,r20,r21,r22,d00,d01,d02,d10,d11,d12,d20,d21,d22, Sm_no, Im_no, Sm_s, Im_s, Sm_ne, Im_ne = Y
    lambda_m = reproduction_rate(t)

    #Susceptible
    #Noltrame
    
    dw00 = -c*w00*Im_no*p_h*p_11/(Im_no+Sm_no+1e-7)
    dw01 = -c*w01*Im_s*p_h*p_12/(Im_s+Sm_s+1e-7) - c*w01*Im_no*p_h*p_21/(Im_no+Sm_no+1e-7)
    dw02 = -c*w02*Im_ne*p_h*p_12/(Im_ne+Sm_ne+1e-7) - c*w02*Im_no*p_h*p_21/(Im_no+Sm_no+1e-7)

    dw10 = -c*w10*Im_no*p_h*p_12/(Im_no+Sm_no+1e-7) - c*w10*Im_s*p_h*p_21/(Im_s+Sm_s+1e-7)
    dw11 = -c*w11*Im_s*p_h*p_11/(Im_s+Sm_s+1e-7)
    dw12 = -c*w12*Im_ne*p_h*p_12/(Im_ne+Sm_ne+1e-7) - c*w12*Im_s*p_h*p_21/(Im_s+Sm_s+1e-7)
    
    dw20 = -c*w20*Im_no*p_h*p_12/(Im_no+Sm_no+1e-7)
    dw21 = -c*w21*Im_s*p_h*p_12/(Im_s+Sm_s+1e-7)
    dw22 = 0
   
    #Noltrame
    di00 = - dw00 - gamma_h*i00
    di01 = - dw01 - gamma_h*i01
    di02 = - dw02 - gamma_h*i02
    dd00 = rho*gamma_h*i00
    dd01 = rho*gamma_h*i01
    dd02 = rho*gamma_h*i02
    dr00 = (1-rho)*gamma_h*i00
    dr01 = (1-rho)*gamma_h*i01
    dr02 = (1-rho)*gamma_h*i02
    
    #Sorya
    di10 = - dw10 - gamma_h*i10
    di11 = - dw11 - gamma_h*i11
    di12 = - dw12 - gamma_h*i12
    dd10 = rho*gamma_h*i10
    dd11 = rho*gamma_h*i11
    dd12 = rho*gamma_h*i12
    dr10 = (1-rho)*gamma_h*i10
    dr11 = (1-rho)*gamma_h*i11
    dr12 = (1-rho)*gamma_h*i12
    
    #Neamrolt
    di20 = - dw20 - gamma_h*i20
    di21 = - dw21 - gamma_h*i21
    di22 = 0
    dd20 = rho*gamma_h*i20
    dd21 = rho*gamma_h*i21
    dd22 = 0
    dr20 = (1-rho)*gamma_h*i20
    dr21 = (1-rho)*gamma_h*i21
    dr22 = 0
    
    #Moustique
    #Noltrame
    dSm_no = lambda_m*(Sm_no +Im_no) - c*Sm_no*i00*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-7) - mu_m*Sm_no
    dSm_no += - t_21*(c*Sm_no*i10*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-7) + c*Sm_no*i20*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-7))
    dSm_no += - t_12*(c*Sm_no*i01*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-9) - c*Sm_no*i02*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-7))
    dIm_no = c*Sm_no*i00*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-7) - mu_m*Im_no
    dIm_no += t_21*(c*Sm_no*i10*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-7) + c*Sm_no*i20*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-7))
    dIm_no += t_12*(c*Sm_no*i01*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-9) - c*Sm_no*i02*p_m/(w00 + i00 + r00+ t_21*(w10 + w20 + i10 + i20 + r10 + r20) + t_12*(w01 + w02 + i01 + i02 + r01 + r02) +1e-7))
    
    #Sorya
    dSm_s = lambda_m*(Sm_s +Im_s) - c*Sm_s*i11*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7) - mu_m*Sm_s
    dSm_s += - t_21*(c*Sm_s*i01*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7) + c*Sm_s*i21*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7))
    dSm_s += - t_12*(c*Sm_s*i10*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7) + c*Sm_s*i12*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7))
    dIm_s = c*Sm_s*i11*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7) - mu_m*Im_s
    dIm_s += t_21*(c*Sm_s*i01*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7) + c*Sm_s*i21*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7))
    dIm_s += t_12*(c*Sm_s*i10*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7) + c*Sm_s*i12*p_m/(w11 + i11 + r11+ t_21*(w01 + w21 + i01 + i21 + r01 + r21) + t_12*(w10 + w12 + i10 + i12 + r10 + r12) +1e-7))
    
    #Neamrolt
    dSm_ne = 0
    dIm_ne = 0

    return [dw00, dw01, dw02, dw10, dw11, dw12, dw20, dw21, dw22, di00,di01,di02,di10,di11,di12,di20,di21,di22,dr00,dr01,dr02,dr10,dr11,dr12,dr20,dr21,dr22,dd00,dd01,dd02,dd10,dd11,dd12,dd20,dd21,dd22, dSm_no, dIm_no, dSm_s, dIm_s, dSm_ne, dIm_ne]



p_h=0.1
p_m=0.5
p_11=1
t_11 =1


p_12=0.7367226
p_21=0.0564963

t_12=0.4
t_21=0.6



Sh_no0, Sh_s0 , Sh_ne0 = 7000-95 , 3000-1, 8300
Ih_no0,Ih_s0 , Ih_ne0 = 58 , 1, 0
Dh_no0 , Dh_s0, Dh_ne0 = 5, 0, 0
Rh_no0 , Rh_s0, Rh_ne0 = 52, 0, 0
Sm_no0 ,Sm_s0, Sm_ne0 = 21600*7/13 , 21600*(1-7/13) , 0
Im_no0 ,Im_s0 , Im_ne0 = 1000, 0 , 0

Sh_0={'no' :Sh_no0, 's' : Sh_s0, 'ne': Sh_ne0}
Ih_0={'no' :Ih_no0, 's' : Ih_s0, 'ne': Ih_ne0}
Dh_0={'no' :Dh_no0, 's' : Dh_s0, 'ne': Dh_ne0}
Rh_0={'no' :Rh_no0, 's' : Rh_s0, 'ne': Rh_ne0}
Sm_0={'no' :Sm_no0, 's' : Sm_s0, 'ne': Sm_ne0}
Im_0={'no' :Im_no0, 's' : Im_s0, 'ne': Im_ne0}

Y0 ={'no' : [Sh_0['no'] , Ih_0['no'],Dh_0['no'],Rh_0['no'] , Sm_0['no'], Im_0['no']],
      's' : [Sh_0['s'] , Ih_0['s'],Dh_0['s'],Rh_0['s'],Sm_0['s'], Im_0['s'] ],
     'ne' : [Sh_0['ne'] , Ih_0['ne'],Dh_0['ne'],Rh_0['ne'] ,Sm_0['ne'], Im_0['ne']]  }

Y0_bis = [Sm_0['no'], Im_0['no'], Sm_0['s'], Im_0['s'], Sm_0['ne'], Im_0['ne']]

# tableau residents , resident [v][w] la proportion de personne de la ville v (prime) qui habitent en w

workers_coef = {
    'no': {'no': 0.048, 's': 0.796, 'ne': 0.156},
    's': {'no': 0.046, 's': 0.792, 'ne': 0.162},
    'ne': {'no': 0.05, 's': 0.792, 'ne': 0.158}
    }

choix = ['no', 's', 'ne']

population_residente = {"no": 7000, "s": 3000, "ne": 8300}

duration = 300# durée de la plage temporelle étudiée
time_values = np.linspace(19, duration, duration + 1)

def population_presente():
    #Calcule la population présente dans une ville à un instant donné.
    
    # Ceux qui habitent et travaillent dans la ville
    workers = {'ne': {'ne': 0, 's': 0, 'no': 0}, 's': {'ne': 0, 's': 0, 'no': 0}, 'no': {'ne': 0, 's': 0, 'no': 0}}
    for ville in choix:
        workers[ville][ville] = population_residente[ville]*workers_coef[ville][ville]
        for v in choix:
            if v != ville:
                workers[v][ville] = population_residente[v]*workers_coef[v][ville]
                workers[ville][v] = population_residente[ville]*workers_coef[ville][v]

    
        # Population totale présente
    return workers

i0 = [240,3,0,0,0,0,0,0,0]
r0 = [0,0,0,0,0,0,0,0,0]
d0 = [0,0,0,0,0,0,0,0,0]



def creation_Y0():
    Y0=[]
    workers = population_presente()
    for v in choix:
        for w in choix:
            Y0.append(workers[v][w])
    for element in i0:
        Y0.append(element)
    for element in r0:
        Y0.append(element)
    for element in d0:
        Y0.append(element)
    for element in Y0_bis:
        Y0.append(element)
    return Y0


def resolution():
    mu_m=1/27
    c = 1
    gamma_h = 1/5
    rho = 0.03
    param_values= (c, gamma_h, rho, mu_m, p_h, p_m, p_11, p_12, p_21, t_11, t_12, t_21)
    Y0 = creation_Y0()
    valeur_model = integrate.odeint(deriv_workers, Y0, time_values, args=tuple(param_values))
    return valeur_model




prediction = resolution()
S_no = prediction[:, 0] + prediction[:, 1] + prediction[:, 2]
S_s = prediction[:, 3] + prediction[:, 4] + prediction[:, 5]
S_ne = prediction[:, 6] + prediction[:, 7] + prediction[:, 8]
I_no = prediction[:, 9] + prediction[:, 10] + prediction[:, 11]
I_s = prediction[:, 12] + prediction[:, 13] + prediction[:, 14]
I_ne = prediction[:, 15] + prediction[:, 16] + prediction[:, 17]
R_no = prediction[:, 18] + prediction[:, 19] + prediction[:, 20]
R_s = prediction[:, 21] + prediction[:, 22] + prediction[:, 23]
R_ne = prediction[:, 24] + prediction[:, 25] + prediction[:, 26]
D_no = prediction[:, 27] + prediction[:, 28] + prediction[:, 29]
D_s = prediction[:, 30] + prediction[:, 31] + prediction[:, 32]
D_ne = prediction[:, 33] + prediction[:, 34] + prediction[:, 35]
Sm_no = prediction[:, 36]
Im_no = prediction[:, 37]
Sm_s = prediction[:, 38]
Im_s = prediction[:, 39]
Sm_ne = prediction[:, 40]
Im_ne = prediction[:, 41]
def fitting_s(plot=True, max_nfev=None):
    from fitting import fit_sorya

    return fit_sorya(plot=plot, max_nfev=max_nfev)


def fitting_no(plot=True, max_nfev=None):
    from fitting import fit_noltrame

    return fit_noltrame(plot=plot, max_nfev=max_nfev)


def fitting_ne(plot=True, max_nfev=None):
    from fitting import fit_neamrolt

    return fit_neamrolt(plot=plot, max_nfev=max_nfev)


def fit_all_cities(plot=True, max_nfev=None):
    """Fit and return the model for all three cities."""
    results = {}
    for city, fitting_function in (
        ("Noltrame", fitting_no),
        ("Sorya", fitting_s),
        ("Neamrolt", fitting_ne),
    ):
        result, predictions = fitting_function(plot=plot, max_nfev=max_nfev)
        results[city] = (result, predictions)
        print(f"{city} - paramètres ajustés : {result.x}")
    return results


if __name__ == "__main__":
    fit_all_cities()