# from CircuitCruncher import * #import the all functions from local library
import CircuitCruncher as cc
import sys

# Change this to where you downloaded the repo
# Todo: Setup repo on device using python3 -m pip install --user -e 
sys.path.append('/home/tare/Repos/CircuitCruncher/CircuitCruncher')


op_raw = '5t-ota_tb.raw'

(arrs, plots) = cc.ng_raw_read(op_raw)
OP_simNumber = cc.simType('op',plots)


dfs = cc.to_data_frames((arrs, plots))

df = dfs[OP_simNumber]  # Get the first DataFrame Assuming that it's the first analysis in the Raw File
# view_headers(df) # Print variables in dataframe to make sure that it's the one we need

save_file_name ='save.spi'
saveVars = ['vgs','vds', 'vdsat', 'gm','gmbs', 'id', 'vth', 'gds','cgs','cgb','cgd'] # set variables to be saved in save.spi file
cc.save_fet_vars(df.columns,saveVars,savefilename = save_file_name) # create save.spi file in sim directory 

