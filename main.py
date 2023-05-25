
import cc_sbml_download
import cc_text
import cc_sbml
import os
import rdffile

def main():

    # set the path to folder containing boolean sbml files
    sbml_bool_path = "cc_sbml_bool2/"

    nine_qs = "Cell Cycle Transcription by Coupled CDK and Network Oscillators (SBML).sbml"

    # for root, dirs, files in os.walk(sbml_bool_path):
    #     for file_name in files:
    #         rdffile.makeRDFfile(sbml_bool_path + file_name)

    rdffile.makeRDFfile(sbml_bool_path + nine_qs)


    #rdffile.makeRDFfile("CAD/Cortical Area Development (SBML).sbml")
    #rdffile.makeRDFfile("BMID000000018784.xml")
    #rdffile.makeRDFfile("BMID000000018771.xml")
    #rdffile.makeRDFfile("BIOMD0000000562_url.xml")
if __name__ == "__main__":
    main()


