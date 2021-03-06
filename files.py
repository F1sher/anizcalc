from const import *

import numpy as np
from os import scandir
from os import path
from os import mkdir
from struct import pack
from struct import unpack

histo_finisize = 512

def get_histos_from_folder(foldername):
    foldername = foldername if foldername[-1] == "/" else foldername + "/"
   
    en_spk = []
    for fname in histo_en_fnames:
        with open(foldername + fname, "rb") as fd:
            fd.seek(histo_finisize, 0)
            en_spk.append(fd.read(histo_fsize))
            en_spk[-1] = unpack(str(histo_size) + "i", en_spk[-1])

    t_spk = []
    for fname in histo_t_fnames:
        with open(foldername + fname, "rb") as fd:
            fd.seek(histo_finisize, 0)
            t_spk.append(fd.read(histo_fsize))
            t_spk[-1] = unpack(str(histo_size) + "i", t_spk[-1])
            
    return np.array(en_spk, dtype=np.int64), np.array(t_spk, dtype=np.int64)


def save_tm_spk(foldername, tm_spk):
    if not path.isdir(foldername):
        mkdir(foldername)
        
    i = 0
    zero_spk = [0 for i in range(histo_size)]
    for fname in histo_t_fnames:
        with open(path.join(foldername, fname), "wb+") as fd:
            fd.seek(histo_finisize, 0)
            if i % 2 == 0:
                fd.write(pack(str(histo_size) + "i", *tm_spk[i // 2]))
            else:
                fd.write(pack(str(histo_size) + "i", *zero_spk))
            i += 1


def save_t_spk(foldername, t_spk):
    if not path.isdir(foldername):
        mkdir(foldername)
        
    for i, fname in enumerate(histo_t_fnames):
        with open(path.join(foldername, fname), "wb+") as fd:
            fd.seek(histo_finisize, 0)
            fd.write(pack(str(histo_size) + "i", *t_spk[i]))


def save_en_spk(foldername, en_spk):
    if not path.isdir(foldername):
        mkdir(foldername)

    for i, fname in enumerate(histo_en_fnames):
        with open(path.join(foldername, fname), "wb+") as fd:
            fd.seek(histo_finisize, 0)
            fd.write(pack(str(histo_size) + "i", *en_spk[i]))


def save_X90_X180(foldername, X90, X180, comp):
    if not path.isdir(foldername):
        mkdir(foldername)

    np.savetxt(path.join(foldername, "X90c{:d}.dat".format(comp)),
               np.column_stack([np.arange(histo_size // comp), X90]))

    np.savetxt(path.join(foldername, "X180c{:d}.dat".format(comp)),
               np.column_stack([np.arange(histo_size // comp), X180]))


def save_R(foldername, R, dR, comp, zero):
    if not path.isdir(foldername):
        mkdir(foldername)

    np.savetxt(path.join(foldername, "anizc{:d}.dat".format(comp)),
               np.column_stack([np.arange(histo_size // comp - zero), R[zero:], dR[zero:]]),
               fmt="%d %.6f %.6f")
    
    
#def save_bg_ascii(foldername, bg):
#    if not path.isdir(foldername):
#        mkdir(foldername)

    
