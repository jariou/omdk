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
#import lxml
import csv 
import os
from itertools import islice
from lxml import etree

class PyTrans:
    def __init__(self, trans_args, chunk_size=5000, flg_row=False,
                                                    flg_verbose=True):
        # file data, as single string
        self.verbose   = flg_verbose
        self.threshold = 100000000  # Max file size for file_ReadAll() method, in bytes [100MB]
        #self.xsd  = self.file_ReadAll(trans_args['d'])  # validation file
        #self.xslt = self.file_ReadAll(trans_args['t'])  # transform file

        self.xsd  = etree.parse(trans_args['d'])  # validation file
        self.xslt = etree.parse(trans_args['t'])  # transform file
        # paths to I/O files
        self.fpath_input   = trans_args['c']	# file_in.csv
        self.fpath_output  = trans_args['o']	# file_out.csv
        self.ext           = os.path.splitext(self.fpath_output)[1]

        #Row Control Vars
        self.row_nums   = flg_row        # flag to add first col as row numbers
        self.row_limit  = chunk_size     # MAX number of CSV input rows to process for each pass      
        self.row_start  = 1              # Start of input file segment to process
        self.row_end    = self.row_limit # end of input file segment to process 
        self.row_header = ""             # CSV col header 

        # Input Validation  
        if (self.ext == ''):
            raise TypeError("Missing file extention for output file.")




# --- Main loop --------------------------------------------------------------#

    #def __call__(self):
    def run(self):


        # read input CSV header 
        fd_input = open(self.fpath_input, 'r')
        self.row_header = self.file_ReadSlice(fd_input, 0, 0)[0]

        """ 
        csv_input_slice[0]  == CSV data
        csv_input_slice[1]  == row Num for first element 
        csv_input_slice[2]  == row Num for last element 
        """
        for csv_input_slice in self.file_NextSlice(fd_input):
            # Convert CSV -> XML
            xml_input_slice = self.csvToXML(self.row_header, csv_input_slice[0])    #covert to lxml object
            self.xmlPrint(xml_input_slice)

            # Transform
            xml_output = self.xmlTransform(xml_input_slice, self.xslt)
            self.xmlPrint(xml_output)

            # Validate Output 
            self.xmlValidate(xml_output,
                             self.xsd)


            # DEBUG
            #return xml_output

            #Convert transform XML back to CSV 

            # Write to Output 
            # If output == UPX -> apply convent 
            #Write output 
     


        




# --- Transform Functions ----------------------------------------------------#
# https://pymotw.com/2/xml/etree/ElementTree/create.html
# http://lxml.de/api/lxml.etree._Element-class.html


    # --- CSV Funcs --- #

    def csvToXML(self, csv_header, csv_data):
        root = etree.Element('root') 
        #fetch each row
        for row in csv_data:
            #Create new 'empty' record   
            rec = etree.SubElement(root, 'rec')
            # Iter over columns and set attributs 
            for i in range(0,len(row)):
                rec.set(self.row_header[i], row[i])
        return root 
    def csvToUXP(self, xml_elementTree):
        pass
    def csvInsertRowNums(self,csv_data,r_start,r_end):
        row_index = range(r_start,r_end)
        row_total = len(row_nums)
        if(row_total != len(csv_data)):
            raise TypeError('Size mismatch between row numbering and dataset')
        return [[row_index[i]] + csv_data[i] for i in range(0,row_total)] 


    # --- XML Funcs --- #

    # WARNING: abributes are stored as dict() object which means keys are returned in an arbitray order
    # so long as the keys are consistrance with values this shouldnt be a problem.. i think?
    def xmlToCVS(self, xml_elementTree):
        root = xml_elementTree.getroot():


        pass

    # http://lxml.de/2.0/validation.html
    def xmlValidate(self, xml_etree, xsd_etree):
        xmlSchema = etree.XMLSchema(xsd_etree) 
   
        self.xmlPrint(xml_etree)
        self.xmlPrint(xsd_etree)
        # Calling 'assertValid' will raise execptions, --> should be handled above this level  
        if (xmlSchema.assertValid(xml_etree)):
            return True

    # http://lxml.de/xpathxslt.html#xslt    
    def xmlTransform(self, xml_doc, xslt):
        lxml_transform = etree.XSLT(self.xslt)      
        return lxml_transform(xml_doc)


    def xmlPrint(self, etree_obj):
        if (self.verbose):
            print('___________________________________________')
            print(etree.tostring(etree_obj, pretty_print=True)) 

# --- File I/O Functions -----------------------------------------------------#

    # Generator Function which processes and returns batches of the input CSV file
    def file_NextSlice(self, file_object):
        while True:
            csv_chunk = self.file_ReadSlice(file_object, 
                                            self.row_start, 
                                            self.row_end)
            # Exit check for EOF
            if (csv_chunk == []):
                #print("File Slice EMPTY: rows[%d .. %d]\n" % (self.row_start, self.row_end)) 
                break 
            else:
                #DEBUG Print
                #print("File Slice: rows[%d .. %d]" % (self.row_start, self.row_end))
                #for row_line in csv_chunk:
                #    print(row_line)
                #print('\n')
                slice_start = self.row_start 
                slice_end   = self.row_end

                self.row_start += self.row_limit
                self.row_end   += self.row_limit
                yield csv_chunk, slice_start, slice_end

    # Return Line numbers of a file between [l_start .. l_end]
    def file_ReadSlice(self, file_obj, l_start, l_end):
        file_obj.seek(0)                                # return pointer to start of file
        input_reader = csv.reader(file_obj, delimiter=',') 
        file_slice = islice(input_reader, l_start,l_end+1)  # create iterator for the file slice
        return [line for line in file_slice]    # return selected lines as list()

    # Retrun entire file as single string (Used for 'xsd/xslt')    
    def file_ReadAll(self, fpath):
        if self.file_isSmall(fpath):
            with open(fpath,'r') as f:
                return "".join([line.strip() for line in f])
        else:
            err_str  = "Large filesize protection, "
            err_str += "check '%s' or set new size threshold" % (fpath) 
            raise IOError(err_str)

    # Guard function to halt 'file_ReadAll()' if filesize is > threshold value
    def file_isSmall(self, fpath):
        # threshold is max size in bytes
        f_size = os.path.getsize(fpath)
        return (f_size < self.threshold)

    # Function to append output as its processed in batches 
    def file_Append(self, fpath, payload):
        #https://docs.python.org/2/library/csv.html
        pass
