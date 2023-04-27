
import cc_sbml_download
import cc_text
import cc_sbml
import os
import rdffile

def main():

    # set the path to folder containing boolean sbml files
    sbml_bool_path = "cc_sbml_bool2/"

    rdffile.makeRDFfile("CAD/Cortical Area Development (SBML).sbml")

if __name__ == "__main__":
    main()


