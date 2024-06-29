# CircuitCruncher: Circuit Simulation Analysis Tools

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Operating Point Analysis](#operating-point-analysis)
  - [Saving SPICE Variables](#saving-spice-variables)
  - [AC Analysis](#ac-analysis)
- [Library Functions](#library-functions)
- [Contributing](#contributing)
- [License](#license)

## Overview
This repository contains Python scripts and modules to perform various analyses on circuit simulation data. The main functionalities include:
- **Operating Point Analysis**: Extracts and displays operating point parameters of transistors.
- **Saving SPICE Variables**: Generates a SPICE save file for specified variables.
- **AC Analysis**: Performs AC post analysis and calculates important parameters like bandwidth, gain, and phase margin.
- **Plotting Manager**: Abilty to plot easier with main functionalities for easy reuse

## Requirements
- Python 3.6+
- NumPy
- Pandas
- PrettyTable

## Installation

<div class="alert alert-block alert-info">
<b>Tip:</b>
Conda envireoment is not a must, you can create any envireoment that have all needed packages.
</div>

 ### Make sure you have conda installed on your system by using this command 
   ```bash
   conda info
   ```
### Installing Miniconda on Linux

Miniconda is a minimal installer for conda, a package manager widely used in data science for managing environments and dependencies. Follow the steps below to install Miniconda on a Linux system.

#### Step 1: Download the Miniconda Installer

1. Open your terminal.
2. Download the latest Miniconda installer script. You can find the URL for the latest version on the [Miniconda official website](https://docs.conda.io/en/latest/miniconda.html). Use `wget` or `curl` to download the script. For example:

    ```sh
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    ```

    Alternatively, using `curl`:

    ```sh
    curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    ```

#### Step 2: Verify the Installer

(Optional but recommended) Verify the integrity of the downloaded script using SHA-256 checksum:

1. Download the checksum file from the same location:

    ```sh
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh.sha256
    ```

2. Check the SHA-256 checksum:

    ```sh
    sha256sum -c Miniconda3-latest-Linux-x86_64.sh.sha256
    ```

    Ensure that the output states the file is OK.

#### Step 3: Run the Installer

1. Make the downloaded script executable:

    ```sh
    chmod +x Miniconda3-latest-Linux-x86_64.sh
    ```

2. Run the installer script:

    ```sh
    ./Miniconda3-latest-Linux-x86_64.sh
    ```

3. Follow the prompts in the installer. You can generally accept the default settings. The prompts will include:
   - Reviewing and accepting the license agreement.
   - Choosing the installation location (the default is usually fine).

#### Step 4: Initialize Miniconda

1. After the installation is complete, you need to initialize Miniconda. This sets up your shell to use `conda`:

    ```sh
    conda init
    ```

2. Close and reopen your terminal or run:

    ```sh
    source ~/.bashrc
    ```

### Step 5: Verify the Installation

To confirm that Miniconda is installed correctly, run:

```sh
conda --version
```

You should see the conda version number, indicating that the installation was successful.

#### Additional Tips

- **Updating Conda**: It is a good practice to keep conda updated. You can update conda using:

    ```sh
    conda update conda
    ```

- **Creating Environments**: Create isolated environments with specific Python versions or packages using:

    ```sh
    conda create --name myenv python=3.8
    ```

- **Activating Environments**: Activate your newly created environment using:

    ```sh
    conda activate myenv
    ```

- **Deactivating Environments**: Deactivate the current environment using:

    ```sh
    conda deactivate
    ```

By following these steps, you should have Miniconda installed and running on your Linux system, providing you with a robust environment management tool for your projects.


1. Clone the repository:
   ```bash
   git clone https://github.com/abdelrahmanali15/CircuitCruncher/tree/try_notebook
   cd cd CircuitCruncher
   ```
   
2. Create conda enviroment from .yaml file 
   ```bash
   conda env create --file environment.yml
   ```
3. Install jupyter notebook extension on vscode
4. Open the notebook to view


## Usage
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

### Saving SPICE Variables
The script `save_spi.py` generates a SPICE save file for specified variables.

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

### AC Analysis  _(unfinished)_
The script `ac_analysis.py` performs AC analysis and calculates parameters like bandwidth, gain, and phase margin.

```python
# ac_analysis.py

from lib import ng_raw_read, to_data_frames, get_column_as_array, measure_ac_parameters, PlotManager

if __name__ == '__main__':
    dfs = to_data_frames(ng_raw_read('/path/to/ac_analysis.raw'))
    df = dfs[0]
    
    freq = get_column_as_array(df, 'frequency')
    vout_mag = get_column_as_array(df, 'v(vout)')
    ac_parameters = measure_ac_parameters(freq, vout_mag)

    vout_db = ac_parameters["vout_db"]
    vout_phase_margin = ac_parameters["vout_phase_margin"]
    A0_db = ac_parameters["A0_db"]
    BW_3dB = ac_parameters["BW_3dB"]
    
    print(f'BW = {BW_3dB:.2e}')
    print(f'A0_db = {A0_db:.2f}')

    pm = PlotManager(num_subplots=2, title='AC Analysis', xlabel='Frequency', ylabel='')
    pm.plot(freq, vout_db, label='Gain dB', subplot_index=0)
    pm.plot(freq, vout_phase_margin, label='Phase', subplot_index=1)
    pm.add_line(line_orientation='vertical', line_value=BW_3dB, line_label='BW 3dB', line_color='red')
    pm.show()
```

## Library Functions
The `lib` folder contains utility functions for data processing and analysis.

### `data_processing.py`
- `lookup(lookup_array, lookup_value, lookup_return_array)`: Linear interpolation function.
- `measure_ac_parameters(frequencies, vout)`: Calculates AC parameters. _(unfinished)_
- `calculate_propagation_delay(time, vout, threshold_ratio=0.5)`: Calculates propagation delay. _(unfinished)_
- `calculate_cmrr(time, vout, vin, Vvdd, Vcm_min, Vcm_max)`: Calculates Common-Mode Rejection Ratio (CMRR). _(unfinished)_
- `op_sim(df, output_file='output.txt', html=True, additional_vars=None, custom_expressions=None)`: Extracts and displays operating point parameters.
- `get_fet(columns)`: Extracts transistor names from columns.
- `save_fet_vars(columns, variables, filename='save.spi')`: Generates a SPICE save file.

### `file_readers.py`
- `ng_raw_read(fname)`: Reads raw simulation data.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
