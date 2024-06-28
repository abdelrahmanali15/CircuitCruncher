from lib import ng_raw_read, to_data_frames, get_column_as_array, lookup, PlotManager,view_headers,op_sim,save_fet_vars
from prettytable import PrettyTable

if __name__ == '__main__':
    
    Op_simNumber = 0
    (arrs, plots) = ng_raw_read('')
    
    print(arrs)
    print(plots[Op_simNumber][b'plotname']) # Print Simulation type to make sure it's what we want
    if plots[Op_simNumber][b'plotname'] != b'Operating Point':
        raise(f"This Data Frame doesn't include Operating Point Analysis")
    
    

    dfs = to_data_frames((arrs, plots))

    df = dfs[0]  # Get the first DataFrame Assuming that it's the first analysis in the Raw File
    # view_headers(df) # Print variables in dataframe to make sure that it's the one we need


    op_sim(df,html=True,additional_vars=['cgs','gmbs','vgs'],custom_expressions={"Avi":"gm/gds"}) # Extract Transistors OP Data