#!/bin/bash

EXEC_PATH='/home/sam/oasis_work/omdk/xtrans/xtrans.exe'
DIR_ROOT='/home/sam/oasis_work/PiWind/'

FILE_OUTPUT='RESULT_XTRANS.csv'
FILE_INPUT=$DIR_ROOT'tests/data/SourceLocPiWind.csv'
FILE_VALIDATION=$DIR_ROOT'flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_SourceLoc.xsd'
FILE_TRANSFORM=$DIR_ROOT'flamingo/PiWind/Files/TransformationFiles/MappingMapToGeneric_Windstorm_CanLoc_A.xslt'


$EXEC_PATH -d $FILE_VALIDATION -c $FILE_INPUT -t $FILE_TRANSFORM -o $FILE_OUTPUT -s
