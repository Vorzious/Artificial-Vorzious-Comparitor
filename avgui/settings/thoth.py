from avgui.settings.segment_filter import *
import os, fnmatch
from tkinter.filedialog import askopenfile, askdirectory, askopenfilenames
from datetime import datetime
import re

class Thoth():
    segment_type = ""
    reference_number = ""
    template_to_open = ""
    new_document_to_open = ""
    found_segment = False
    found_reference = False
    amount_of_references_found = 0

    def __init__(self, primary, secondary, format_required, seg_type, ref_num):
        self.segment_type = seg_type
        self.reference_number = ref_num
        
        for f in os.listdir(primary):
            if f.endswith(".edi"):
                edi = open(primary + "/" + f, 'r')
                
                # Check if inside of the line there's an UNH and RFF with the given values
                for e in edi:
                    if "UNH" in e:
                        if self.segment_type in e:
                            self.found_segment = True
                        else:
                            self.found_segment = False
                    if "RFF+ON" in e and self.amount_of_references_found <= 0: # Ensures that we'll only accept one good reference. In case several references are present inside of the same file
                        if self.reference_number in e:
                            number = re.sub(r"RFF\+ON:", "", e) # Remove the RFF+ON from the line
                            number = re.sub(r"\'", "", number) # Remove the apostrophe from the line
                            number = number.strip()

                            # Ensure that the number is exactly the reference number without special characters
                            if self.reference_number == number:
                                self.found_reference = True
                                self.amount_of_references_found += 1
                        else:
                            self.found_reference = False
                
                if self.found_segment == True and self.found_reference == True:
                    self.template_to_open = edi.name
                    break # Ends for loop for primary directory when a file has been found
                else:
                    self.found_reference = False
                    self.found_segment = False
                    self.amount_of_references_found = 0

                edi.close()
                
        # Reset values for secondary loop --> Primary values should be saved already
        self.found_reference = False
        self.found_segment = False
        self.amount_of_references_found = 0

        for f in os.listdir(secondary):
            if f.endswith(".edi"):
                if format_required:
                    f = self.find_replace(secondary + "/" + f, "'", "'\n")
                    edi = open(f, 'r')
                else:
                    edi = open(secondary + "/" + f, 'r')

                # Check if inside of the line there's an UNH and RFF with the given values
                for e in edi:
                    if "UNH" in e:
                        if self.segment_type in e:
                            self.found_segment = True
                        else:
                            self.found_segment = False
                    if "RFF+ON" in e and self.amount_of_references_found <= 0: # Ensures that we'll only accept one good reference. In case several references are present inside of the same file
                        if self.reference_number in e:
                            number = re.sub(r"RFF\+ON:", "", e) # Remove the RFF+ON from the line
                            number = re.sub(r"\'", "", number) # Remove the apostrophe from the line
                            number = number.strip()

                            # Ensure that the number is exactly the reference number without special characters
                            if self.reference_number == number:
                                self.found_reference = True
                                self.amount_of_references_found += 1
                        else:
                            self.found_reference = False

                if self.found_segment == True and self.found_reference == True:
                    self.new_document_to_open = edi.name
                    break # Ends for loop for secondary directory when a file has been found
                else:
                    self.found_reference = False
                    self.found_segment = False
                    self.amount_of_references_found = 0

                edi.close()

                if format_required:
                    os.remove(f) # Removes the _formatted files that don't meet the user requirements

    def run_comparitor(self):
        template = open(self.template_to_open, 'r')
        new_doc = open(self.new_document_to_open, 'r')

        # Prepare a list to compare the lines in
        template_list = []
        new_doc_list = []

        # Prepare a dictionary to compare amount of sections in
        self.template_dict = {}
        self.new_doc_dict = {}

        # Track amount of errors, warnings & success'
        self.error_counter = 0
        self.warning_counter = 0
        self.success_counter = 0
        self.total_counter = 0

        for line in template:
            template_list.append(line)

        for line in new_doc:
            new_doc_list.append(line)

        # Counts all the headers for the template file
        for i in range(len(template_list)):
            header = line_rules(template_list[i])
            
            if header not in self.template_dict.keys():
                self.template_dict[header] = 1
            else:
                self.template_dict[header] += 1

        # Counts all the headers for the comparison file
        for i in range(len(new_doc_list)):
            header = line_rules(new_doc_list[i])

            if header not in self.new_doc_dict.keys():
                self.new_doc_dict[header] = 1
            else:
                self.new_doc_dict[header] += 1

        # Compared the count in both dictionaries with the template as a baseline
        for key in self.template_dict:
            if key not in self.new_doc_dict:
                self.new_doc_dict[key] = 0

            if self.template_dict[key] != self.new_doc_dict[key]:
                self.error_counter += 1
            elif not does_line_have_rule(key):
                self.warning_counter += 1
            else:
                self.success_counter +=1
            
            self.total_counter += 1


        for key in self.new_doc_dict:
            if key not in self.template_dict:
                self.error_counter += 1
                self.total_counter += 1

        # Close Documents to finish off the functions properly
        template.close()
        new_doc.close()

        self.write_away_results(self.template_dict, self.new_doc_dict)

    def write_away_results(self, primary_results, secondary_results):
        file_name_to_generate = self.generate_name(primary_results, "UNH", "RFF+ON")
        path = os.path.abspath(os.path.join(__file__, "../../")) # Get directory of module
        dir_path = os.path.dirname(path)
        
        if os.path.isdir(dir_path + "/comparisons"):
            os.chdir(dir_path + "/comparisons") # Ensures files are going to be saved in a comparisons directory
        else:
            os.mkdir(dir_path + "/comparisons") # Ensure that the comparisons directory exists - if not, create it
            os.chdir(dir_path + "/comparisons") # Ensures files are going to be saved in a comparisons directory

        f = open(file_name_to_generate, "w+")

        f.write("Primary found: %s\nSecondary Found: %s\n\n" % (self.template_to_open, self.new_document_to_open))

        for key in sorted(secondary_results):
            if key not in primary_results:
                text_to_display = "Not Primary Error: Found key <> %s <> that is only present in the secondary file\n" % key
                f.write(text_to_display)

        line_number = 1 # Ensure that the line number starts with 1
        for key in sorted(primary_results):
            if primary_results[key] != secondary_results[key]:
                feedback = "Mismatch"
            elif does_line_have_rule(key) == False: # Redudant code -- Needs to be fixed
                feedback = "Warning - Segment is unknown"
            else:
                feedback = "Success"           

            text_to_display = "%s) %s: Comparing <> %s <> Primary file has %s ; Secondary file has %s \n" % (
                line_number,
                feedback,
                key,
                primary_results[key],
                secondary_results[key]
            )
            f.write(text_to_display)
            line_number += 1

        f.write("Amount of inconsistencies %s" % self.error_counter)

        f.close()
        os.chdir("..") # Go back to parent directory

    def find_replace(self, file, seperator, replace):
        with open(file) as f:
            s = f.read()
            f.close()
        s = s.replace(seperator, replace)
        
        file = re.sub(r'\.edi', "_formatted.edi", file) # Formats new file name to be filename_formatted.edi

        with open(file, "w+") as f:
            f.write(s)
            f.close()
            return f.name

    def generate_name(self, primary_results, primary, secondary):
        # FIXME
        # "UNH" is now getting added to the name.... 
        today = datetime.date(datetime.now())
        today = today.strftime("%Y%m%d")
        primary_filter = [key for key, value in primary_results.items() if primary in key][0] # Always grab the first segment type from a list to create a name        
        secondary_filter = [key for key, value in primary_results.items() if secondary in key][0]  # Always grab the first additional type from a list to create a name
        secondary_filter = secondary_filter.rsplit(":")[1] # Only grab the reference number, remove unnecessary information
        name = "%s_%s_%s.txt" % (today, primary_filter, secondary_filter)
        
        return name