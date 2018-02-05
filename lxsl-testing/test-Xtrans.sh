#!/bin/bash

EXEC_PATH='./xtrans/xtrans.exe'
DIR_ROOT='/home/sam/oasis_work/PiWind/'

FILE_OUTPUT_UPX='RESULT_XTRANS.upx'
FILE_OUTPUT_CSV='RESULT_XTRANS.csv'
FILE_INPUT=$DIR_ROOT'tests/data/SourceLocPiWind.csv'
FILE_VALIDATION=$DIR_ROOT'flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_SourceLoc.xsd'
FILE_TRANSFORM=$DIR_ROOT'flamingo/PiWind/Files/TransformationFiles/MappingMapToGeneric_Windstorm_CanLoc_A.xslt'


echo '-- RUN CVS output --------------------------'
mono $EXEC_PATH -d $FILE_VALIDATION -c $FILE_INPUT -t $FILE_TRANSFORM -o $FILE_OUTPUT_CSV -s
cat $FILE_OUTPUT_CSV


## ERROR -> must use files from ARA model 

echo '-- RUN UPX output --------------------------'
mono $EXEC_PATH -d $FILE_VALIDATION -c $FILE_INPUT -t $FILE_TRANSFORM -o $FILE_OUTPUT_UPX -s
cat $FILE_OUTPUT_UPX
