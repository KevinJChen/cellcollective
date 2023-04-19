import csv
from keybert import KeyBERT


# return list of boolean model names from cc_name.text
def readBoolfromText():
    bool_cc_names = []
    # read txt file -> names of cell collective models
    with open('cc_name.txt') as file:
        for line in file:
            if line[-4:] == ', B\n':
                bool_cc_names.append(line[:-4].rstrip().lower())
            else:
                continue
    return bool_cc_names


# return list of metabolic model names from cc_name.text
def readMetafromText():
    meta_cc_names = []
    # read txt file -> names of cell collective models
    with open('cc_name.txt') as file:
        for line in file:
            if line[-4:] == ', M\n':
                meta_cc_names.append(line[:-4].rstrip().lower())
            else:
                continue
    return meta_cc_names


# perform keybert keyword extraction on boolean list of names
# places it in 'boolean_keyword.txt'
def keybertExtraction(bool_cc_names):
    with open('boolean_keyword.txt', 'w') as f:
        for name in bool_cc_names:
            f.write(str(name) + " -> ")
            kw_model = KeyBERT()
            keywords = kw_model.extract_keywords(name)
            print(keywords)
            f.write(str(keywords) + "\n")


def readPathwayOntology():
    pathway_labels = []
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
    return pathway_labels


# matches titles and writes to ccTOpathway.txt
def manualTitleMatch(bool_cc_names, pathway_labels):
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