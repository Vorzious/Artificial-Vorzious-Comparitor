import os
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter import messagebox
from avgui.settings.thoth import Thoth
from avgui.settings.segment_filter import *
from PIL import Image, ImageTk, ImageSequence
import json

class Avgui():
    resolution = "1280x700"
    default_rgb = (219, 219, 219)
    blue_rgb = (63, 0, 179)
    light_blue_rgb = (117, 41, 255)
    green_rgb = (49, 200, 124)
    dark_green_rgb = (0, 102, 34)
    red_rgb = (200, 44, 14)
    orange_rgb = (255, 168, 90)

    primary_file_name = ""
    secondary_file_name = ""

    def __init__(self, parent):
        self.path = os.path.abspath(__file__) # Get directory of module
        self.get_last_used_directories()

        # If config settigs contain non-existent last-used directories. Reset the last used directories to the working directory
        if not os.path.isdir(self.last_used_primary_directory) or not os.path.isdir(self.last_used_secondary_directory):
            self.set_last_used_directory("both", ".")
        else:
            self.primary_directory = self.last_used_primary_directory
            self.secondary_directory = self.last_used_secondary_directory

        self.seg_type = StringVar()
        self.ref_num = StringVar()

        # Root
        self.myParent = parent 
        self.myParent.geometry(self.resolution)

        # Main container
        self.main_container = Frame(parent, bg=self.from_rgb(self.default_rgb))
        self.main_container.pack(expand=YES, fill=BOTH)

        # Control frame
        # Left side of AVGUI -- File Configurator
        self.control_frame = Frame(self.main_container, bg=self.from_rgb(self.default_rgb))
        self.control_frame.pack(side=LEFT, expand=NO, padx=15, pady=5, ipadx=5, ipady=5)
        
        # Sets a logo
        self.logo_canvas = tk.Canvas(self.control_frame, width=325, height=300, bd=0, highlightthickness=0, bg=self.from_rgb(self.default_rgb))
        self.logo_canvas.pack(expand=YES, fill=BOTH)
        self.logo = PhotoImage(file=os.path.dirname(self.path) + "/logo.png")
        self.logo_canvas.create_image(175, 0, image=self.logo, anchor=N)

        Label(self.control_frame, text="File Configurator", font=("Helvetica", 16, "bold"), justify=LEFT, bg=self.from_rgb(self.default_rgb)).pack(side=TOP, anchor=W, ipady=30)
        
        self.format_bool = IntVar()
        self.format_required_cb = Checkbutton(self.control_frame, cursor="hand2", activebackground=self.from_rgb(self.default_rgb), bg=self.from_rgb(self.default_rgb), text="Format secondary file", variable=self.format_bool)
        self.format_required_cb.pack(side=TOP, anchor=NW, expand=NO, fill=Y)

        # Upload Buttons inside of the File Configurator
        self.buttons_frame = Frame(self.control_frame, bg=self.from_rgb(self.default_rgb))
        self.buttons_frame.pack(side=TOP, expand=NO, fill=Y, ipadx=5, ipady=5)

        # Right side of the GUI
        # Includes Status, Amount of Inconsistencies & Results
        self.comparitor_frame = Frame(self.main_container) 
        self.comparitor_frame.pack(side=RIGHT, expand=YES, fill=BOTH)        

        # Results - Top frame
        self.top_frame = Frame(self.comparitor_frame)
        self.top_frame.pack(side=TOP, expand=YES, fill=BOTH)      

        # Inconsistencies -- Right frame bottom 10%
        self.inconsistency_frame = Frame(self.comparitor_frame, relief=RIDGE, height=75, bg=self.from_rgb(self.default_rgb))
        self.inconsistency_frame.pack(side=TOP, fill=BOTH)

        # Results - Right Frame top 90%
        self.results_frame = Frame(self.top_frame, background=self.from_rgb(self.default_rgb))
        self.results_frame.pack(side=RIGHT, expand=YES, fill=BOTH)

        self.inconsistency_label = Label(self.inconsistency_frame, text="Success: 0 / 0 || Errors: 0 || Warnings: 0" , bg=self.from_rgb(self.default_rgb), font=("Helvetica", 11, "bold"), height=2)
        self.inconsistency_label.pack()
        self.resultsLabel = Label(self.results_frame, text="Result", font=("Helvetica", 14, "bold"), bg=self.from_rgb(self.default_rgb), pady=10)
        self.resultsLabel.pack(fill=X)

        self.status_label = Label(self.results_frame, text="Status", bg=self.from_rgb(self.blue_rgb), fg="white", font=("Helvetica", 12, "bold"), width=7, pady=5)
        self.status_label.pack(fill=X)

        # Prepare a scrollable text widget for bigger results        
        self.scroll = Scrollbar(self.results_frame)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.results = Text(self.results_frame, wrap=NONE, yscrollcommand=self.scroll.set, cursor="arrow")
        self.results.pack(side=LEFT, fill=BOTH, expand=True)
        self.scroll.config(command=self.results.yview)
        self.results.configure(font=("Helvetica", 9))
        self.results.config(state=DISABLED)
            
        # File configurator buttons
        self.primary_directory_frame = Frame(self.control_frame, borderwidth=5, bg=self.from_rgb(self.default_rgb))
        self.secondary_directory_frame = Frame(self.control_frame, borderwidth=5, bg=self.from_rgb(self.default_rgb))

        self.primary_directory_frame.pack(side=LEFT, expand=YES, fill=Y, anchor=N)
        self.secondary_directory_frame.pack(side=LEFT, expand=YES, anchor=N)

        self.primary_directory_label = Label(self.primary_directory_frame, text="Primary Directory", font=("Helvetica", 9, "bold"), padx=15, pady=15, bg=self.from_rgb(self.default_rgb)).pack()
        
        self.secondary_directory_label = Label(self.secondary_directory_frame, text="Secondary Directory", font=("Helvetica", 9, "bold"), padx=15, pady=15, bg=self.from_rgb(self.default_rgb)).pack()

        self.primary_directory_upload_button = Button(self.primary_directory_frame, cursor="hand2", text="Select", font=("Helvetica", 9, "bold"), activebackground=self.from_rgb(self.blue_rgb), bg=self.from_rgb(self.blue_rgb), fg="white", padx=10, pady=10, command=self.primary_directory_to_use).pack(fill=BOTH)
        self.secondary_directory_upload_button = Button(self.secondary_directory_frame, cursor="hand2", text="Select", font=("Helvetica", 9, "bold"), activebackground=self.from_rgb(self.blue_rgb), bg=self.from_rgb(self.blue_rgb), fg="white", padx=10, pady=10, command=self.secondary_directory_to_use).pack(fill=BOTH)
        
        if self.last_used_primary_directory == "." or self.last_used_secondary_directory == ".":
            self.primary_directory_chosen_label = Label(self.primary_directory_frame, text="No directory has been selected", justify=CENTER, wraplength=180, bg=self.from_rgb(self.default_rgb))
            self.secondary_directory_chosen_label = Label(self.secondary_directory_frame, text="No directory has been selected", justify=CENTER, wraplength=180, bg=self.from_rgb(self.default_rgb))
        else:
            self.primary_directory_chosen_label = Label(self.primary_directory_frame, text=self.last_used_primary_directory, justify=CENTER, wraplength=180, bg=self.from_rgb(self.default_rgb))
            self.secondary_directory_chosen_label = Label(self.secondary_directory_frame, text=self.last_used_secondary_directory, justify=CENTER, wraplength=180, bg=self.from_rgb(self.default_rgb))

        self.execute_cmp_button = Button(self.primary_directory_frame, bd=2, activebackground=self.from_rgb(self.green_rgb), bg=self.from_rgb(self.green_rgb), fg="white", font=("Helvetica", 11, "bold"), cursor="hand2", text="Run Comparison", command=self.run_cmp)
        self.execute_cmp_button.pack(fill=BOTH, expand=YES, side=BOTTOM, anchor=W, ipady=15)
        
        # Input fields for Reference Number and Segment type
        self.reference_text = Entry(self.secondary_directory_frame, textvariable=self.ref_num)
        self.reference_text.pack(fill=X, side=BOTTOM, anchor=E)
        self.reference_text_label = Label(self.secondary_directory_frame, text="Reference Number", bg=self.from_rgb(self.blue_rgb), fg="white")
        self.reference_text_label.pack(fill=X, side=BOTTOM, anchor=W, pady=3)

        self.segment_text = Entry(self.secondary_directory_frame, textvariable=self.seg_type)
        self.segment_text.pack(fill=X, side=BOTTOM, anchor=E)
        self.segment_text.bind("<KeyRelease>", self.seg_type_to_uppercase)
        self.segment_text_label = Label(self.secondary_directory_frame, text="Segment Type", bg=self.from_rgb(self.blue_rgb), fg="white")
        self.segment_text_label.pack(fill=X, side=BOTTOM, anchor=W, pady=3)
        
        self.primary_directory_chosen_label.pack(fill=BOTH)
        self.secondary_directory_chosen_label.pack(fill=BOTH)

    def primary_directory_to_use(self, event = None):
        self.primary_directory = askdirectory(initialdir=self.last_used_primary_directory, title="Open Primary Directory")
        self.set_primary_directory_text(self.primary_directory) # Update text below button to show currently selected file
        self.set_last_used_directory("primary", self.primary_directory)

    def secondary_directory_to_use(self, event = None):
        self.secondary_directory = askdirectory(initialdir=self.last_used_secondary_directory, title="Open Secondary Directory")
        self.set_secondary_directory_text(self.secondary_directory) # Update text below button to show currently selected file
        self.set_last_used_directory("secondary", self.secondary_directory)

    def run_cmp(self):
        if self.seg_type.get() != "" and self.ref_num.get() != "":
            cmp = Thoth(self.primary_directory, self.secondary_directory, self.format_bool.get(), self.seg_type.get(), self.ref_num.get())

            self.results.config(state=NORMAL) # Ensure that the program can write to the text area
            self.results.delete("1.0", END) # Ensure that there's no text in the widget -- Only show the newest comparison
            error_color_tag = self.results.tag_configure("Missing", background=self.from_rgb(self.red_rgb), foreground="white")
            
            # If no files founds
            if cmp.template_to_open == "":
                self.results.insert("1.0", "Could not find matching files inside of the primary directory\n", "Missing")
                self.set_status_text("File Missing Error")
                self.set_status_bg(self.from_rgb(self.red_rgb))

            if cmp.new_document_to_open == "":
                self.results.insert("1.0", "Could not find matching files inside of the secondary directory\n", "Missing")
                self.set_status_text("File Missing Error")
                self.set_status_bg(self.from_rgb(self.red_rgb))

            # If files have been found for both directories
            if cmp.template_to_open != "" and cmp.new_document_to_open != "":
                self.primary_file_name = cmp.template_to_open
                self.secondary_file_name = cmp.new_document_to_open
                cmp.run_comparitor()
                self.set_inconsistency_count_text(cmp.success_counter, cmp.total_counter, cmp.error_counter, cmp.warning_counter)
                
                if cmp.error_counter >= 1:
                    self.set_status_text("Failure")
                    self.set_status_bg(self.from_rgb(self.red_rgb))
                elif cmp.warning_counter >= 1:
                    self.set_status_text("Warning")
                    self.set_status_bg(self.from_rgb(self.orange_rgb))
                else:
                    self.set_status_text("Success")
                    self.set_status_bg(self.from_rgb(self.green_rgb))

                self.show_results(cmp.template_dict, cmp.new_doc_dict)
                
                if self.format_bool.get():
                    self.format_bool.set(False)

            self.results.config(state=DISABLED) # Ensure that the user can't insert text into the area
        else:
            messagebox.showerror("Information Missing", "Please fill in a Segment Type and a Reference Number")

    def set_inconsistency_count_text(self, success, total, errors, warnings):
        self.inconsistency_label['text'] = "Success: %s / %s || Errors: %s || Warnings: %s" % (success, total, errors, warnings)

    def set_status_text(self, val):
        self.status_label['text'] = val

    def set_status_bg(self, color):
        self.status_label['bg'] = color

    def set_primary_directory_text(self, directory):
        self.primary_directory_chosen_label['text'] = directory
    
    def set_secondary_directory_text(self, directory):
        self.secondary_directory_chosen_label['text'] = directory

    # Contains redundant code with thoth.py
    def show_results(self, results_template, results_new_file):
        # Ensure that the program can write to the text area
        self.results.config(state=NORMAL)

        # Ensure that there's no text in the widget -- Only show the newest comparison
        self.results.delete("1.0", END)

        # Count Lines
        line_number = len(results_template)       
        for key in sorted(results_template, reverse=True):
            if results_template[key] != results_new_file[key]:
                feedback = "Mismatch"
                color_tag = self.results.tag_configure("Mismatch", background=self.from_rgb(self.red_rgb), foreground="white")
            elif does_line_have_rule(key) == False: # Redudant code -- Needs to be fixed
                feedback = "Warning - Segment is unknown"
                color_tag = self.results.tag_configure("Warning", background=self.from_rgb(self.orange_rgb), foreground="black")
            else:
                feedback = "Success"           
                color_tag = self.results.tag_configure("Success", background="white", foreground="black")
            
            text_to_display = "%s) %s: Comparing <> %s <> Primary file has %s ; Secondary file has %s\n" % (
                line_number,
                feedback,
                key,
                results_template[key],
                results_new_file[key]
            )

            self.results.insert("1.0", text_to_display, feedback)
            line_number -= 1

        for key in sorted(results_new_file, reverse=True):
            if key not in results_template:
                text_to_display = "Primary Key Missing: Found key <> %s <> that is only present in the secondary file\n" % key
                self.results.insert("1.0", text_to_display, "Mismatch")

        self.results.insert("1.0", "Primary found: %s\nSecondary Found: %s\n\n" % (self.primary_file_name, self.secondary_file_name), "Success")

        # Ensure that the user can't insert text into the area
        self.results.config(state=DISABLED)

    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        self.master.geometry(self._geom)
        self._geom=geom

    def from_rgb(self, rgb):
        return "#%02x%02x%02x" % rgb

    def seg_type_to_uppercase(self, event):
        self.seg_type.set(self.seg_type.get().upper())

    def get_last_used_directories(self):
        with open(os.path.dirname(self.path) + "/settings/config.json", "r") as json_file:
            data = json.load(json_file)
            self.last_used_primary_directory = data["last_primary_directory_location"]
            self.last_used_secondary_directory = data["last_secondary_directory_location"]

    def set_last_used_directory(self, dir, val):
        if val != "":
            if dir == "primary":
                self.last_used_primary_directory = val
            elif dir == "secondary":
                self.last_used_secondary_directory = val
            elif dir == "both":
                self.last_used_primary_directory = val
                self.last_used_secondary_directory = val

            with open(os.path.dirname(self.path) + "/settings/config.json", "r") as json_file:
                data = json.load(json_file)

            data["last_primary_directory_location"] = self.last_used_primary_directory
            data["last_secondary_directory_location"] = self.last_used_secondary_directory

            with open(os.path.dirname(self.path) + "/settings/config.json", "w") as json_file:
                json.dump(data, json_file)