#**************************************************************************************************************
#file: deid_sarthak_main.py 
#Code based on the De-identification algorithm -- scrubs PHI from free-text medical records  by M. Douglass 2004 in perl followed by adaptations by Dr. Gari Clifford's team
#The part of the code is for identifying the **Category Dates** from medical records and has been edited by 
# Sarthak Satpathy as part of the BMI-500 course at Emory University, GA, USA
# Date: Oct 17, 2021
#
#_______________________________________________________________________________
#
#deid_sarthak_extra.py : De-identification algorithm -- scrubs Date PHI from free-text medical records 
# Command to run the python program: 
# python deid_sarthak_extra.py <input_filename> <output_filename>
#
# Input arguments: 
# input_filename (usual extension .txt): file to be de-identified eg. id.txt
# output_filename (usual extension .phi): output file with patient name record and the date PHI coordinate on the chunk eg. date.phi
#
# Required modules to import: 're', 'sys'
#
# Output files: 
# filename.phi: 
# code performance statistics can be evaluated by using the stats.py script
# Command to run the stats.py program:
# python stats.py id.deid id-phi.phrase <output file from deid_sarthak_extra.py script

#### Block 1: Importing libraries and initializing the regular expression ####
import re
import sys
#the regular expression to look for datr

date_pattern ='(\d{1,2}[-/]\d{1,2}[-\.\s/]??\d{0,4}|\(\d{1,2}\)*\d{1,2}[-\s/]??\d{0,4})'
"""
The regular expression looks for text with the following order: first a digit, which can be upto ones or tens place, followed by a delimiter and another set of digits varying from 0-4 as there could be some dates without Year and some with year in 2 digit and 4 digit formats
"""
# compiling the reg_ex would save sime time!
date_reg = re.compile(date_pattern)
#####

#### Block 2: Defining a function that looks for date in each chunk of the input txt file ####
def check_for_date(patient,note,chunk, output_handle):
    """
    Inputs:
        - patient: Patient Number, will be printed in each occurance of personal information found
        - note: Note Number, will be printed in each occurance of personal information found
        - chunk: one whole record of a patient
        - output_handle: an opened file handle. The results will be written to this file.
            to avoid the time intensive operation of opening and closing the file multiple times
            during the de-identification process, the file is opened beforehand and the handle is passed
            to this function. 
    Logic:
        Search the entire chunk for phone number occurances. Find the location of these occurances 
        relative to the start of the chunk, and output these to the output_handle file. 
        If there are no occurances, only output Patient X Note Y (X and Y are passed in as inputs) in one line.
        Use the precompiled regular expression to find phones.
    """
    # we found that adding this offset to start and end positions would produce the same results
    offset = 27

    # For each new note, the first line should be Patient X Note Y and then all the personal information positions
    output_handle.write('Patient {}\tNote {}\n'.format(patient,note))

    # search the whole chunk, and find every position that matches the regular expression
    # for each one write the results: "Start Start END"
    # Also for debugging purposes display on the screen (and don't write to file) 
    # the start, end and the actual personal information that we found
    for match in date_reg.finditer(chunk):
                
            # debug print, 'end=" "' stops print() from adding a new line
            #print(patient, note,end=' ')
            #print((match.start()-offset),match.end()-offset, match.group())
            # initialize a flag variable to zero
            flag = 0             
            test = match.group() # test variable stores the matched string like 2/19
            # in the test variable we store a list where all the digits are extracted as a list
            test = re.findall(r'\d+', test) 
            # If the string has only 1 digit, we use the conditional for checking if the number is greater than 31, the max number a month or date can take
            #print(test)
            if len(test) ==1:
                if int(test[0]) >31:
                    flag+=1
            # If the string has only 2 numbers, we use the conditional for checking if the number is greater than 12 and 31 respectively, the max number a month or date can take 
            # we also look for zeros
            if len(test) ==2:
                #flag+=1
                if int(test[0]) >12:
                    flag+=1
                if int(test[0]) ==0:
                    flag+=1
                if int(test[1]) >31:
                    flag+=1
                if int(test[0]) ==0:
                    flag+=1
            if flag < 1:
                # create the string that we want to write to file ('start start end')    
                result = str(match.start()-offset) + ' ' + str(match.start()-offset) +' '+ str(match.end()-offset) 
            
                # write the result to one line of output
                output_handle.write(result+'\n')
                print(patient, note,end=' ')
                print((match.start()-offset),match.end()-offset, match.group())


#### Block 3: The final step where the Block 2 is looped over all patient records and notes ####
def deid_date(text_path= 'id.text', output_path = 'date.phi'):
    """
    Inputs: 
        - text_path: path to the file containing patient records
        - output_path: path to the output file.
    
    Outputs:
        for each patient note, the output file will start by a line declaring the note in the format of:
            Patient X Note Y
        then for each phone number found, it will have another line in the format of:
            start start end
        where the start is the start position of the detected phone number string, and end is the detected
        end position of the string both relative to the start of the patient note.
        If there is no phone number detected in the patient note, only the first line (Patient X Note Y) is printed
        to the output
    Screen Display:
        For each phone number detected, the following information will be displayed on the screen for debugging purposes 
        (these will not be written to the output file):
            start end phone_number
        where `start` is the start position of the detected phone number string, and `end` is the detected end position of the string
        both relative to the start of patient note.
    
    """
    # start of each note has the patter: START_OF_RECORD=PATIENT||||NOTE||||
    # where PATIENT is the patient number and NOTE is the note number.
    start_of_record_pattern = '^start_of_record=(\d+)\|\|\|\|(\d+)\|\|\|\|$'

    # end of each note has the patter: ||||END_OF_RECORD
    end_of_record_pattern = '\|\|\|\|END_OF_RECORD$'

    # open the output file just once to save time on the time intensive IO
    with open(output_path,'w+') as output_file:
        with open(text_path) as text:
            # initilize an empty chunk. Go through the input file line by line
            # whenever we see the start_of_record pattern, note patient and note numbers and start 
            # adding everything to the 'chunk' until we see the end_of_record.
            chunk = ''
            for line in text:
                record_start = re.findall(start_of_record_pattern,line,flags=re.IGNORECASE)
                if len(record_start):
                    patient, note = record_start[0]
                chunk += line

                # check to see if we have seen the end of one note
                record_end = re.findall(end_of_record_pattern, line,flags=re.IGNORECASE)

                if len(record_end):
                    # Now we have a full patient note stored in `chunk`, along with patient numerb and note number
                    # pass all to check_for_phone to find any phone numbers in note.
                    check_for_date(patient,note,chunk.strip(), output_file)
                    
                    # initialize the chunk for the next note to be read
                    chunk = ''

if __name__== "__main__":
        
    
    
    deid_date(sys.argv[1], sys.argv[2])
    