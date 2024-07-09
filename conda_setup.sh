#!/bin/bash

INSTALL_PATH="/usr/local/bin"
CONDA_PREFIX="$HOME/micromamba-env"

# Step 1: Download and extract Micromamba
echo "Downloading Micromamba..."
sudo curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | sudo tar -xj -C "$INSTALL_PATH" bin/micromamba
sudo chmod +x "$INSTALL_PATH/micromamba"

# Step 2: Create the conda environment using Micromamba and environment.yaml
echo "Creating Conda environment..."
"$INSTALL_PATH/micromamba" create --yes --prefix "$CONDA_PREFIX" --file environment.yml

# Step 3: Activate the environment
eval "$("$INSTALL_PATH/micromamba" shell hook --shell bash)"
micromamba activate "$CONDA_PREFIX"

# Step 4: Install additional Python packages if needed
echo "Installing additional Python packages..."
pip install gdstk

echo "Setup complete. To activate the environment in the future, run:"
echo "eval \"\$($INSTALL_PATH/micromamba shell hook --shell bash)\""
echo "micromamba activate \"$CONDA_PREFIX\""
