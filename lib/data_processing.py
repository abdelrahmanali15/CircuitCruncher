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
