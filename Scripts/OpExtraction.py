import CircuitCruncher as cc
import sys


# Change this to where you downloaded the repo
# Enable this if: t you didn't Setup repo on device using python3 -m pip install --user -e 
# sys.path.append('/home/tare/Repos/CircuitCruncher/CircuitCruncher')

op_raw =  '5t-ota_tb.raw'
output_dir=''

(arrs, plots) = cc.ng_raw_read(op_raw)
OP_simNumber = cc.simType('op',plots)


dfs = cc.to_data_frames((arrs, plots))

df = dfs[OP_simNumber]  # Get the first DataFrame Assuming that it's the first analysis in the Raw File
# view_headers(df) # Print variables in dataframe to make sure that it's the one we need


# You can add variables other than default printed variables also add simple expresion of variables 
cc.op_sim(df,html=True,additional_vars=['cgs','gmbs','vgs','cgb','cgd'],custom_expressions={"Avi":"gm*ro","Cgg": "cgb+cgs+cgd"},output_file=output_dir+'dc_op') # Extract Transistors OP Data