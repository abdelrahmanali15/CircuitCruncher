# Environment Setup Script

This repository contains a script to set up a conda environment using micromamba and install necessary packages.

## Prerequisites

- Bash shell
- curl
- tar

## Running the Installation Script (1st Method)

1. Set Up Environment Variables

You can set up environment variables in your `.bashrc` or system-wide configuration files to ensure Micromamba and your Conda environments are recognized globally.

Edit the `/etc/profile` file (requires sudo):

```bash
sudo nano /etc/profile
```

Add the following lines to the end of the file:

```bash
# Set up Micromamba and Conda environment variables
export PATH="/usr/local/bin/micromamba:$PATH"
```

Save the file and exit the text editor.

2. Apply Changes

To apply the changes system-wide without restarting, you can source the `/etc/profile` file:

```bash
source /etc/profile
```

3. Clone this repository (skip if already done):
   ```
   git clone https://github.com/abdelrahmanali15/CircuitCruncher
   cd CircuitCruncher
   ```

2. Make sure you have an `environment.yaml` file in the same directory as the setup script. This file should contain all the conda packages you want to install.

3. Make the script executable:
   ```
   chmod +x conda_setup.sh
   ```

4. Run the setup script:
   ```
   ./conda_setup.sh
   ```
5. Verify Installation

After completing these steps, you should be able to run Micromamba and its commands from any terminal session:

```bash
micromamba --version
```

5. After the script finishes, activate the environment by running the commands printed at the end of the script execution they will be something like this:
   ```
   export CONDA_PREFIX="/path/to/conda-env"
   export PATH="/path/to/conda-env/bin:$PATH"
   ```

6. Everytime you should use the same commands to activate enviroment or go to instilaion directory of the repo and run 
    ```bash
    source ./conda-env/bin/activate
    ```


## Install Command by Command (2nd Method)

1. **Download Micromamba:**
   - Open a terminal or command prompt.
   - Navigate to your project directory.
   - Run the following command to download and extract Micromamba:
     ```bash
     curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba
     ```

2. **Set Up Conda Environment:**
   - Ensure Python 3.7 or later is installed on your system.
   - In your terminal, navigate to the directory containing your `environment.yaml` file.
   - Run the following commands:
     ```bash
     # Set up environment variables and paths
     export PATH="$PWD/bin:$PATH"
     export CONDA_PREFIX="$PWD/conda-env"
     
     # Create the conda environment using Micromamba and the environment.yaml file
     ./bin/micromamba create --yes --prefix $CONDA_PREFIX --file environment.yml
     ```

3. **Install Additional Python Packages:**
   - You can install any other libraries you want not included in  `environment.yml`, install them using pip:
     ```bash
     ./conda-env/bin/python -m pip install gdstk
     ```

4. **Activate the Environment:**
   - Activate the newly created environment to use your library and its dependencies:
     ```bash
     source ./conda-env/bin/activate
     ```

5. **Run Your Application or Script:**
   - Now you can run your Python scripts.


## What the Script Does

1. Downloads and extracts micromamba.
2. Sets up a conda environment path.
3. Creates a new conda environment using the provided `environment.yaml` file.
4. Installs additional packages via pip (in this case, `gdstk`).
5. Sets up necessary environment variables.



## Troubleshooting

If you encounter any issues:
- Make sure you have write permissions in the directory where you're running the script.
- Check that your `environment.yaml` file is correctly formatted and contains valid package names.
- Ensure you have a stable internet connection for downloading packages.
- **Environment Activation:** Remember to activate the environment (`source ./conda-env/bin/activate`) whenever you want to use your library or run scripts that require the installed packages.
- **Customization:** Modify `environment.yaml` to include any additional packages or specific versions required by your library.
- **Permissions:** Ensure you have appropriate permissions to execute scripts and install packages in your chosen directory.


For more information on micromamba, visit [https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html)

To make Micromamba accessible system-wide and set it up so that you can run it from anywhere in your terminal, you can follow these steps:

### 1. Install Micromamba

Download and install Micromamba into a system-wide directory, such as `/usr/local/bin`, which is typically already included in the `PATH` for all users.

```bash
# Example installation path (adjust as needed)
INSTALL_PATH="/usr/local/bin"

# Download and extract Micromamba
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj -C "$INSTALL_PATH" bin/micromamba

# Add execute permissions
chmod +x "$INSTALL_PATH/bin/micromamba"
```


This setup ensures that Micromamba is accessible system-wide and recognized as a command without needing to specify its full path. Adjust the installation path (`/usr/local/bin` in this example) as necessary based on your system configuration and preferences.


