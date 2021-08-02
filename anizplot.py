#!/usr/bin/env python

import click
from os import path, mkdir, system

from files import *
from anizcalc import *


@click.command()
@click.option("--dir", default="./", help="Directory with TDPAC spectra.")
@click.option("--comp", default=1, type=int, help="Compression of anisotropy.")
def main(dir, comp):
    """
    Calculate X90, X180 and anisotropy R(t).
    Results will be saved in "dir/anizc{comp}".
    """
    user_input = {}
    user_input["spkfolder"] = dir
    user_input["compression"] = comp

    en_spk, t_spk = get_histos_from_folder(user_input["spkfolder"])
    print("user_input = ", user_input)
    
    tsum_spk = calc_tsum_spks(t_spk)
    #save_tm_spk(path.join(user_input["spkfolder"], "t_sum"), tsum_spk)
    #save_en_spk(path.join(user_input["spkfolder"], "t_sum"), en_spk)
    
    xcenters = calc_xcenters_peak(tsum_spk)
    xshifts = calc_shifts(xcenters)
    swap_spks(t_spk, xcenters, 0)
    shift_spks(t_spk, xshifts)
    #save_t_spk(path.join(user_input["spkfolder"], "t_shifted"), t_spk)
    #save_en_spk(path.join(user_input["spkfolder"], "t_shifted"), en_spk)

    calc_S(t_spk)

    bg = calc_bg(t_spk, typ="line")
    #save_t_spk(path.join(user_input["spkfolder"], "t_bg"), np.array(bg, dtype=np.int32))
    #save_en_spk(path.join(user_input["spkfolder"], "t_bg"), en_spk)

    substract_bg(t_spk, bg)
    #save_t_spk(path.join(user_input["spkfolder"], "t_wo_bg"), t_spk)
    #save_en_spk(path.join(user_input["spkfolder"], "t_wo_bg"), en_spk)

    X90, X180 = calc_X90_X180(t_spk)
    #save_X90_X180(path.join(user_input["spkfolder"], "test_anizc1"), X90, X180, 1)

    compX90, compX180 = calc_comp_X90_X180(X90, X180, user_input["compression"])
    #save_X90_X180(path.join(user_input["spkfolder"], "test_anizc4"),
    #              compX90, compX180, user_input["compression"])

    R = calc_R(X90, X180, user_input["compression"])
    dR = calc_dR(t_spk, bg, X90, X180, user_input["compression"])
    
    save_foldername = path.join(user_input["spkfolder"], "anizc{:d}".format(user_input["compression"]))
    save_R(save_foldername, R, dR, user_input["compression"], xcenters[0] // user_input["compression"])
    #print("gnuplot inp = ", "{:s} \"plot \\\"{:s}\\\"\"".format("gnuplot -e",
    #                                   path.join(save_foldername, "anizc{:d}.dat".format(comp))))
    #system("{:s} \"plot \\\"{:s}\\\" with yerror; pause -1\"".format("gnuplot -e",
    #                                   path.join(save_foldername, "anizc{:d}.dat".format(comp))))
    
    
if __name__ == "__main__":
    main()
