#!/bin/bash

EXEC_ROOT='/home/sam/oasis_work/PiWind/'
FILE_ROOT=$(pwd)/


# -- xTrans ----------------------------------------------------------- #
  
    exit_err(){
        exit 1
    }
    run_xtrans(){
        echo '-- test '$1' --------------------------'
        echo "xtrans:     "$EXEC_PATH
        echo "input:      "$FILE_INPUT
        echo "output:     "$FILE_OUTPUT
        echo "validation: "$FILE_VALIDATION
        echo "transform:  "$FILE_TRANSFORM
        printf '\n'

        CMD=$EXEC_PATH' '$2' -d '$FILE_VALIDATION' -c '$FILE_INPUT' -t '$FILE_TRANSFORM' -o '$FILE_OUTPUT

        mono --debug $CMD
        #echo $CMD
        #cat $FILE_OUTPUT
    }

    # Check mono is installed 
    command -v mcs >/dev/null 2>&1 || exit_err "Missing dependency, install 'Mono' on your system first: \nhttp://www.mono-project.com/docs/getting-started/install/\n" 
    #assuming exec from dir  <repo root>/tests/exposure/generate_xtrans_output.sh   
    # (can improve later)
    ../../xtrans/make-xtrans 
    if [ $? -ne 0 ]; then
        printf "error when compiling xtrans\n" && exit 1
    fi    
    EXEC_PATH='../../xtrans/xtrans.exe'


# -- PiWind Model ----------------------------------------------------------- #
    CASE=0
    FILE_INPUT=$FILE_ROOT'data/piWind/input/SourceLocPiWind.csv'
    FILE_OUTPUT=$FILE_ROOT'output/xtrans/'$CASE'_case_xtrans.csv'
    FILE_VALIDATION=$FILE_ROOT'data/piWind/validation/Generic_Windstorm_SourceLoc.xsd'
    FILE_TRANSFORM=$FILE_ROOT'data/piWind/transformation/MappingMapToGeneric_Windstorm_CanLoc_A.xslt'
    run_xtrans $CASE -s

    CASE=1
    FILE_INPUT=$FILE_OUTPUT
    FILE_OUTPUT=$FILE_ROOT'output/xtrans/'$CASE'_case_xtrans.csv'
    FILE_VALIDATION=$FILE_ROOT'/data/piWind/validation/Generic_Windstorm_CanLoc_B.xsd'
    FILE_TRANSFORM=$FILE_ROOT'/data/piWind/transformation/MappingMapTopiwind_modelloc.xslt'
    run_xtrans $CASE



# -- ARA Model -------------------------------------------------------------- #

    CASE=2
    FILE_INPUT=$FILE_ROOT'data/ARA/input/NationwideDF_loc.csv'
    FILE_OUTPUT=$FILE_ROOT'output/xtrans/'$CASE'_case_xtrans.csv'
    FILE_VALIDATION=$FILE_ROOT'data/ARA/validation/SourceLocARA.xsd'
    FILE_TRANSFORM=$FILE_ROOT'data/ARA/transformation/MappingMapToCanLocARA_A.xslt'
    run_xtrans $CASE -s

#    CASE=3
#    FILE_INPUT=$FILE_OUTPUT
#    FILE_OUTPUT=$FILE_ROOT'output/xtrans/'$CASE'_case_xtrans.upx'
#    FILE_VALIDATION=$FILE_ROOT'data/ARA/validation/CanLocARA_B.xsd'
#    FILE_TRANSFORM=$FILE_ROOT'data/ARA/transformation/MappingMapToModelLocARA.xslt'
#    run_xtrans $CASE










