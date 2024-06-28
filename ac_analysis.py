from lib import ng_raw_read, to_data_frames, get_column_as_array, lookup, view_headers, PlotManager,measure_ac_parameters,ac_analysis
import numpy as np
import pandas as pd
from prettytable import PrettyTable

if __name__ == '__main__':
    
    AC_simNumber = 0 # assuming that it is the first analysis
    (arrs, plots) = ng_raw_read('ota-5t_tb2_ac.raw')
    
    if plots[AC_simNumber][b'plotname'] != b'AC Analysis':
        raise Exception("This Data Frame doesn't include AC Analysis")
    
    dfs = to_data_frames((arrs, plots))
    df = dfs[0]
    
    # view_headers(df)

    ac_analysis(df,save=True)



    '''example Usage to get data for more post processing 
    # Call the function with data
        freq = get_column_as_array(df,'frequency')
    vout_mag = get_column_as_array(df,'v(vout)')
    ac_parameters = measure_ac_parameters(frequencies, vout)

    # Accessing the returned data
    vout_mag = ac_parameters["vout_mag"]
    vout_db = ac_parameters["vout_db"]
    vout_phase_margin = ac_parameters["vout_phase_margin"]
    A0 = ac_parameters["A0"]
    A0_db = ac_parameters["A0_db"]
    UGF = ac_parameters["UGF"]
    PM = ac_parameters["PM"]
    BW_3dB = ac_parameters["BW_3dB"]
    GBW = ac_parameters["GBW"]

    # Print the results
    print("vout_mag:", vout_mag)
    print("vout_db:", vout_db)
    print("vout_phase_margin:", vout_phase_margin)
    print("A0:", A0)
    print("A0_db:", A0_db)
    print("UGF:", UGF)
    print("PM:", PM)
    print("BW_3dB:", BW_3dB)
    print("GBW:", GBW)
    '''