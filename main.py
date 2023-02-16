import csv
import keyword
import os

def main():

    cc_names = []
    # read txt file -> names of cell collective models
    with open('cc_name.txt') as file:
        cc_names = [line.rstrip().lower() for line in file]

    pathway_labels = []
    # read csv file -> pathway ontology
    with open('PW.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile)
        line_count = 0
        for row in spamreader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                pathway_labels.append((row[1] + " " + row[2]).replace("|", " ").lower())
                line_count += 1

    # pathway_keywords = []
    # # pathway_keywords -> tokenized pathway labels
    # for label in pathway_labels:
    #     keyword = label.replace("(", "").replace(")", "")
    #     # remove general words (pathway, process, drug)
    #     keyword = keyword.replace("pathway", "").replace("process", "").replace("drug", "")
    #     pathway_keywords.append(keyword)

    blacklist = ["pathway", "of", "drug", "in", "and"]
    ccTOpathway= {}
    # dict -> matches cc titles to possible related pathways from pathway ontology
    for name in cc_names:
        tokenized_name = name.split(" ")
        for label in pathway_labels:
            tokenized_label = label.split(" ")
            if "pathway" in tokenized_label:
                tokenized_label.remove("pathway")
            if "of" in tokenized_label:
                tokenized_label.remove("of")
            if "drug" in tokenized_label:
                tokenized_label.remove("drug")
            if "in" in tokenized_label:
                tokenized_label.remove("in")
            if "and" in tokenized_label:
                tokenized_label.remove("and")
            if "-" in tokenized_label:
                tokenized_label.remove("-")
            for term in tokenized_name:
                if term in tokenized_label:
                    ccTOpathway[name] = label

    print(ccTOpathway)
    # for key, value in ccTOpathway.items():
    #     print(key + ": " + value)

    f = open("ccTOpathway.txt", "w+")
    for key, value in ccTOpathway.items():
        f.write(key + "\n\t" + value + "\n")



    # for name in cc_names:
    #     print(name)
    #     for word in name.split(" "):
    #         if keyword.iskeyword(word) is False:
    #             print(word, end=", ")
    #     print("")
    #     print("-----")



if __name__ == "__main__":
    main()


