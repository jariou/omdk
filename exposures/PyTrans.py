
# -*- coding: utf-8 -*-

# BSD 3-Clause License
# 
# Copyright (c) 2017-2020, Oasis Loss Modelling Framework
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# 
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# 
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

__all__ = [
    'PyTrans'
]

import lxml


""" should parse the following arguments 
Options:
  -d, --xsd=VALUE            xsd file name
  -c, --csv=VALUE            csv file name
  -t, --xslt=VALUE           xslt file name
  -o, --output=VALUE         output file name
  -s                         Add sequence number column
  -h, --help                 show this message and exit

----------------------------------------------------------

execpt input as dict()

xtrans_args = {
       'd': validation_file_path,
       'c': input_file_path,
       't': transformation_file_path,
       'o': output_file_path,
       's': ''    						<--- Ask Ben about how this is used 
}

TEST CASE 0:
	"source_exposures_file_path": "tests/data/SourceLocPiWind.csv",
	"source_exposures_validation_file_path": "flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_SourceLoc.xsd",
	"source_to_canonical_exposures_transformation_file_path": "flamingo/PiWind/Files/TransformationFiles/MappingMapToGeneric_Windstorm_CanLoc_A.xslt",

TEST CASE 1: 
	OUTPUT of CASE 0  (csv)
	"canonical_exposures_validation_file_path": "flamingo/PiWind/Files/ValidationFiles/Generic_Windstorm_CanLoc_B.xsd",
	"canonical_to_model_exposures_transformation_file_path": "flamingo/PiWind/Files/TransformationFiles/MappingMapTopiwind_modelloc.xslt",



REF:
	https://dbader.org/blog/python-dunder-methods
	https://docs.python.org/3/reference/datamodel.html
	http://lxml.de/extensions.html

	http://blog.appliedinformaticsinc.com/how-to-parse-and-convert-xml-to-csv-using-python/
	http://lxml.de/xpathxslt.html#xslt



Support for UPX?  --> http://www.unicede.com/
	# code snippet, note the output format depends on the output filename given   

	string ext = Path.GetExtension(outputcsvfile);                                                                                                                          
		   if (ext == ".csv")
		   {
			   converttocsv(newDoc, outputcsvfile, "rec", RowDelimit.NewLine, ColumnDelimit.Comma, outputheader);
		   }
		   if (ext == ".upx")
		   {   
			   Console.WriteLine ("=======GENERATING UPX=========");
			   converttoupx(newDoc, outputcsvfile, "rec", RowDelimit.NewLine, ColumnDelimit.Comma, outputheader,ref upx);
		   }
		   return 0;


THINK ABOUT:  dealing with very large CSV files 


"""
class PyTrans:
    def __init__(self, trans_args, rows=False):
		try:
			self.validation_fpath      = trans_args['d']  	# file.xsd
			self.transformation_fpath  = trans_args['t']	# file.xslt
			self.input_fpath           = trans_args['c']	# file_in.csv
			self.output_fpath          = trans_args['o']	# file_out.csv
			self.displayRows 		   = rows				# flag to add first col as row numbers
		except KeyError as e:
			print(e)
			# handle the error 'missing variables' by throwing oasis Execption?

		def run(self):
			pass
			#main exec goes here

			#read in files

			#Convert CSV -> XML 
            #Run Input validation 
            
			#Create lxml ElementTree 
			#Apply Transform 
            #Convert transform XML back to CSV 
            #Write output 
			


		def toXML(self, cvs_filedata):
			pass

		def toCVS(self, xml_elementTree):
			pass

		def writeFile(self, fpath, payload):
			pass
			#with open(fpath,'w') as f:
				
		def readFile(self, fpath):
			pass
			#with open(fpath,'r') as f:
				#for line in f ..
			#return file_data


