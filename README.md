# omi_enablement
An example of OMI setup on a FMC+ development board

# Directory Structure
* C contains a C sources of main testing routines
    ```
    Compilation : gcc *.c -o omirpi.out
    Usage      : ./omirpi.out info -c fire -b 3
    ```
* hw contains the scripts used to generates the FPGA binary for FMC+ board
* petalinux contains the petalinux configurations files
* python contains the python sources of main testing routines

Check further information at: https://OpenCAPI.github.io/omi-doc/blocs/enablement/
