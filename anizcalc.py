import numpy as np
from const import *


def calc_tsum_spks(t_spk):
    m = np.zeros((tsum_spk_num, histo_size), dtype=np.int64)
    
    for i in range(tsum_spk_num):
        m[i] = t_spk[2*i] + t_spk[2*i+1]
        
    return m


def calc_xcenters_peak(tm_spk):
    argnum_min, argnum_max = 100, 3500
    xi_w_range = 100
    max_el_num, max_el = np.zeros(tsum_spk_num, dtype=np.uint32), np.zeros(tsum_spk_num, dtype=np.uint32)
    xcenters = np.zeros(tsum_spk_num, dtype=np.int32)
    
    for i in range(tsum_spk_num):
        max_el_num[i] = argnum_min + np.argmax(tm_spk[i, argnum_min:argnum_max])
        max_el[i] = tm_spk[i][max_el_num[i]]
        
        xi_range = np.arange(max_el_num[i]-xi_w_range, max_el_num[i]+xi_w_range-1)
        yi = xi_range * tm_spk[i][xi_range]
        s = np.sum(tm_spk[i][xi_range])

        if (s <= 0):
            xcenters[i] = 0
        else:
            xcenters[i] = round(np.sum(yi) / s)
        
    return xcenters


def calc_shifts(xcenters):
    shifts = np.zeros(tsum_spk_num, dtype=np.int32)
    for i in range(1, tsum_spk_num):
        shifts[i] = xcenters[0] - xcenters[i]

    return shifts


def swap_spks(t_spk, xcenters, nucleus_type=0):
    for i in range(nucleus_type, t_spk_num, 2):
        xc = round(xcenters[i // 2])
        """
        if xc < histo_size // 2:
            p = np.zeros(xc)
            np.copyto(p, t_spk[i][xc:])
            t_spk[i][xc+1:2*xc+1] = t_spk[i][:xc][::-1]
            t_spk[i][:xc] = p[::-1][:xc]
        """
        for j in range(1, histo_size):
            if j > xc or xc + j > histo_size - 1 or xc - j < 0:
                break
            tmp = t_spk[i][xc+j]
            t_spk[i][xc+j] = t_spk[i][xc-j]
            t_spk[i][xc-j] = tmp


def shift_spks(t_spk, xshifts):
    for i in range(t_spk_num):
        t_spk[i] = np.roll(t_spk[i], xshifts[i // 2])


#check this function
def calc_S(t_spk):
    S_start, S_stop = np.zeros(det_num), np.zeros(det_num)
    ind_start = ((1, 3, 5), (0, 7, 9), (2, 6, 11), (4, 8, 10))
    ind_stop = ((0, 2, 4), (1, 6, 8), (3, 7, 10), (4, 9, 11))

    for i in range(det_num):
        S_start[i] = np.sum(t_spk[ind_start[i], ])
        S_stop[i] = np.sum(t_spk[ind_stop[i], ])
    
    return S_start, S_stop


def calc_bg(t_spk, typ="const"):
    bg = np.ones((t_spk_num, histo_size))
    x_range = np.arange(0, histo_size)

    if typ is "const":
        bg_start, bg_stop = 700, 800
        for i in range(t_spk_num):
            bg[i] *= int(np.mean(t_spk[i][bg_start:bg_stop]))
    elif typ is "line":
        bg_start, bg_stop = 500, 1000
        for i in range(t_spk_num):
            z = np.polyfit(x_range[bg_start:bg_stop],
                           t_spk[i][bg_start:bg_stop],
                           1)
            p = np.poly1d(z)
            bg[i] = p(x_range)
    elif typ is "poly":
        bg_start, bg_stop = 500, 1500
        for i in range(t_spk_num):
            z = np.polyfit(x_range[bg_start:bg_stop],
                           t_spk[i][bg_start:bg_stop],
                           2)
            p = np.poly1d(z)
            bg[i] = p(x_range)
    elif typ is "ones":
        None

    bg[bg < 0] = 0
        
    return bg


def substract_bg(t_spk, bg):
    for i in range(t_spk_num):
        t_spk[i] = t_spk[i] - bg[i]
        t_spk[i][t_spk[i] <= 0] = 1.0


def calc_X90_X180(t_spk):
    X90, X180 = np.ones(histo_size), np.ones(histo_size)
    X90_ind = (0, 1, 4, 5, 6, 7, 10, 11)
    X180_ind = (2, 3, 8, 9)
    
    for i in range(histo_size):
        for ind in X90_ind:
            X90[i] *= float(t_spk[ind][i])**(1/8)
        #v1 = t_spk[0][i] * t_spk[1][i] * t_spk[4][i] * t_spk[5][i] * t_spk[6][i] * t_spk[7][i] * t_spk[10][i] * t_spk[11][i]

        for ind in X180_ind:
            X180[i] *= float(t_spk[ind][i])**(1/4)

    return X90, X180


def calc_comp_X90_X180(X90, X180, comp):
    compX90, compX180 = np.zeros(histo_size // comp), np.zeros(histo_size // comp)

    for p in range(0, histo_size // comp):
        for j in range(0, comp):
            if p * comp + j > histo_size:
                break
            compX90[p] += X90[p*comp+j]
            compX180[p] += X180[p*comp+j]
            
    return compX90 / comp, compX180 / comp


def calc_R(X90, X180, comp):
    R = np.zeros(histo_size // comp)

    for p in range(0, histo_size // comp):
        for j in range(0, comp):
            if p * comp + j > histo_size:
                break
            R[p] += 2.0 * (X180[p*comp+j] - X90[p*comp+j]) / (X180[p*comp+j] + 2.0 * X90[p*comp+j])
        #R[j] = 2.0 * (compX180[j] - compX90[j]) / (compX180[j] + 2.0 * compX90[j])

    return R / comp


def calc_dR(t_spk, bg, X90, X180, comp):
    err_sum = np.zeros((2, histo_size), dtype=float)
    dR = np.zeros(histo_size, dtype=float)
    dRcomp = np.zeros(histo_size // comp, dtype=float)
    
    for j in range(0, histo_size):
        err_sum[0][j] = (t_spk[0][j] + 2.0 * bg[0][j]) / (t_spk[0][j])**2 + \
                        (t_spk[1][j] + 2.0 * bg[1][j]) / (t_spk[1][j])**2 + \
		        (t_spk[4][j] + 2.0 * bg[4][j]) / (t_spk[4][j])**2 + \
		        (t_spk[5][j] + 2.0 * bg[5][j]) / (t_spk[5][j])**2 + \
		        (t_spk[6][j] + 2.0 * bg[6][j]) / (t_spk[6][j])**2 + \
		        (t_spk[7][j] + 2.0 * bg[7][j]) / (t_spk[7][j])**2 + \
		        (t_spk[10][j] + 2.0 * bg[10][j]) / (t_spk[10][j])**2 + \
		        (t_spk[11][j] + 2.0 * bg[11][j]) / (t_spk[11][j])**2
        err_sum[0][j] /= 64.0

        err_sum[1][j] = (t_spk[2][j] + 2.0 * bg[2][j]) / (t_spk[2][j])**2 + \
			(t_spk[3][j] + 2.0 * bg[3][j]) / (t_spk[3][j])**2 + \
			(t_spk[8][j] + 2.0 * bg[8][j]) / (t_spk[8][j])**2 + \
			(t_spk[9][j] + 2.0 * bg[9][j]) / (t_spk[9][j])**2
        err_sum[1][j] /= 16.0
    
    dR = 6.0 * X180 * X90 / (X180 + 2.0 * X90)**2 * (err_sum[0] + err_sum[1])**0.5
    """
    for j in range(0, histo_size):
        v1 = (X90[j] + 2.0 * X180[j])**2 * (err_sum[0][j] + err_sum[1][j])**0.5
        if v1 <= 0.0:
            return dR
        dR[j] = 6.0 * X90[j] * X180[j] / v1
 
    #breakpoint()
    """
    for p in range(0, histo_size // comp):
        for j in range(0, comp):
            if p * comp + j >= histo_size:
                break
            dRcomp[p] += (dR[p*comp+j])**2

    dRcomp = (dRcomp)**0.5 / comp

    return dRcomp
