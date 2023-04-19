
import cc_sbml_download
import cc_text
import cc_sbml
import os

def main():

    # set the path to folder containing boolean sbml files
    sbml_bool_path = "cc_sbml_bool/"

    no_href = 0
    with open("sbml_bool_uniprot.txt", "w") as f:
        for filename in os.listdir(sbml_bool_path):
            # check if the file is a file (not a directory)
            if os.path.isfile(os.path.join(sbml_bool_path, filename)):
                if filename == ".DS_Store":
                    continue
                # path to file
                f.write(str(sbml_bool_path) + str(filename) + "\n")
                print(sbml_bool_path + filename)

                UniProt_extraction_phrases = [("UniProt ID", "UniProt"), ("UniProt Accession ID", "Accession")]
                total_UniProtID = []
                for target_phrase, index_phrase in UniProt_extraction_phrases:

                    # extract texts in notes section that contain "UniProt ID"
                    p_texts = cc_sbml.notesSBML(sbml_bool_path + filename, target_phrase)

                    # extract where "UniProt" is in href link
                    all_UniProtID = cc_sbml.retrievehref(p_texts, target_phrase, index_phrase)
                    no_href += all_UniProtID[1]
                    total_UniProtID += all_UniProtID[0]

                f.write("UniProt ID:\n" + str(total_UniProtID) +
                        "\nno_href: " + str(all_UniProtID[1]) + "\n")

                NCBI_extraction_phrases = [("NCBI Gene ID", "Gene"), ("Gene Name", "Gene")]
                total_NCBIID = []

                for target_phrase, index_phrase in NCBI_extraction_phrases:

                    # extract texts in notes section that contain "NCBI ID"
                    ncbi_texts = cc_sbml.notesSBML(sbml_bool_path + filename, target_phrase)

                    # extract where "Gene" is in href link
                    all_ncbiID = cc_sbml.retrievehref(ncbi_texts, target_phrase, index_phrase)
                    total_NCBIID += all_ncbiID[0]

                f.write("NCBI ID:\n" + str(total_NCBIID) + "\n")

                # extract the pubmed annotations
                pubmed_miriam_urn = cc_sbml.getMIRIAM_URN(sbml_bool_path + filename, "pubmed")
                f.write("PubMed:\n" + str(pubmed_miriam_urn) + "\n\n")



if __name__ == "__main__":
    main()


