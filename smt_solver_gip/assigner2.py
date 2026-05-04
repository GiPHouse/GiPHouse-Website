###################################################################################################
# This code is meant to accommodate an INTERACTVE process to create GiPHouse groups.  It is not   #
# meant to be started and then finish with a complete group assignment rolling out; but rather,   #
# it is meant to make suggestions and then allow for manual alterations to requirements and input #
# so that we can still include human judgement in decisions.                                      #
###################################################################################################

import project_data
import engineer_data
import assignment_info
import smt_maker
import csv_loader
from colour_codes import *

import csv
import sys
import math
from datetime import datetime
from z3 import *

initialise_colours()

########## STEP 1: reading the projects ##########

# make sure that the given projects file correctly represents this year's projects, or otherwise
# add the projects manually using project_data.add_project
with open("projects.txt", 'r', encoding="utf-8") as file:
  project_data.add_projects([ f.strip() for f in file.read().splitlines() ])

# now set short names for the projects; this is not strictly necessary, but is convenient for
# printing, since otherwise student preferences may for instance get very long
# you will also afterwards be able to refer to a project by its short name
project_data.set_short_name("Automated Water Data Validation", "Water Data")
project_data.set_short_name("Conditional Independence Testing", "Independence Testing")
project_data.set_short_name("Digitalization of the Oiconomy Pricing System", "Oiconomy")
project_data.set_short_name("Integrating Digital Pathology Tooling with QuPath", "Pathology")
project_data.set_short_name("Introduction Scavenger Hunt website", "Scavenger Hunt")
project_data.set_short_name("Music Carrier Databas", "Music Carrier")
project_data.set_short_name("My Lifestyle Platform Mobile App", "Lifestyle")
project_data.set_short_name("Portal Genius SAAS Webapplication", "Portal Genius")
project_data.set_short_name("RapidReport: an AI-driven radiology reporting", "RapidReport")
project_data.set_short_name("Upgrade of ToDI", "ToDI")
project_data.choose_short_names()

# when you are happy, change the year to the current one!
if datetime.now().year != 2026:
  project_data.print_projects()
  sys.exit(0)

########## STEP 2: reading the engineer data ##########

registrations = csv_loader.load_registrations("test_registrations.csv")

engineer_data.print_students(range(engineer_data.num_students), " * ")