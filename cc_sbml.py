import ccapi
from libsbml import *
import libsbml
import xml.etree.ElementTree as ET
import re

def openSBML():
    reader = SBMLReader()
    doc = reader.readSBML("data/test2.sbml")
    print(doc.getNumErrors())
    print(doc.getErrorLog().toString())

    model = doc.getModel()

    qual_model = model.getPlugin("qual")

# make the UniProt ID into link to it
def makeUniProtLink(UniProt):
    return UniProt


# make the NCBI ID into link to it
def makeNCBILink(NCBI):
    return NCBI

# retrieve the uniform resource names (URNs) in the
# minimal information requested in the annotation of models (MIRIAM)
def getMIRIAM_URN(SBMLFile, target_phrase):

    miriam_urns = []

    # load the SBML file
    document = libsbml.readSBMLFromFile(SBMLFile)

    # get the model object
    model = document.getModel()

    if model is None:
        return

    # get the file annotations
    file_annotation = model.getAnnotation()

    # get the rdf of annotation
    rdf_annotation = file_annotation.getChild(0)

    # get description annotation of rdf
    description_annotation = rdf_annotation.getChild(0)

    for i in range(description_annotation.getNumChildren()):
        bqbiol = description_annotation.getChild(i)
        rdf_bag = bqbiol.getChild("Bag")
        rdf_li = rdf_bag.getChild("li")

        match = re.search(r'"([^"]+)"', rdf_li.toXMLString())
        if match is not None:
            miriam_urn = match.group(1)
            if target_phrase in miriam_urn:
                last_colon_index = miriam_urn.rfind(":")
                miriam_urns.append(miriam_urn[last_colon_index + 1:])

    # get the QualitativeModelPlugin
    qmodel_plugin = model.getPlugin("qual")

    # get the list of QualitativeSpecies objects
    qs_list = qmodel_plugin.getListOfQualitativeSpecies()

    for species in qs_list:

        # get full annotation of species
        species_annotation = species.getAnnotation()

        # get rdf annotation of species
        rdf_annotation = species_annotation.getChild(0)

        # get description annotation of rdf
        description_annotation = rdf_annotation.getChild(0)

        for i in range(description_annotation.getNumChildren()):
            bqbiol = description_annotation.getChild(i)
            rdf_bag = bqbiol.getChild("Bag")
            rdf_li = rdf_bag.getChild("li")

            match = re.search(r'"([^"]+)"', rdf_li.toXMLString())
            if match is not None:
                miriam_urn = match.group(1)
                if target_phrase in miriam_urn:
                    last_colon_index = miriam_urn.rfind(":")
                    miriam_urns.append(miriam_urn[last_colon_index + 1:])

    return miriam_urns



    # get the list of QualitativeSpecies objects
    qs_list = qmodel_plugin.getListOfQualitativeSpecies()

    # loop through the qualtiative species
    for species in qs_list:

        # get rdf tag from the annotation
        rdf = species.getAnnotation().getChild("RDF")
        if rdf is None:
            continue

        # loop through elements of rdf tag
        for i in range(rdf.getNumChildren()):
            li = rdf.getChild(i)
            resource = li.getAttrValue("rdf:Bag")
            if "pubmed" in resource:
                pmid = resource.split(":")[-1]
                print(species.getId(), pmid)


# retrieve the href link from target phrase
def retrievehref(p_texts, target_phrase, index_phrase):
    href = []
    if p_texts is None:
        return

    no_href = 0
    # iterate through each p element in p_texts
    for p in p_texts:
        if len(p) < 30:
            href.append(p)
            continue

        # split the text by " "
        tokenized = p.split(" ")

        # find each UniProt index
        indices = [i for i in range(len(tokenized)) if index_phrase in tokenized[i]]

        for i in indices:
            # look for the next token that contains "href"
            # max loop set to 20 or less than length of tokenized
            index = i
            while (index < i+5) and (index < len(tokenized)):

                # find the href and end
                if "href" in tokenized[index]:

                    # extract after the last "/" and before &quot
                    start_index = tokenized[index].find('/',
                                                        tokenized[index].find('/',
                                                                              tokenized[index].find('/',
                                                                                                    tokenized[index].find('/') + 1) + 1) + 1) + 1
                    end_index = tokenized[index].find('&quot;', start_index)
                    extracted = tokenized[index][start_index:end_index]
                    if "/" in extracted:
                        #  add each id if there are multiple
                        for id in extracted.split("/"):
                            href.append(id)
                    else:
                        href.append(extracted)
                    break
                index += 1

            # some unique cases don't have href
            if index >= len(tokenized) or index >= i+5:
                no_href += 1
                continue
    # print("no_href: " + str(no_href))
    return href, no_href


# takes SBMLfile and target phrase
# goes through notes section of each QualitativeSpecies object
def notesSBML(SBMLfile, target_phrase):
    p_texts = []

    # read the SBML file
    sbml_document = libsbml.readSBMLFromFile(SBMLfile)

    # get the model
    model = sbml_document.getModel()

    # if no model, return
    if model is None:
        print(SBMLfile, "THIS FILE HAS NO MODEL")
        return

    # get the QualitativeModelPlugin
    qmodel_plugin = model.getPlugin("qual")

    # get the list of QualitativeSpecies objects
    qs_list = qmodel_plugin.getListOfQualitativeSpecies()

    # iterate through the notes of each QualitativeSpecies object
    for i in range(qs_list.size()):
        qs = qs_list.get(i)

        # get XML notes object
        qs_notes = qs.getNotes()

        # if no notes are found, continue
        if qs_notes is None:
            continue

        # get the p elements (list of <p> elements in notes)
        p_elements = qs_notes.getChild("body")
        for j in range(p_elements.getNumChildren()):

            # strip <p> and </p>
            p = p_elements.getChild(j)

            # convert XML notes object to string
            p_text = p.getChild(0).toXMLString()

            # add text if it contains the target_phrase
            if target_phrase in p_text:

                # if href in text, add and skip
                # (will be processed later)
                if "href" in p_text:
                    p_texts.append(p_text)
                    continue
                # if code is not html junk
                elif "&" not in p_text:
                    # get everything after the colon
                    # removes tabs and spaces
                    extracted = p_text.split(":")[1].replace("\t", "").replace(" ", "")

                    # extract each ID if it has multiple
                    if "/" in extracted:
                        for id in extracted.split("/"):
                            p_texts.append(id.replace(" ", ""))
                    else:
                        p_texts.append(extracted)
    return p_texts


# update an SBML file from version 1 to the latest version

# read SBML file, check version, and it is 1
# upgrade to the latest version using setLevelAndVersion

# validates the updated SBML with SBMLValidator

def updateSBMLversion():
    sbml_reader = libsbml.SBMLReader()
