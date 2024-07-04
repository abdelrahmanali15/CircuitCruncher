from __future__ import division
import numpy as np
import pandas as pd
import yaml

BSIZE_SP = 512
MDATA_LIST = [b'title', b'date', b'plotname', b'flags', b'no. variables',
              b'no. points', b'dimensions', b'command', b'option']

def ng_raw_read(fname: str) -> 'tuple[list[np.ndarray], list[dict]]':
    with open(fname, 'rb') as fp:
        arrs = []
        plots = []
        names = {}
        plot = {}
        index_suffix = 0

        def read_metadata_line():
            try:
                return fp.readline(BSIZE_SP).split(b':', maxsplit=1)
            except Exception as e:
                raise IOError(f"Error reading file: {e}")

        while True:
            metadata = read_metadata_line()
            if len(metadata) != 2:
                break

            key, value = metadata[0].lower(), metadata[1].strip()
            plot[key] = value

            if key == b'variables':
                if b'no. variables' not in plot or b'no. points' not in plot:
                    raise KeyError("Missing 'no. variables' or 'no. points' in metadata before 'variables' key.")

                num_vars = int(plot[b'no. variables'])
                num_points = int(plot[b'no. points'])
                plot['varnames'] = []
                plot['varunits'] = []

                for var_index in range(num_vars):
                    var_spec = fp.readline(BSIZE_SP).strip().decode('ascii').split()
                    assert var_index == int(var_spec[0])

                    var_name = var_spec[1]
                    if var_name in names:
                        var_name += str(index_suffix)
                        index_suffix += 1
                    names[var_name] = 1

                    plot['varnames'].append(var_name)
                    plot['varunits'].append(var_spec[2])

            if key == b'binary':
                if b'flags' not in plot:
                    raise KeyError("Missing 'flags' in metadata before 'binary' key.")

                dtype_formats = [np.complex_ if b'complex' in plot[b'flags'] else np.float_] * num_vars
                row_dtype = np.dtype({'names': plot['varnames'], 'formats': dtype_formats})
                arrs.append(np.fromfile(fp, dtype=row_dtype, count=num_points))
                plots.append(plot.copy())
                fp.readline()  # Skip the end-of-line character after the binary data

    return arrs, plots


def to_data_frames(ngarr: 'tuple[list[np.ndarray], list[dict]]') -> 'list[pd.DataFrame]':
    arrs, plots = ngarr
    return [pd.DataFrame(data=arr, columns=plot['varnames']) for arr, plot in zip(arrs, plots)]

def to_data_frame(fraw: str) -> pd.DataFrame:
    arrs, plots = ng_raw_read(fraw)
    if arrs:
        return pd.DataFrame(data=arrs[0], columns=plots[0]['varnames'])
    return None

def get_column_as_array(df: pd.DataFrame, column_name: str) -> np.ndarray:
    if column_name not in df.columns:
        raise KeyError(f"Could not find name '{column_name}' in columns: {', '.join(df.columns)}")
    return df[column_name].values


def view_headers(df: pd.DataFrame):
    print(df.columns)


def loadYaml(config_name = 'config.yaml'):    
    with open(config_name, 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


def loadConfig():
    config = loadYaml()
    # Accessing configuration values
    ngspice_options = config["ngspice"]["options"]
    sim_output_dir = config["sim"]["dir"]
    op_raw_file = config["sim"]["op_raw"]
    ac_raw_file = config["sim"]["ac_raw"]
    output_dir = config["output"]["dir"]

    op_raw_path = sim_output_dir + '/' + op_raw_file
    ac_raw_path = sim_output_dir + '/' + ac_raw_file


    return {"ngOptions": ngspice_options, 
            "op_RawPath":op_raw_path,
            "ac_RawPath" : ac_raw_path,
            "out_dir": output_dir  }  


def simType(name,plots): 
    def simAlias():
        if name == 'ac':
            return b'AC Analysis'
        elif name == 'op':
            return b'Operating Point'
        elif name == 'dc':
            return b'DC transfer characteristic'
        elif name == 'stb':
            return b'AC Analysis'
        else:
            pass

    idx = 0
    for plot in plots: 
        if plot[b'plotname'] == simAlias():
            return idx 
        else:
            idx = idx + 1
    
    raise NotImplementedError(f"Unsupported plot name {name}")