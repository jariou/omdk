#!/bin/bash

#(Optional) load Virtualenv 
source ../pyth2/bin/activate

# Case 0: Append sequence numbers to each row
python PyTrans.py -d ../lxsl-testing/input/Generic_Windstorm_SourceLoc.xsd \
                  -c ../lxsl-testing/input/SourceLocPiWind.csv\
                  -t ../lxsl-testing/input/MappingMapToGeneric_Windstorm_CanLoc_A.xslt\
                  -o ../lxsl-testing/pyTrans_output/case0_py_withRows.cvs\
                  -l 5 

# Case 1: No Row numbers
python PyTrans.py -d ../lxsl-testing/input/Generic_Windstorm_SourceLoc.xsd \
                  -c ../lxsl-testing/input/SourceLocPiWind.csv\
                  -t ../lxsl-testing/input/MappingMapToGeneric_Windstorm_CanLoc_A.xslt\
                  -o ../lxsl-testing/pyTrans_output/case1_noRows.csv\
                  -l 5 \
                  -s
