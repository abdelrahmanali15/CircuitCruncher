from lib import ng_raw_read, to_data_frames, get_column_as_array, lookup, PlotManager,view_headers,op_sim,save_fet_vars
from prettytable import PrettyTable

if __name__ == '__main__':
    
    Op_simNumber = 0
    (arrs, plots) = ng_raw_read('/home/tare/XschemForSky/Projects/ota-5t/xschem/sim2/test_analog.raw')
    
    
    print(f"Simulation is {plots[Op_simNumber][b'plotname']}") # Print Simulation type to make sure it's what we want
    if plots[Op_simNumber][b'plotname'] != b'Operating Point':
        raise(f"This Data Frame doesn't include Operating Point Analysis")
    
    

    dfs = to_data_frames((arrs, plots))

    df = dfs[0]  # Get the first DataFrame Assuming that it's the first analysis in the Raw File
    # view_headers(df) # Print variables in dataframe to make sure that it's the one we need


    saveVars = ['vgs','vds', 'vdsat', 'gm','gmbs', 'id', 'vth', 'gds','cgs'] # set variables to be saved in save.spi file
    save_fet_vars(df.columns,saveVars,'/home/tare/XschemForSky/Projects/ota-5t/xschem/save_test_analog.spi') # create save.spi file 


