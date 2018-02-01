#   AutoReload modules in iPython
# %load_ext autoreload
# %autoreload 2


from PyTrans import *

# args 
validation_file_path        = '../lxsl-testing/input/Generic_Windstorm_SourceLoc.xsd'
transformation_file_path    = '../lxsl-testing/input/MappingMapToGeneric_Windstorm_CanLoc_A.xslt' 
input_file_path             = '../lxsl-testing/input/SourceLocPiWind.csv' 
output_file_path            = '../lxsl-testing/pytrans_output/test_case_0.csv'


# expected Arg dict()
xtrans_args = {
	'd': validation_file_path,
	'c': input_file_path,
	't': transformation_file_path,
	'o': output_file_path,
	's': ''
}

TestObj = PyTrans(xtrans_args, chunk_size=5)
