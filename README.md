# CircuitCruncher: Circuit Simulation Analysis Tools

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Using Conda (Recommended)](#using-conda)
  - [Normal Install (Easy)](#normal-install-easy)
- [Usage](#usage)
  - [Operating Point Analysis](#operating-point-analysis)
  - [Saving SPICE Variables](#saving-spice-variables)
  - [AC Analysis Data Extraction](#ac-analysis-data-extractions)
- [Library Functions](#library-functions)
- [Contributing](#contributing)
- [License](#license)

## Overview
This repository contains Python scripts and modules to perform various analyses on circuit simulation data. The main functionalities include:
- **Operating Point Analysis**: Extracts and displays operating point parameters of transistors.
- **Saving SPICE Variables**: Generates a SPICE save file for specified variables.
- **Plotting Manager**: Abilty to plot easier with main functionalities for easy reuse

## Requirements
- Python 3.8+
- NumPy
- Pandas
- PrettyTable

## Installation
### Using Conda
<div class="alert alert-block alert-info">
<b>Tip:</b>
Conda envireoment is not a must, it just makes your life easier when you have too many projects depending on different versions of libraries.
</div>

1.  Make sure you have conda installed on your system by using this command
    ```bash
      conda info
    ``` 
  
2. If you don't have conda follow the following guide to install conda on Debian or Ubuntu

    [Anaconda Install on Debian and Ubuntu](https://docs.anaconda.com/anaconda/install/linux/)


3. Clone the repository

   ```bash
   git clone https://github.com/abdelrahmanali15/CircuitCruncher
   cd CircuitCruncher
   ```
4. Create conda enviroment from .yaml file 
 
   ```bash
   conda env create --file environment.yml
   ```
5. Install VSCode Extensions

    To work efficiently with Jupyter notebooks and data, install the following extensions in VSCode:

    - **Jupyter Notebook Extension**: This allows you to open and run Jupyter notebooks directly in VSCode.
    - **Data Wrangler Extension (optional)**: This extension helps with better variable reading and data manipulation.

6. Edit Jupyter Extension Setting to Show Scrollable Outputs
    Go to file > prefrences > settings. Search for `notebook.output.scrolling` in search bar and enable scrolling.

7. Open the notebook to view

8. To update go to repo directory and pull changes
```bash 
git checkout notebook_extratesting
git pull origin notebook_extratesting
```
9. Update dependencies
```bash
conda env update --file environment.yml
```


### Normal Install (Easy)
1. Clone the repo by
```bash
git clone https://github.com/abdelrahmanali15/CircuitCruncher
```
2. Go to CircuitCruncher folder
``` bash
cd CircuitCruncher
```

3. Install dependencies
```bash
  python3 -m pip install --user -r requirements.txt
  ```
3.  Run command in terminal inside the repo where `setup.py` is located
```bash
python3 -m pip install --user -e .
```
4. Install VSCode Extensions (assuming you are working on vscode)

    To work efficiently with Jupyter notebooks and data, install the following extensions in VSCode:

    - **Jupyter Notebook Extension**: This allows you to open and run Jupyter notebooks directly in VSCode.
    - **Data Wrangler Extension (optional)**: This extension helps with better variable reading and data manipulation.

5. Edit Jupyter Extension Setting to Show Scrollable Outputs
    Go to file > prefrences > settings. Search for `notebook.output.scrolling` in search bar and enable scrolling.

6.  Open the notebook to view

7. To update go to repo directory and pull changes
```bash 
git checkout notebook_extratesting
git pull origin notebook_extratesting
```
8. Update dependencies
```bash
python3 -m pip install --user -e 
```
## Usage
<div class="alert alert-block alert-info">
<b>Tip:</b> Check the<a href="post_analysis_notebook.ipynb">Jupyter Notebook</a> for latest documentation</div>

>

<div class="alert alert-block alert-info">
<b>Note:</b> You will find various post-analysis scripts in the <a href="Scripts">Scripts</a> folder. Copy what you will use to your simulation directory.
</div>





### Saving SPICE Variables
The script `save_spi.py` generates a SPICE save file for specified variables.
> **Note:** For this script to work correctly you need to add the option `.options savecurrents` before your control block in xschem or ngspice spice file.

```python
# save_spi.py

from lib import ng_raw_read, to_data_frames, save_fet_vars

if __name__ == '__main__':
    Op_simNumber = 0
    (arrs, plots) = ng_raw_read('/path/to/simulation.raw')
    
    if plots[Op_simNumber][b'plotname'] != b'Operating Point':
        raise Exception("This Data Frame doesn't include Operating Point Analysis")
    
    dfs = to_data_frames((arrs, plots))
    df = dfs[0]
    
    saveVars = ['vgs', 'vds', 'vdsat', 'gm', 'gmbs', 'id', 'vth', 'gds', 'cgs']
    save_fet_vars(df.columns, saveVars, '/path/to/save_test_analog.spi')
```

- Example Output _truncated_
![code](https://github.com/abdelrahmanali15/CircuitCruncher/assets/131778595/1bf1bf5e-6781-4bbd-90ae-04a31f57d380)


User then should include his file in the `contrl block` of xschem or ngspice
- Example
```
name=COMMANDS
simulator=ngspice
only_toplevel=false
value="
.param vdd=1.8
.param vcm=0.9
.options savecurrents

.control

    save all
    .include path/to/save/file/save.spi

    * operating point
    optran 0 0 0 100n 10u 0
    op

    write ota-5t_tb.raw
  
.endc
"
```

### Operating Point Analysis
The script `op_analysis.py` extracts and displays the operating point parameters of transistors from a raw simulation file.

```python
# op_analysis.py

from lib import ng_raw_read, to_data_frames, op_sim

if __name__ == '__main__':
    Op_simNumber = 0
    (arrs, plots) = ng_raw_read('/path/to/simulation.raw')
    
    if plots[Op_simNumber][b'plotname'] != b'Operating Point':
        raise Exception("This Data Frame doesn't include Operating Point Analysis")
    
    dfs = to_data_frames((arrs, plots))
    df = dfs[0]
    op_sim(df, html=True, additional_vars=['cgs', 'gmbs', 'vgs'], custom_expressions={"Avi": "gm*ro"})
```

- Example Output
  - `.txt` file
![image](https://github.com/abdelrahmanali15/CircuitCruncher/assets/131778595/7f4485bf-9ec9-41aa-8b76-0370a4b4027b)
  - `.html` file
![image](https://github.com/abdelrahmanali15/CircuitCruncher/assets/131778595/3a9b90c1-4330-41cd-8ef1-9dfa2fcea9f6)
   
### AC Analysis Data Extractions
The script `ac_analysis.py` performs AC analysis and calculates parameters like bandwidth, gain, and phase margin.

```python
# ac_analysis.py

from lib import ng_raw_read, to_data_frames, get_column_as_array, measure_ac_parameters, PlotManager

if __name__ == '__main__':
    AC_simNumber = 0 # assuming that it is the first analysis if you run it after op in the same simulation the change 0 to 1
    (arrs, plots) = ng_raw_read(ac_raw_path)

    if plots[AC_simNumber][b'plotname'] != b'AC Analysis':
        raise Exception("This Data Frame doesn't include AC Analysis")

    dfs = to_data_frames((arrs, plots))
    df = dfs[0]

    # view_headers(df)

    ac_parameters = ac_analysis(df,save=True,output_file=output_dir+'ac_out')

    plt.show()
```

## Library Functions
The `lib` folder contains utility functions for data processing and analysis.

### `data_processing.py`

#### `lookup`

```python
lookup(lookup_array: np.ndarray, lookup_value: float, lookup_return_array: np.ndarray) -> float
```

Performs linear interpolation to find the corresponding value in `lookup_return_array` for a given `lookup_value`.

- **Parameters:**
  - `lookup_array` (np.ndarray): Array of x-values.
  - `lookup_value` (float): The x-value to look up.
  - `lookup_return_array` (np.ndarray): Array of y-values.

- **Returns:**
  - `float`: Interpolated y-value.

#### `op_sim`

```python
op_sim(df: pd.DataFrame, output_file='output.txt', html=True, additional_vars=None, custom_expressions=None)
```

Extracts headers from the DataFrame, calculates `gm/id`, `vstar` and `ro`, and displays results in a formatted table in the terminal and `.txt` file it has the ability to save `.html` file.
It has the ability to calculate simple custom expressions made of saved variables.
It also has the ability to input a list of variables not included in default printed variables which are 
```python
default_variables = ['vds', 'vdsat', 'gm', 'id', 'vth', 'gds', 'gm/id', 'vstar', 'ro']
```

- **Parameters:**
  - `df` (pd.DataFrame): DataFrame with columns to process.
  - `output_file` (str): Name of the output file.
  - `html` (bool): Save table as HTML if True.
  - `additional_vars` (list): Additional variables to include.
  - `custom_expressions` (dict): Custom expressions to evaluate.

#### `get_fet`

```python
get_fet(columns: list) -> list
```

Extracts transistor names with hierarchy from list of variable names (headers of Data frame).

- **Parameters:**
  - `columns` (list): List of column names.

- **Returns:**
  - `list`: List of transistor names.

#### `save_fet_vars`

```python
save_fet_vars(columns: list, variables: list, filename='save.spi')
```

Generates a SPICE save file contains command to save all user specified variables of transistors.
Include this file into `control block` in xschem or ngspice by `.include /path/to/file/save.spi`

- **Parameters:**
  - `columns` (list): List of column names.
  - `variables` (list): List of variables to save.
  - `filename` (str): Name of the file to save.

- **Returns:**
  - `None`

---

### `file_readers.py`
#### `ng_raw_read`

```python
ng_raw_read(fname: str) -> tuple[list[np.ndarray], list[dict]]
```

Reads a binary file of Raw saved simulation data and returns a list of numpy arrays and a list of metadata dictionaries.
metadata dictionaries contain the following keys
```python
 MDATA_LIST = [b'title', b'date', b'plotname', b'flags', b'no. variables',
              b'no. points', b'dimensions', b'command', b'option']
```
you can use those keys after parsing Raw file to access them ot you can just use linux terminal command ` <more your_raw_file.raw>` in the simulation directory.

- **Parameters:**
  - `fname` (str): Path to the binary file.

- **Returns:**
  - tuple: List of `np.ndarray` and list of metadata dictionaries.

#### `to_data_frames`

```python
to_data_frames(ngarr: tuple[list[np.ndarray], list[dict]]) -> list[pd.DataFrame]
```

Converts the output of `ng_raw_read` to a list of pandas DataFrames.

- **Parameters:**
  - `ngarr` (tuple): Tuple from `ng_raw_read`.

- **Returns:**
  - list: List of `pd.DataFrame`.


#### `get_column_as_array`

```python
get_column_as_array(df: pd.DataFrame, column_name: str) -> np.ndarray
```

Extracts a column from a DataFrame as a numpy array. Each array represent the data of the input variable name as written in raw file.

- **Parameters:**
  - `df` (`pd.DataFrame`): DataFrame.
  - `column_name` (str): Column name.

- **Returns:**
  - `np.ndarray`: Column as array.

#### `view_headers`

```python
view_headers(df: pd.DataFrame)
```

Prints the column headers of a DataFrame to see the saved variable names.

- **Parameters:**
  - `df` (`pd.DataFrame`): DataFrame.

---


## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License
This project is licensed under the Apache License. See the [LICENSE](LICENSE) file for details.

---
