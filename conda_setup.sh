#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

INSTALL_PATH="/usr/local/bin"
CONDA_PREFIX="$HOME/micromamba-env"

# Step 1: Download and extract Micromamba
echo "Downloading Micromamba..."
MICROMAMBA_URL=$(curl -s https://api.github.com/repos/mamba-org/micromamba-releases/releases/latest | grep browser_download_url | grep linux-64 | cut -d '"' -f 4)
sudo curl -Ls "$MICROMAMBA_URL" | sudo tar -xvj -C "$INSTALL_PATH" bin/micromamba

if [ ! -f "$INSTALL_PATH/micromamba" ]; then
    echo "Error: Micromamba binary not found at $INSTALL_PATH/micromamba"
    exit 1
fi

sudo chmod +x "$INSTALL_PATH/micromamba"

echo "Micromamba installed at $INSTALL_PATH/micromamba"

# Step 2: Create the conda environment using Micromamba and environment.yaml
echo "Creating Conda environment..."
"$INSTALL_PATH/micromamba" create --yes --prefix "$CONDA_PREFIX" --file environment.yml

# Step 3: Activate the environment
export PATH="$CONDA_PREFIX/bin:$PATH"
export CONDA_DEFAULT_ENV="$CONDA_PREFIX"

# Step 4: Install additional Python packages if needed
echo "Installing additional Python packages..."
"$CONDA_PREFIX/bin/pip" install gdstk

echo "Setup complete. To activate the environment in the future, run:"
echo "export PATH=\"$CONDA_PREFIX/bin:\$PATH\""
echo "export CONDA_DEFAULT_ENV=\"$CONDA_PREFIX\""
