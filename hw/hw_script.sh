#!/bin/bash
############## hw_side ################
RED="\e[31m"
ORANGE="\e[33m"
ENDCOLOR="\e[0m"

# Check Vivado command
if ! command -v vivado &> /dev/null
then
    echo -e "${RED}[ERROR]${ENDCOLOR} Vivado binaries not found. Please make sure you have sourced them in the current terminal."
    exit
fi

# Check Vivado version
output=$(/usr/bin/which vivado)
if ! [[ "$output" == *"2020.2"* ]]; then 
    echo -e "${ORANGE}[WARNING]${ENDCOLOR} This version is created using Vivado 2020.2. You do not have the same version. Continue at your own risk."
    exit
fi

# Get project name and path
output=$(pwd)
fire="/afs/bb/u/zoualami/omi/default_fire/modified/astra_5cd07be_333"
xdc="$output/peta_fire_constraints.xdc"
echo "Please enter the new project's name: "
read project_name
echo "Please enter the new project's path (without project's name) [current directory: $output/, leave blank to keep it] : "
read project_path
echo "Please enter the fire's project path [default directory: $fire, leave blank to keep it] : "
read fire_path
echo "Please enter the XDC's file path [default directory: $xdc, leave blank to keep it] : "
read xdc_path

if [ -z "$project_path"]; then project_path="$output/"; fi
if ! [[ "$project_path" == *"/" ]]; then project_path="$project_path/"; fi
if [ -z "$fire_path"]; then fire_path="$fire/"; fi
if [ -z "$xdc_path"]; then xdc_path="$xdc"; fi


# launch the hardware generation script
vivado -mode batch -source tcl_code.tcl -tclargs "$project_name" "$project_path" "$fire_path" "$xdc_path"