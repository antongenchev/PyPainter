#!/bin/bash

###############################################
# Build Script for ImageProcessingTools       #
###############################################
# This script automates the build process     #
# for ImageProcessingTools, allowing you      #
# to clean previous builds, generate a        #
# `setup.py` file (if it doesn't exist),      #
# and compile Python Cython extensions.       #
#                                             #
# Arguments:                                  #
#   $1 - Tool name (e.g., "ShapeTool")        #
#   $2 - Optional flags:                      #
#       --clean         : Clean previous      #
#                         build artifacts     #
#       --generate-setup: Generate a basic    #
#                         setup.py file if    #
#                         it doesn't exist.   #
#                                             #
########################################################################
# Example usage:                                                       #
#   ./src/ImageProcessingTools/build_tool.sh ToolName --clean          #
#   ./src/ImageProcessingTools/build_tool.sh ToolName --generate-setup #
########################################################################

TOOL_NAME="$1"

# FLAGS
CLEAN=0 # Clean build (delete build folders)
GENERATE_SETUP=0 # Generate setup.py (only if setup.py does not exist)

# Check for flags in any order
for arg in "$@"; do
    case $arg in
        --clean)
            CLEAN=1
            ;;
        --generate-setup)
            GENERATE_SETUP=1
            ;;
        *)
            ;;
    esac
done

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "\e[31m[Error] Virtual environment 'venv' does not exist. Please create one first.\e[0m"
    exit 1
fi
source venv/bin/activate

# Define the tool directory and setup file
tool_dir="src/ImageProcessingTools/$TOOL_NAME/"
setup_file="$tool_dir/setup.py"
if [ ! -f "$setup_file" ]; then
    if [ $GENERATE_SETUP -eq 1 ]; then
        echo "[Info] Generating setup.py file for $TOOL_NAME"
        cat > "$setup_file" <<EOL
from setuptools import setup
from Cython.Build import cythonize

setup(
    name="$TOOL_NAME",
    ext_modules=cythonize("$TOOL_NAME.py")
)
EOL
        echo -e "\e[32m[Success] setup.py file generated for $TOOL_NAME.\e[0m"
    else
        echo -e "\e[31m[Error] File '$setup_file' does not exist!\e[0m"
        exit 1
    fi
fi

cd $tool_dir

# Clean previous builds if the flag is set
if [ $CLEAN -eq 1 ]; then
    echo "[Info] Cleaning up previous builds..."
    rm -rf build/
fi

# Run the build process
echo "[Info] Building $TOOL_NAME..."
python setup.py build_ext --inplace

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo -e "\e[31m[Error] Build failed!\e[0m"
    exit 1
fi

echo "[Info] Build completed successfully."



##############################
# Check package dependencies #
##############################
# Warnings will be generated if there are missing dependencies.
# Even if the build is successful the shared object module might
# rely on dependencies which are not installed (e.g. numpy, etc.).
# These distrbution packages must be installed manually before the
# project can be started using main.py or build into an executable.

# Get the required python packages
dependencies=$(python -c "import yaml; 
with open('configuration.yaml', 'r') as f: 
    config = yaml.safe_load(f); 
    print(config.get('dependency', {}).get('packages', []))")
dependencies_list=$(echo "$dependencies" | tr -d "[],'\""| tr '\n' ' ')

# Get the list of installed packages
installed_packages=$(pip freeze)

warn_flag=0
missing_dependencies=()
for dep in $dependencies_list; do
    dep_name=$(echo $dep | sed 's/[<>=!].*//')
    installed_version=$(echo "$installed_packages" | grep -oP "\b$dep_name==\K[^\s]+")

    # If the package is not installed at all, mark as missing
    if [ -z "$installed_version" ]; then
        missing_dependencies+=("$dep")
        warn_flag=1
        continue
    fi

    # Handle version specifiers (e.g., ==, > etc.)
    if [[ "$dep" =~ == ]]; then
        required_version=$(echo $dep | sed 's/.*==//')
        if [ "$installed_version" != "$required_version" ]; then
            echo -e "\e[33m[Warning] Version mismatch for $dep_name: required $required_version, but installed $installed_version.\e[0m"
            warn_flag=1
        fi
    elif [[ "$dep" =~ ">=" ]]; then
        required_version=$(echo $dep | sed 's/.*>=//')
        if [[ "$(python -c 'from packaging import version; print(version.parse("'$installed_version'") >= version.parse("'$required_version'"))')" != "True" ]]; then
            echo -e "\e[33m[Warning] Installed version $installed_version of $dep_name is lower than required $required_version.\e[0m"
            warn_flag=1
        fi
    elif [[ "$dep" =~ "<=" ]]; then
        required_version=$(echo $dep | sed 's/.*<=//')
        if [[ "$(python -c 'from packaging import version; print(version.parse("'$installed_version'") <= version.parse("'$required_version'"))')" != "True" ]]; then
            echo -e "\e[33m[Warning] Installed version $installed_version of $dep_name is higher than required $required_version.\e[0m"
            warn_flag=1
        fi
    elif [[ "$dep" =~ ">" ]]; then
        required_version=$(echo $dep | sed 's/.*>//')
        if [[ "$(python -c 'from packaging import version; print(version.parse("'$installed_version'") > version.parse("'$required_version'"))')" != "True" ]]; then
            cho -e "\e[33m[Warning] Installed version $installed_version of $dep_name is not greater than required $required_version.\e[0m"
            warn_flag=1
        fi
    elif [[ "$dep" =~ "<" ]]; then
        required_version=$(echo $dep | sed 's/.*<//')
        if [[ "$(python -c 'from packaging import version; print(version.parse("'$installed_version'") < version.parse("'$required_version'"))')" != "True" ]]; then
            cho -e "\e[33m[Warning] Installed version $installed_version of $dep_name is not lower than required $required_version.\e[0m"
            warn_flag=1
        fi
    elif [[ "$dep" =~ "!=" ]]; then
        required_version=$(echo $dep | sed 's/.*!=//')
        if [ "$installed_version" == "$required_version" ]; then
            echo -e "\e[33m[Warning] Installed version $installed_version of $dep_name is equal to forbidden version $required_version.\e[0m"
            warn_flag=1
        fi
    fi
done

if [ ${#missing_dependencies[@]} -gt 0 ]; then
    echo -e "\e[33m[Warning] The following dependencies are required but missing in the virtual environment:\e[0m"
    for dep in "${missing_dependencies[@]}"; do
        echo -e "\e[33m - $dep\e[0m"
    done
fi

if [ $warn_flag -eq 1 ]; then
    echo -e "\e[33m[Warning] There were warnings during the dependency check. Please review the messages above.\n   Advice: Use pip to resolve them.\e[0m"
else
    echo -e "\e[32m[INFO] All python package dependencies are correctly installed and up-to-date!\e[0m"
fi

