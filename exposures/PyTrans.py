
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
import os
from itertools import islice

class PyTrans:
    def __init__(self, trans_args, row_flag=False, chunk_size=5000):
        self.validation_fpath      = trans_args['d']  	# file.xsd
        self.transform_fpath       = trans_args['t']	# file.xslt
        self.input_fpath           = trans_args['c']	# file_in.csv
        self.output_fpath          = trans_args['o']	# file_out.csv
        self.rows 		           = row_flag			# flag to add first col as row numbers
        self.ext                   = os.path.splitext(self.output_fpath)[1]
        self.threshold             = 100000000          # Max file size for file_ReadAll() method, in bytes [100MB]
        #self.lineLimit             = chunk_size     
        #self.lineCount             = -1                 # Points the the Row number of the first line read in current iter
        if (self.ext == ''):
            raise TypeError("Missing file extention for output file.")



    def __call__(self):
        first_row = ''  # read Row0 of input csv 
        fd_xsd   = self.readFile(self.validation_fpath)
        fd_xslt  = self.readFile(self.transform_fpath)
 #      fd_input = 




        pass
        #main exec goes here

        #read in files

        #Convert CSV -> XML 
        #Run Input validation 
        
        #Create lxml ElementTree 
        #Apply Transform 
        #Convert transform XML back to CSV 

        # If output == UPX -> apply convent 
        #Write output 
        
    def csvToUXP(self, xml_elementTree):
        pass
    def csvToXML(self, cvs_filedata):
        pass
    def xmlToCVS(self, xml_elementTree):
        pass


    def file_Append(self, fpath, payload):
        pass
        #with open(fpath,'w') as f:
            
#    def file_ReadLines(self, file_object, line_limit):
#        # if at start of file return only the first line
#        if (file_object.tell() == 0):
#            yield file_object.readline().strip()
#
#        # return lines upto 'line_limit' or untill EOL is found 
#        else:    
#            data = list()
#            for (i=0, i<line_limit, i++)
#                
#                if not data:
#                    break
#                yield data


    def file_ReadLines(self, file_obj, l_start, l_end):
        file_obj.seek(0)                                # return pointer to start of file
        file_slice = islice(file_obj, l_start,l_end)    # create iterator for the file slice
        return [line.strip() for line in file_slice]    # return selected lines as list()

    def file_ReadAll(self, fpath):
        if self.file_isSmall(fpath):
            with open(fpath,'r') as f:
                return "".join([line.strip() for line in f])
        else:
            err_str  = "Large filesize protection, "
            err_str += "check '%s' or set new size threshold" % (fpath) 
            raise IOError(err_str)


    def file_isSmall(self, fpath):
        # threshold is max size in bytes
        f_size = os.path.getsize(fpath)
        return (f_size < self.threshold)
