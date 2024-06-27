# Project Title: Circuit Simulation Analysis Tools

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
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/circuit-simulation-analysis-tools.git
   cd circuit-simulation-analysis-tools
   ```
2. Install the required packages:
   ```bash
   pip install numpy pandas prettytable
   ```

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
