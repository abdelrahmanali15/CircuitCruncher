import numpy as np
import pandas as pd
import re
from prettytable import PrettyTable 


def lookup(lookup_array: np.ndarray, lookup_value: float, lookup_return_array: np.ndarray):
        """
        Perform a linear interpolation to find the corresponding value in lookup_return_array
        for a given lookup_value based on lookup_array.

        Parameters:
        lookup_array (np.ndarray): Array of x-values for the interpolation.
        lookup_value (float): The x-value to look up.
        lookup_return_array (np.ndarray): Array of y-values for the interpolation.

        Returns:
        float: Interpolated y-value corresponding to lookup_value.
        """
        if not isinstance(lookup_array, np.ndarray):
            raise TypeError("lookup_array must be a numpy array")
        if not isinstance(lookup_return_array, np.ndarray):
            raise TypeError("lookup_return_array must be a numpy array")
        if not np.isscalar(lookup_value):
            raise TypeError("lookup_value must be a scalar")
        if len(lookup_array) != len(lookup_return_array):
            raise ValueError("lookup_array and lookup_return_array must have the same length")
        if len(lookup_array) < 2:
            raise ValueError("lookup_array and lookup_return_array must have at least two elements")

        # Perform the linear interpolation
        return np.interp(lookup_value, lookup_array, lookup_return_array)

def measure_ac_parameters(frequencies, vout):
    vout_mag = np.abs(vout)
    vout_db = 20 * np.log10(vout_mag)
    vout_phase_margin = np.angle(vout, deg=True) + 180

    # Find the index closest to 1 kHz
    idx_1kHz = np.argmin(np.abs(frequencies - 10))
    A0 = vout_mag[idx_1kHz]
    A0_db = vout_db[idx_1kHz]

    # Unity gain frequency
    ugf = np.interp(1, vout_mag[::-1], frequencies[::-1])

    # Find the index closest to the unity gain frequency
    idx_ugf = np.argmin(np.abs(frequencies - ugf))
    PM = vout_phase_margin[idx_ugf]

    # Calculate the 3 dB bandwidth
    BW_3dB_freqs = frequencies[vout_db >= (A0_db - 3)]
    if len(BW_3dB_freqs) > 0:
        BW_3dB = BW_3dB_freqs[-1] - BW_3dB_freqs[0]
    else:
        BW_3dB = None

    # Calculate Gain-Bandwidth Product (GBW)
    GBW = A0 * ugf


    return {
        "vout_mag": vout_mag,
        "vout_db": vout_db,
        "vout_phase_margin": vout_phase_margin,
        "A0": A0,
        "A0_db": A0_db,
        "UGF": ugf,
        "PM": PM,
        "BW_3dB": abs(BW_3dB),
        "GBW": (GBW)
    }


'''example Usage
# Call the function with data
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


def calculate_propagation_delay(time, vout, threshold_ratio=0.5):
    """
    Calculate the propagation delay in a transient simulation.

    Parameters:
    time (np.ndarray): Array of time points.
    vout (np.ndarray): Array of output voltage values at corresponding time points.
    threshold_ratio (float): Ratio of the peak value to use as the threshold (default is 0.5 for 50%).

    Returns:
    float: Propagation delay in the same units as the time array.

    Propagation delay.  Input differential Vdiff is set to the overdrive
    voltage.  Set PWL source to the negative of its value, then switch to the
    positive.  Measure the time for the output to change state (cross
    Vdd / 2). Where Vdd/2 is the DC output voltage
    """
    # Find the peak value of vout
    peak_vout = np.max(vout)

    # Calculate the threshold value
    threshold = peak_vout * threshold_ratio

    # Find the index where vout first crosses the threshold
    crossing_indices = np.where(vout >= threshold)[0]
    if len(crossing_indices) == 0:
        return None  # No crossing found

    # Time of the first crossing
    crossing_time = time[crossing_indices[0]]

    # Assuming the input signal starts at time 0 and crosses the threshold at time 0
    # Adjust this if the input signal is not provided or starts at a different time
    # May need to be adjusted later

    # Propagation delay is the time at which the output crosses the threshold
    propagation_delay = crossing_time

    return propagation_delay


def calculate_cmrr(time, vout, vin, Vvdd, Vcm_min, Vcm_max):
    """
    Calculate the Common-Mode Rejection Ratio (CMRR) in dB.

    Parameters:
    time (np.ndarray): Array of time points.
    vout (np.ndarray): Array of output voltage values at corresponding time points.
    vin (np.ndarray): Array of input voltage values at corresponding time points.
    Vvdd (float): Supply voltage.
    Vcm_min (float): Minimum common-mode voltage.
    Vcm_max (float): Maximum common-mode voltage.

    Returns:
    float: CMRR in dB.
    """
    threshold = Vvdd / 2

    # Find the times when vout crosses the threshold
    crossings = np.where(np.diff(np.sign(vout - threshold)))[0]

    if len(crossings) < 4:
        raise ValueError("Insufficient threshold crossings found in vout.")

    # Extract times of the first four crossings
    t_cross1, t_cross2, t_cross3, t_cross4 = time[crossings[:4]]

    # Find corresponding input voltages
    vhigh1 = np.interp(t_cross1, time, vin)
    vlow1 = np.interp(t_cross2, time, vin)
    vhigh2 = np.interp(t_cross3, time, vin)
    vlow2 = np.interp(t_cross4, time, vin)

    # Calculate offset voltages
    voffset1 = 0.5 * (vhigh1 + vlow1) - Vcm_min
    voffset2 = 0.5 * (vhigh2 + vlow2) - Vcm_max

    # Calculate CMRR
    cmrr = (voffset1 - voffset2) / (Vcm_max - Vcm_min)
    cmrr_db = 20 * np.log10(abs(cmrr))

    return cmrr_db


''' 
# Example usage with dummy data
time = np.linspace(0, 1e-6, 1000)  # Time vector from 0 to 1 microsecond
vout = np.sin(2 * np.pi * 1e6 * time)  # Example output voltage (replace with actual data)
vin = np.sin(2 * np.pi * 1e6 * time) + 0.1  # Example input voltage (replace with actual data)
Vvdd = 5.0  # Example supply voltage
Vcm_min = 0.5  # Example minimum common-mode voltage
Vcm_max = 1.5  # Example maximum common-mode voltage

# Calculate CMRR
cmrr_db = calculate_cmrr(time, vout, vin, Vvdd, Vcm_min, Vcm_max)
print(f"CMRR: {cmrr_db} dB")

'''



# def parse_columns(columns):
#     """
#     Parses the column names of a DataFrame to extract variable names and transistor numbers.

#     This function looks for specific variables within square brackets in the column names and associates them 
#     with their corresponding transistor numbers (e.g., xm1, xm2, etc.). It returns a dictionary where the keys 
#     are the variable names and the values are dictionaries. In these dictionaries, the keys are the transistor 
#     numbers and the values are the full column names.

#     Parameters:
#     ----------
#     columns : list of str
#         The list of column names from a DataFrame.

#     Returns:
#     -------
#     dict of dict
#         A dictionary where:
#             - The keys are variable names (e.g., 'vds', 'vdsat', 'gm', 'id', 'vth', 'gds').
#             - The values are dictionaries where:
#                 - The keys are transistor numbers (e.g., '1', '2', '3').
#                 - The values are the full column names from the DataFrame.
#     """

    
#     variables = ['vds', 'vdsat', 'gm', 'id', 'vth', 'gds']
#     parsed_columns = {var: {} for var in variables}
    
#     pattern = re.compile(r'\[([^\]]+)\]')
    
#     for col in columns:
#         matches = pattern.findall(col)
#         if matches:
#             var_name = matches[0]
#             if var_name in variables:
#                 # Extract the transistor number (e.g., xm1, xm2, etc.)
#                 trans_match = re.search(r'xm(\d+)', col)
#                 if trans_match:
#                     transistor_num = trans_match.group(1)
#                     parsed_columns[var_name][transistor_num] = col

#     return parsed_columns




# def op_sim(df):
#     """
#     Automates the process of extracting required columns from the DataFrame, calculating gm/id and vstar,
#     and displaying the results in a formatted table using PrettyTable.

#     Parameters:
#     ----------
#     df : DataFrame
#         The DataFrame containing the columns to be processed.

#     Returns:
#     -------
#     None
#         Prints the PrettyTable containing the gm/id and Vstar and other DC OP Parameters values for each transistor.
#     """
#     # Define the column parsing function
#     def parse_columns(columns):
#         variables = ['vds', 'vdsat', 'gm', 'id', 'vth', 'gds']
#         parsed_columns = {var: {} for var in variables}
        
#         pattern = re.compile(r'\[([^\]]+)\]')
        
#         for col in columns:
#             matches = pattern.findall(col)
#             if matches:
#                 var_name = matches[0]
#                 if var_name in variables:
#                     # Extract the transistor number (e.g., xm1, xm2, etc.)
#                     trans_match = re.search(r'xm(\d+)', col)
#                     if trans_match:
#                         transistor_num = trans_match.group(1)
#                         parsed_columns[var_name][transistor_num] = col

#         return parsed_columns

#     # Extract the required columns using the parse_columns function
#     columns = df.columns
#     parsed_columns = parse_columns(columns)
    
#     # Function to get column as array or NaN if column is missing
#     def get_column_as_array(df, col_name):
#         return df[col_name].values if col_name in df else np.nan

#     # Helper function to format values with appropriate units
#     def format_value(val):
#         if np.isnan(val):
#             return "NaN"
#         abs_val = abs(val)
#         if abs_val >= 1e9:
#             return f"{val/1e9:.2f}G"
#         elif abs_val >= 1e6:
#             return f"{val/1e6:.2f}M"
#         elif abs_val >= 1e3:
#             return f"{val/1e3:.2f}k"
#         elif abs_val >= 1:
#             return f"{val:.2f}"
#         elif abs_val >= 1e-3:
#             return f"{val*1e3:.2f}m"
#         elif abs_val >= 1e-6:
#             return f"{val*1e6:.2f}μ"
#         elif abs_val >= 1e-9:
#             return f"{val*1e9:.2f}n"
#         else:
#             return f"{val*1e12:.2f}p"
    
#     # Get all transistor numbers
#     all_transistors = set()
#     for var_dict in parsed_columns.values():
#         all_transistors.update(var_dict.keys())
    
#     # Extract gm and id arrays for each transistor
#     gm = {num: get_column_as_array(df, parsed_columns['gm'].get(num, None)) for num in all_transistors}
#     id = {num: get_column_as_array(df, parsed_columns['id'].get(num, None)) for num in all_transistors}
#     vds = {num: get_column_as_array(df, parsed_columns['vds'].get(num, None)) for num in all_transistors}
#     vdsat = {num: get_column_as_array(df, parsed_columns['vdsat'].get(num, None)) for num in all_transistors}
#     vth = {num: get_column_as_array(df, parsed_columns['vth'].get(num, None)) for num in all_transistors}
#     gds = {num: get_column_as_array(df, parsed_columns['gds'].get(num, None)) for num in all_transistors}
    
    
#     # Calculate gm/id and v_star and ro
#     gmid = {num: gm[num] / id[num] if not np.isnan(gm[num]).all() and not np.isnan(id[num]).all() else np.nan for num in gm}
#     v_star = {num: 2 * id[num] / gm[num] if not np.isnan(gm[num]).all() and not np.isnan(id[num]).all() else np.nan for num in gm}
#     ro = {num: 1 / gds[num] if not np.isnan(gds[num]).all() else np.nan for num in gds}

    
#     # Create a PrettyTable object
#     table = PrettyTable()
    
#     # Define headers
#     table.field_names = ["Parameter"] + [f"M{num}" for num in sorted(all_transistors)]
    
#     # Add rows with formatted values
#     table.add_row(["gm/id"] + [format_value(gmid[num][0]) if not np.isnan(gmid[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["Vstar"] + [format_value(v_star[num][0]) if not np.isnan(v_star[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["Vdsat"] + [format_value(vdsat[num][0]) if not np.isnan(vdsat[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["vds"] + [format_value(vds[num][0]) if not np.isnan(vds[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["vth"] + [format_value(vth[num][0]) if not np.isnan(vth[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["gds"] + [format_value(gds[num][0]) if not np.isnan(gds[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["ro"] + [format_value(ro[num][0]) if not np.isnan(ro[num]).all() else "NaN" for num in sorted(all_transistors)])
#     # Center align the columns
#     table.align = "c"
    
#     # Print the table
#     print(table)





# def op_sim(df,output_file='output.txt',html=True):
#     """
#     Automates the process of extracting required columns from the DataFrame, calculating gm/id and vstar,
#     and displaying the results in a formatted table using PrettyTable.

#     Parameters:
#     ----------
#     df : DataFrame
#         The DataFrame containing the columns to be processed.

#     Returns:
#     -------
#     None
#         Prints the PrettyTable containing the gm/id and Vstar and other DC OP Parameters values for each transistor.
#     """
    # Define the column parsing function
    # def parse_columns(columns):
    #     variables = ['vds', 'vdsat', 'gm', 'id', 'vth', 'gds']
    #     parsed_columns = {var: {} for var in variables}

    #     pattern = re.compile(r'\[([^\]]+)\]')
    #     # hierarchy_pattern = re.compile(r'(@m(?:\.\w+)+)\.xm(\d+)\.')    #Doesnt work if no hirerchy i think
    #     # hierarchy_pattern = re.compile(r'(@m(?:\.\w+)+)\.msky130_fd_pr__\w+_01v8')  # Specific to sky130 pdk
    #     hierarchy_pattern = re.compile(r'(@m(?:\.\w+)+)\.(\w+)')  # Generalized pattern

    #     for col in columns:
    #         matches = pattern.findall(col)
    #         # print(f"Column: {col} -> Matches: {matches}")  # Debugging line
    #         if matches:
    #             var_name = matches[0]
    #             if var_name in variables:
    #                 # Extract the full path and transistor number (e.g., @m.xm1.msky130_fd_pr__nfet_01v8)
    #                 hierarchy_match = hierarchy_pattern.search(col)
    #                 # print(f"Hierarchy Match: {hierarchy_match}")  # Debugging line
    #                 if hierarchy_match:
    #                     full_path = hierarchy_match.group(1)
    #                     parsed_columns[var_name][full_path] = col

    #     print(f"Parsed Columns: {parsed_columns}")  # Debugging line
    #     return parsed_columns


    # # Extract the required columns using the parse_columns function
    # columns = df.columns
    # parsed_columns = parse_columns(columns)
    
#     # Function to get column as array or NaN if column is missing
#     def get_column_as_array(df, col_name):
#         return df[col_name].values if col_name in df else np.nan

#     # Helper function to format values with appropriate units
#     def format_value(val):
#         if np.isnan(val):
#             return "NaN"
#         abs_val = abs(val)
#         if abs_val >= 1e9:
#             return f"{val/1e9:.2f}G"
#         elif abs_val >= 1e6:
#             return f"{val/1e6:.2f}M"
#         elif abs_val >= 1e3:
#             return f"{val/1e3:.2f}k"
#         elif abs_val >= 1:
#             return f"{val:.2f}"
#         elif abs_val >= 1e-3:
#             return f"{val*1e3:.2f}m"
#         elif abs_val >= 1e-6:
#             return f"{val*1e6:.2f}μ"
#         elif abs_val >= 1e-9:
#             return f"{val*1e9:.2f}n"
#         else:
#             return f"{val*1e12:.2f}p"
    
#     # Get all transistor numbers
#     all_transistors = set()
#     for var_dict in parsed_columns.values():
#         all_transistors.update(var_dict.keys())
    
#     # Extract gm and id arrays for each transistor
#     gm = {num: get_column_as_array(df, parsed_columns['gm'].get(num, None)) for num in all_transistors}
#     id = {num: get_column_as_array(df, parsed_columns['id'].get(num, None)) for num in all_transistors}
#     vds = {num: get_column_as_array(df, parsed_columns['vds'].get(num, None)) for num in all_transistors}
#     vdsat = {num: get_column_as_array(df, parsed_columns['vdsat'].get(num, None)) for num in all_transistors}
#     vth = {num: get_column_as_array(df, parsed_columns['vth'].get(num, None)) for num in all_transistors}
#     gds = {num: get_column_as_array(df, parsed_columns['gds'].get(num, None)) for num in all_transistors}
    
#     # Calculate gm/id and v_star and ro
#     gmid = {num: gm[num] / id[num] if not np.isnan(gm[num]).all() and not np.isnan(id[num]).all() else np.nan for num in gm}
#     v_star = {num: 2 * id[num] / gm[num] if not np.isnan(gm[num]).all() and not np.isnan(id[num]).all() else np.nan for num in gm}
#     ro = {num: 1 / gds[num] if not np.isnan(gds[num]).all() else np.nan for num in gds}

#     # Create a PrettyTable object
#     table = PrettyTable()
    
#     # Define headers
#     table.field_names = ["Parameter"] + [f"{num}" for num in sorted(all_transistors)]
    
#     # Add rows with formatted values
#     table.add_row(["gm/id"] + [format_value(gmid[num][0]) if not np.isnan(gmid[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["Vstar"] + [format_value(v_star[num][0]) if not np.isnan(v_star[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["Vdsat"] + [format_value(vdsat[num][0]) if not np.isnan(vdsat[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["vds"] + [format_value(vds[num][0]) if not np.isnan(vds[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["vth"] + [format_value(vth[num][0]) if not np.isnan(vth[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["gds"] + [format_value(gds[num][0]) if not np.isnan(gds[num]).all() else "NaN" for num in sorted(all_transistors)])
#     table.add_row(["ro"] + [format_value(ro[num][0]) if not np.isnan(ro[num]).all() else "NaN" for num in sorted(all_transistors)])
#     # Center align the columns
#     table.align = "c"
    
#     # Print the table
#     print(table)

#      # Create a DataFrame to store the table data
#     table_data = {
#         "Parameter": ["gm/id", "Vstar", "Vdsat", "vds", "vth", "gds", "ro"]
#     }
#     for num in sorted(all_transistors):
#         table_data[num] = [
#             format_value(gmid[num][0]) if not np.isnan(gmid[num]).all() else "NaN",
#             format_value(v_star[num][0]) if not np.isnan(v_star[num]).all() else "NaN",
#             format_value(vdsat[num][0]) if not np.isnan(vdsat[num]).all() else "NaN",
#             format_value(vds[num][0]) if not np.isnan(vds[num]).all() else "NaN",
#             format_value(vth[num][0]) if not np.isnan(vth[num]).all() else "NaN",
#             format_value(gds[num][0]) if not np.isnan(gds[num]).all() else "NaN",
#             format_value(ro[num][0]) if not np.isnan(ro[num]).all() else "NaN"
#         ]
    
#     df_table = pd.DataFrame(table_data)
    
#     def save_table_html(df_table, output_html):
#         with open(output_html, 'w') as file:
#             file.write(
#                 df_table.style.set_table_styles([
#                     {'selector': 'thead th', 'props': [('background-color', '#aec6cf'), ('color', 'black'), ('text-align', 'center')]},
#                     {'selector': 'tbody td', 'props': [('text-align', 'center'), ('padding', '10px'), ('border', '2px solid #ddd')]},
#                     {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
#                     {'selector': 'tbody tr:hover', 'props': [('background-color', '#ffcccc')]}
#                 ]).set_caption("Transistor Parameters")
#                 .set_table_attributes('class="dataframe minimalist-table"')
#                 .hide(axis='index')
#                 .to_html()
#             )
#         print(f"Table saved as {output_html}")


#         # Save table as TXT
#     def save_table_txt(table, output_txt):
#         with open(output_txt, 'w') as file:
#             file.write(str(table))
#         print(f"Table saved as {output_txt}")
    
    
    
#     save_table_txt(table, output_file)

#     if html:
#         save_table_html(df_table, 'output.html')


'''"""
def op_sim(df, output_file='output.txt', html=True, additional_vars=None):
    """
    Automates the process of extracting required columns from the DataFrame, calculating gm/id and vstar,
    and displaying the results in a formatted table using PrettyTable.

    Parameters:
    ----------
    df : DataFrame
        The DataFrame containing the columns to be processed.
    output_file : str
        The name of the output file to save the table.
    html : bool
        Whether to save the table as an HTML file.
    additional_vars : list
        List of additional variables to include in the processing.

    Returns:
    -------
    None
        Prints the PrettyTable containing the gm/id and Vstar and other DC OP Parameters values for each transistor.
    """
    # Define the column parsing function
    def parse_columns(columns, variables):
        parsed_columns = {var: {} for var in variables}

        pattern = re.compile(r'\[([^\]]+)\]')
        hierarchy_pattern = re.compile(r'(@m(?:\.\w+)+)\.(\w+)')  # Generalized pattern

        for col in columns:
            matches = pattern.findall(col)
            if matches:
                var_name = matches[0]
                if var_name in variables:
                    # Extract the full path and transistor number (e.g., @m.xm1.msky130_fd_pr__nfet_01v8)
                    hierarchy_match = hierarchy_pattern.search(col)
                    if hierarchy_match:
                        full_path = hierarchy_match.group(1)
                        parsed_columns[var_name][full_path] = col

        return parsed_columns

    # Default variables
    default_variables = ['vds', 'vdsat', 'gm', 'id', 'vth', 'gds']
    # Merge default variables with additional ones
    if additional_vars:
        variables = list(set(default_variables + additional_vars))
    else:
        variables = default_variables

    # Extract the required columns using the parse_columns function
    columns = df.columns
    parsed_columns = parse_columns(columns, variables)

    # Function to get column as array or NaN if column is missing
    def get_column_as_array(df, col_name):
        return df[col_name].values if col_name in df else np.nan

    # Helper function to format values with appropriate units
    def format_value(val):
        if np.isnan(val):
            return "NaN"
        abs_val = abs(val)
        if abs_val >= 1e12:
            return f"{val/1e12:.2f}T"
        elif abs_val >= 1e9:
            return f"{val/1e9:.2f}G"
        elif abs_val >= 1e6:
            return f"{val/1e6:.2f}M"
        elif abs_val >= 1e3:
            return f"{val/1e3:.2f}k"
        elif abs_val >= 1:
            return f"{val:.2f}"
        elif abs_val >= 1e-3:
            return f"{val*1e3:.2f}m"
        elif abs_val >= 1e-6:
            return f"{val*1e6:.2f}μ"
        elif abs_val >= 1e-9:
            return f"{val*1e9:.2f}n"
        elif abs_val >= 1e-12:
            return f"{val*1e12:.2f}p"
        elif abs_val >= 1e-15:
            return f"{val*1e15:.2f}f"
        else:
            return f"{val*1e18:.2f}a"

    # Get all transistor numbers
    all_transistors = set()
    for var_dict in parsed_columns.values():
        all_transistors.update(var_dict.keys())

    # Extract arrays for each transistor and each variable
    data = {var: {num: get_column_as_array(df, parsed_columns[var].get(num, None)) for num in all_transistors} for var in variables}

    # Calculate derived parameters gm/id, v_star, ro if they are part of the variables
    derived_params = {}
    if 'gm' in variables and 'id' in variables:
        derived_params['gm/id'] = {num: data['gm'][num] / data['id'][num] if not np.isnan(data['gm'][num]).all() and not np.isnan(data['id'][num]).all() else np.nan for num in all_transistors}
    if 'gm' in variables and 'id' in variables:
        derived_params['v_star'] = {num: 2 * data['id'][num] / data['gm'][num] if not np.isnan(data['gm'][num]).all() and not np.isnan(data['id'][num]).all() else np.nan for num in all_transistors}
    if 'gds' in variables:
        derived_params['ro'] = {num: 1 / data['gds'][num] if not np.isnan(data['gds'][num]).all() else np.nan for num in all_transistors}

    # Create a PrettyTable object
    table = PrettyTable()

    # Define headers
    table.field_names = ["Parameter"] + [f"{num}" for num in sorted(all_transistors)]

    # Add rows with formatted values
    for var in sorted(variables):
        table.add_row([var] + [format_value(data[var][num][0]) if not np.isnan(data[var][num]).all() else "NaN" for num in sorted(all_transistors)])

    # Add derived parameters to the table
    for param, values in derived_params.items():
        table.add_row([param] + [format_value(values[num][0]) if not np.isnan(values[num]).all() else "NaN" for num in sorted(all_transistors)])

    # Center align the columns
    table.align = "c"

    # Print the table
    print(table)

    # Create a DataFrame to store the table data
    table_data = {
        "Parameter": variables + list(derived_params.keys())
    }
    for num in sorted(all_transistors):
        table_data[num] = [format_value(data[var][num][0]) if not np.isnan(data[var][num]).all() else "NaN" for var in variables]
        table_data[num].extend([format_value(derived_params[param][num][0]) if not np.isnan(derived_params[param][num]).all() else "NaN" for param in derived_params])

    df_table = pd.DataFrame(table_data)

    def save_table_html(df_table, output_html):
        with open(output_html, 'w') as file:
            file.write(
                df_table.style.set_table_styles([
                    {'selector': 'thead th', 'props': [('background-color', '#aec6cf'), ('color', 'black'), ('text-align', 'center')]},
                    {'selector': 'tbody td', 'props': [('text-align', 'center'), ('padding', '10px'), ('border', '2px solid #ddd')]},
                    {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
                    {'selector': 'tbody tr:hover', 'props': [('background-color', '#ffcccc')]}
                ]).set_caption("Transistor Parameters")
                .set_table_attributes('class="dataframe minimalist-table"')
                .hide(axis='index')
                .to_html()
            )
        print(f"Table saved as {output_html}")

    # Save table as TXT
    def save_table_txt(table, output_txt):
        with open(output_txt, 'w') as file:
            file.write(str(table))
        print(f"Table saved as {output_txt}")

    save_table_txt(table, output_file)

    if html:
        save_table_html(df_table, 'output.html')
"""'''


def op_sim(df, output_file='output.txt', html=True, additional_vars=None, custom_expressions=None):
    """
    Automates the process of extracting required columns from the DataFrame, calculating gm/id and vstar,
    and displaying the results in a formatted table using PrettyTable.

    Parameters:
    ----------
    df : DataFrame
        The DataFrame containing the columns to be processed.
    output_file : str
        The name of the output file to save the table.
    html : bool
        Whether to save the table as an HTML file.
    additional_vars : list
        List of additional variables to include in the processing.
    custom_expressions : dict
        Dictionary of custom expressions to evaluate, with the key as the name of the expression and the value as the expression string.

    Returns:
    -------
    None
        Prints the PrettyTable containing the gm/id and Vstar and other DC OP Parameters values for each transistor.
    """
    # Define the column parsing function
    def parse_columns(columns, variables):
        parsed_columns = {var: {} for var in variables}

        pattern = re.compile(r'\[([^\]]+)\]')
        hierarchy_pattern = re.compile(r'(@m(?:\.\w+)+)\.(\w+)')  # Generalized pattern

        for col in columns:
            matches = pattern.findall(col)
            if matches:
                var_name = matches[0]
                if var_name in variables:
                    # Extract the full path and transistor number (e.g., @m.xm1.msky130_fd_pr__nfet_01v8)
                    hierarchy_match = hierarchy_pattern.search(col)
                    if hierarchy_match:
                        full_path = hierarchy_match.group(1)
                        parsed_columns[var_name][full_path] = col

        return parsed_columns

    # Default variables
    default_variables = ['vds', 'vdsat', 'gm', 'id', 'vth', 'gds']
    # Merge default variables with additional ones
    if additional_vars:
        variables = list(set(default_variables + additional_vars))
    else:
        variables = default_variables

    # Extract the required columns using the parse_columns function
    columns = df.columns
    parsed_columns = parse_columns(columns, variables)

    # Function to get column as array or NaN if column is missing
    def get_column_as_array(df, col_name):
        return df[col_name].values if col_name in df else np.nan

    # Helper function to format values with appropriate units
    def format_value(val):
        if np.isnan(val):
            return "NaN"
        abs_val = abs(val)
        if abs_val >= 1e12:
            return f"{val/1e12:.2f}T"
        elif abs_val >= 1e9:
            return f"{val/1e9:.2f}G"
        elif abs_val >= 1e6:
            return f"{val/1e6:.2f}M"
        elif abs_val >= 1e3:
            return f"{val/1e3:.2f}k"
        elif abs_val >= 1:
            return f"{val:.2f}"
        elif abs_val >= 1e-3:
            return f"{val*1e3:.2f}m"
        elif abs_val >= 1e-6:
            return f"{val*1e6:.2f}μ"
        elif abs_val >= 1e-9:
            return f"{val*1e9:.2f}n"
        elif abs_val >= 1e-12:
            return f"{val*1e12:.2f}p"
        elif abs_val >= 1e-15:
            return f"{val*1e15:.2f}f"
        else:
            return f"{val*1e18:.2f}a"

    # Get all transistor numbers
    all_transistors = sorted(set(num for var_dict in parsed_columns.values() for num in var_dict.keys()))

    # Extract arrays for each transistor and each variable
    data = {var: {num: get_column_as_array(df, parsed_columns[var].get(num, None)) for num in all_transistors} for var in variables}

    # Calculate derived parameters gm/id, v_star, ro if they are part of the variables
    derived_variables = ['gm/id','v_star','ro']
    derived_params = {}
    if 'gm' in variables and 'id' in variables:
        derived_params['gm/id'] = {num: data['gm'][num] / data['id'][num] if not np.isnan(data['gm'][num]).all() and not np.isnan(data['id'][num]).all() else np.nan for num in all_transistors}
    if 'gm' in variables and 'id' in variables:
        derived_params['v_star'] = {num: 2 * data['id'][num] / data['gm'][num] if not np.isnan(data['gm'][num]).all() and not np.isnan(data['id'][num]).all() else np.nan for num in all_transistors}
    if 'gds' in variables:
        derived_params['ro'] = {num: 1 / data['gds'][num] if not np.isnan(data['gds'][num]).all() else np.nan for num in all_transistors}
    
    variables.sort()
    # Evaluate custom expressions
    custom_results = {}
    if custom_expressions:
        for expr_name, expr in custom_expressions.items():
            custom_results[expr_name] = {}
            for num in all_transistors:
                local_vars = {var: data[var][num] for var in variables}
                derived_vars = {var: derived_params[var][num] for var in derived_variables}
                local_vars.update(derived_vars)
                try:
                    custom_results[expr_name][num] = eval(expr, {"__builtins__": None}, local_vars)
                except Exception as e:
                    custom_results[expr_name][num] = np.nan

    # Create a PrettyTable object
    table = PrettyTable()

    # Define headers
    table.field_names = ["Parameter"] + [f"{num}" for num in all_transistors]

    # Add rows with formatted values
    for var in variables:
        table.add_row([var] + [format_value(data[var][num][0]) if not np.isnan(data[var][num]).all() else "NaN" for num in all_transistors])

    # Add derived parameters to the table
    for param, values in derived_params.items():
        table.add_row([param] + [format_value(values[num][0]) if not np.isnan(values[num]).all() else "NaN" for num in all_transistors])

    # Add custom expressions to the table
    for expr_name, results in custom_results.items():
        table.add_row([expr_name] + [format_value(results[num][0]) if not np.isnan(results[num]).all() else "NaN" for num in all_transistors])

    # Center align the columns
    table.align = "c"

    # Print the table
    print(table)

    # Create a DataFrame to store the table data
    table_data = {
        "Parameter": variables + list(derived_params.keys()) + list(custom_results.keys())
    }
    for num in all_transistors:
        table_data[num] = [format_value(data[var][num][0]) if not np.isnan(data[var][num]).all() else "NaN" for var in variables]
        table_data[num].extend([format_value(derived_params[param][num][0]) if not np.isnan(derived_params[param][num]).all() else "NaN" for param in derived_params])
        table_data[num].extend([format_value(custom_results[expr_name][num][0]) if not np.isnan(custom_results[expr_name][num]).all() else "NaN" for expr_name in custom_results])

    df_table = pd.DataFrame(table_data)

    def save_table_html(df_table, output_html):
        with open(output_html, 'w') as file:
            file.write(
                df_table.style.set_table_styles([
                    {'selector': 'thead th', 'props': [('background-color', '#aec6cf'), ('color', 'black'), ('text-align', 'center')]},
                    {'selector': 'tbody td', 'props': [('text-align', 'center'), ('padding', '10px'), ('border', '2px solid #ddd')]},
                    {'selector': 'tbody tr:nth-child(even)', 'props': [('background-color', '#f9f9f9')]},
                    {'selector': 'tbody tr:hover', 'props': [('background-color', '#ffcccc')]}
                ]).set_caption("Transistor Parameters")
                .set_table_attributes('class="dataframe minimalist-table"')
                .hide(axis='index')
                .to_html()
            )
        print(f"Table saved as {output_html}")

    # Save table as TXT
    def save_table_txt(table, output_txt):
        with open(output_txt, 'w') as file:
            file.write(str(table))
        print(f"Table saved as {output_txt}")

    save_table_txt(table, output_file)

    if html:
        save_table_html(df_table, 'output.html')




def get_fet(columns):
    # Pattern to extract the transistor name with hierarchy
    hierarchy_pattern = re.compile(r'(@m(?:\.\w+)+\.\w+)')
    
    transistors = set()  # Use a set to avoid duplicates

    for col in columns:
        hierarchy_match = hierarchy_pattern.search(col)
        if hierarchy_match:
            transistors.add(hierarchy_match.group(1))
    
    return list(transistors)


def save_fet_vars(columns, variables, filename='save.spi'):
    try:
        transistors = get_fet(columns)
        with open(filename, 'w') as f:
            for transistor in transistors:
                for var in variables:
                    try:
                        if var.startswith('v'):
                            f.write(f"save v({transistor}[{var}])\n")
                        elif var.startswith('i'):
                            f.write(f"save i({transistor}[{var}])\n")
                        else:
                            f.write(f"save   {transistor}[{var}]\n")
                    except Exception as e:
                        print(f"Error writing variable {var} for transistor {transistor}: {e}")
                f.write("\n")
        print("Output file created successfully")
    except Exception as e:
        print(f"Error during save_fet_vars execution: {e}")