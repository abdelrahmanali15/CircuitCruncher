#!/bin/bash

# Step 1: Download and extract Micromamba
echo "Downloading Micromamba..."
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xj bin/micromamba

# Step 2: Set up environment variables and paths
export PATH="$PWD/bin:$PATH"
export CONDA_PREFIX="$PWD/conda-env"

# Step 3: Create the conda environment using Micromamba and environment.yaml
echo "Creating Conda environment..."
./bin/micromamba create --yes --prefix $CONDA_PREFIX --file environment.yml

# Step 4: Install additional Python packages if needed
echo "Installing additional Python packages..."
"$CONDA_PREFIX/bin/python" -m pip install gdstk

echo "Setup complete. To activate the environment, run:"
echo "export CONDA_PREFIX=\"$CONDA_PREFIX\""
echo "export PATH=\"$CONDA_PREFIX/bin:\$PATH\""

