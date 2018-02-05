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
import csv 
import os
from itertools import islice
from lxml import etree

class PyTrans:
    def __init__(self, trans_args, chunk_size=5000, flg_verbose=True):
        self.verbose   = flg_verbose
        self.threshold = 100000000  # Max file size for file_ReadAll() method, in bytes [100MB]

        self.xsd  = etree.parse(trans_args['d'])  # validation file
        self.xslt = etree.parse(trans_args['t'])  # transform file
        self.fpath_input   = trans_args['c']      # file_in.csv
        self.fpath_output  = trans_args['o']      # file_out.csv
        self.ext           = os.path.splitext(self.fpath_output)[1]

        #Row Control Vars
        self.row_nums   = (trans_args['s'] == 's')  # Is 's' or 'S' as well?
        self.row_limit  = chunk_size      # MAX number of CSV input rows to process for each pass      
        self.row_start  = 1               # Start of input file segment to process
        self.row_end    = self.row_limit  # end of input file segment to process 
        self.row_header_in  = None        # CSV col header 
        self.row_header_out = None        # CSV col header Post Transform

        # Input Validation  
        if (self.ext == ''):
            raise TypeError("Missing file extention for output file.")




# --- Main loop --------------------------------------------------------------#

    def __call__(self):

        # read input CSV header 
        fd_input = open(self.fpath_input, 'r')
        self.row_header_in = self.file_ReadSlice(fd_input, 0, 0)[0]

        """ 
        csv_input_slice[0]  == CSV data
        csv_input_slice[1]  == row Num for first element 
        csv_input_slice[2]  == row Num for last element 
        """
        for csv_input_slice in self.file_NextSlice(fd_input):


            # DEBUG PRINT 
            print("--- lines[%d .. %d] ----------------------------------------------" % (csv_input_slice[1],csv_input_slice[2]))

            # Convert CSV -> XML
            xml_input_slice = self.csvToXML(self.row_header_in, csv_input_slice[0])    #covert to lxml object
            self.print_xml(xml_input_slice)

            # Transform
            xml_output = self.xmlTransform(xml_input_slice, self.xslt)
            self.print_xml(xml_output)

            # Validate Output 
            print ( self.xmlValidate(xml_output,
                             self.xsd) )

            #Convert transform XML back to CSV 
            csv_output = self.xmlToCVS(xml_output,          #XML etree
                                       csv_input_slice[1],  #First Row in this slice
                                       csv_input_slice[2])  #Last Row in this slice

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
                rec.set(self.row_header_in[i], row[i])
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

    def xmlToCVS(self, xml_elementTree, row_first, row_last):
        root = xml_elementTree.getroot()
        
        # Check if this is the first file chunk processed
        # and Extract the New CSV header 
        if not (self.row_header_out):
            self.row_header_out = root[0].keys()

            if self.row_nums:
                self.row_header_out.insert(0,'ROW_ID')
            #Append first line to output csv file
            self.file_writeHeader(self.row_header_out)


        # Convert each chunk into Python Dict then pass to:
        #     class csv.DictWriter(csvfile ... )
        #     see: https://docs.python.org/2/library/csv.html 

        line_counter = row_first

        for rec in root:
            #print([rec.get(key) for key in self.row_header_out])

            # Convert Row record to python dict() Object
            rec_d = rec.attrib 

            # append ROW_ID
            if self.row_nums:
                rec_d['ROW_ID'] = str(line_counter)
                line_counter += 1 

            # Append to output file 
            self.print_dict(rec_d)
            self.file_AppendRow(self.row_header_out, rec_d)

        # guard for correct Row numbering
        if ((self.row_nums) and (line_counter-1 != row_last)):
            raise KeyError('Row_ID missmatch') 




    # http://lxml.de/2.0/validation.html
    # If valid   -> Return True 
    #    invalid -> error_log 
    def xmlValidate(self, xml_etree, xsd_etree):
        xmlSchema = etree.XMLSchema(xsd_etree) 
        self.print_xml(xml_etree)
        self.print_xml(xsd_etree)
        # Calling 'assertValid' will raise execptions, --> should be handled above this level  
        #if (xmlSchema.assertValid(xml_etree)):
        if (xmlSchema.validate(xml_etree)):
            return True
        else:
            print("Wanining: Input failed to Valida")
            log = xmlSchema.error_log
            print(log.last_error)
            return False


    # http://lxml.de/xpathxslt.html#xslt    
    def xmlTransform(self, xml_doc, xslt):
        lxml_transform = etree.XSLT(self.xslt)      
        return lxml_transform(xml_doc)


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

    ## Function to append output as its processed in batches 
    #
    # file_object: OutputFile 
    # row_names: list of row names  -->   ['ROW_ID', 'ACCNTNUM', .. ]
    # row_data: dict mapping for XML Atribuites  {'ROW_ID': '1', 'ACCNTNUM': '0.02',   ....  }
    # https://docs.python.org/2/library/csv.html
    def file_AppendRow(self, row_names, row_data):
        file_out = open(self.fpath_output, 'awb')
        writer = csv.DictWriter(file_out,
                                fieldnames=row_names,
                                extrasaction='raise')
        writer.writerow(row_data)

    # WARNING: This will overwrite the file path
    def file_writeHeader(self, row_names):
        file_out = open(self.fpath_output, 'w')
        writer = csv.writer(file_out,
                            delimiter=',')
        writer.writerow(row_names)
                                


# --- Verbose Print Funcs ----------------------------------------------------#

    def print_dict(self,d):
         import pprint
         pp = pprint.PrettyPrinter(indent=4)
         pp.pprint(d)

    def print_xml(self, etree_obj):
        if (self.verbose):
            print('___________________________________________')
            print(etree.tostring(etree_obj, pretty_print=True)) 


if __name__ == "__main__":
    import argparse 

    # ---Input parser ------------------------------------------------------- #
    parser = argparse.ArgumentParser(prog='')
    parser.add_argument('-c','--input', required=True, type=str, 
                        dest='input_file_path',action='store',default=1,
                        help='Input file path.')
    parser.add_argument('-o','--output', required=True, type=str, 
                        dest='output_file_path',action='store',default=1,
                        help='output file path for writing CVS/UPX data.')
    parser.add_argument('-t','--xslt', required=True, type=str, 
                        dest='transformation_file_path',action='store',default=1,
                        help='xslt file path.')
    parser.add_argument('-d','--xls', required=True, type=str, 
                        dest='validation_file_path',action='store',default=1,
                        help='xsd file path.')
    parser.add_argument('-s','--sequ', required=False, 
                        dest='row_flag',action='store_true',default=False,
                        help='Boolean to append ROW_ID to output file')
    parser.add_argument('-l','--linebatch', required=False, type=int, 
                        dest='lines',action='store',default=50000,
                        help='Number of lines to process in each iteration')

    args = parser.parse_args()

    # expected Arg dict()
    xtrans_args = { 
        'd': args.validation_file_path,
        'c': args.input_file_path,
        't': args.transformation_file_path,
        'o': args.output_file_path,
        's': ''
    }
    if args.row_flag:
        xtrans_args['s'] = 's'

    #print(xtrans_args)
    PyTrans(xtrans_args,
            chunk_size=args.lines)()
