import csv
import keyword
import os

def main():

    cc_names = []
    bool_cc_names = []
    meta_cc_names = []
    # read txt file -> names of cell collective models
    with open('cc_name.txt') as file:
        for line in file:
            if line[-4:] == ', B\n':
                bool_cc_names.append(line[:-4].rstrip().lower())
            elif line[-4:] == ", M\n":
                meta_cc_names.append(line[:-4].rstrip().lower())
            else:
                continue

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

    blacklist = ["pathway", "of", "drug", "in", "and", "-", "signaling", "pathways", "cell", "cycle", "receptor", "the", "from"]
    ccTOpathway= {}
    # dict -> matches cc titles to possible related pathways from pathway ontology
    # key: cc_name
    # value: list of possible pathways
    for name in bool_cc_names:
        ccTOpathway[name] = []
        tokenized_name = name.split(" ")
        for label in pathway_labels:
            tokenized_label = label.split(" ")
            for term in tokenized_name:
                if term in tokenized_label and term not in blacklist:
                    ccTOpathway[name].append(label)

    f = open("ccTOpathway.txt", "w+")
    for key, value in ccTOpathway.items():
        f.write(key + "\n-----\n")
        for v in value:
            f.write("\t" + v + "\n")

if __name__ == "__main__":
    main()


