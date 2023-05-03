import libsbml
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, RDFS, XSD
import xml.etree.ElementTree as ET
import cc_sbml
import re


# takes an sbml file name
def makeRDFfile(filepath):
    # load the SBML model from a file
    reader = libsbml.SBMLReader()
    document = reader.readSBMLFromFile(filepath)
    model = document.getModel()

    # Create an RDF graph
    graph = Graph()

    # Define namespaces
    sbml_ns = Namespace("http://www.sbml.org/sbml-level3/version1/core")
    qual_ns = Namespace("http://www.sbml.org/sbml/level3/version1/qual/version1")
    dcterms_ns = Namespace("http://purl.org/dc/terms/")
    uniprot_ns = Namespace("http://www.uniprot.org/uniprot/")
    ncbi_ns = Namespace("http://www.ncbi.nlm.nih.gov/gene/")
    biopax_ns = Namespace("https://www.biopax.org/release/biopax-level3.owl#")

    bqbiol_ns = Namespace("http://www.biopax.org/release/biopax-level3.owl#")
    graph.bind('bqbiol', Namespace('http://www.biopax.org/release/biopax-level3.owl#'))

    SBML = Namespace("http://biomodels.net/sbml#")
    graph.bind('sbml', SBML)

    miriam_ns = Namespace('https://identifiers.org/')
    pubmed_ns = miriam_ns['pubmed/']

    # https://research.cellcollective.org/?dashboard=true#module/2035:1/cortical-area-development/1
    # set the model uri
    model_uri = "http://www.example.org/models/my_model"
    #graph.add((URIRef(model_uri), RDF.type, sbml_ns.Model))

    # add annotations for the model
    if model.isSetMetaId():

        # <rdf:Description rdf:about="http://www.example.org/models/my_model">
        #     <dcterms:identifier>_957b9011-08c6-43aa-a4c3-69ed1e1242db</dcterms:identifier>
        #   </rdf:Description>
        # </rdf:RDF>
        graph.add((URIRef(model_uri), DCTERMS.identifier, Literal(model.getMetaId())))

        #     <dc:title>Cortical Area Development</dc:title>
        graph.add((URIRef(model_uri), DC.title, Literal(model.getName())))

        # weird html junk
        #graph.add((URIRef(model_uri), DCTERMS.description, Literal(model.getNotesString())))

        model_pubmeds = extractPubMed(model)
        for id in model_pubmeds:
            pubmed_uri = URIRef(pubmed_ns + id)
            graph.add((URIRef(model_uri), bqbiol_ns.isDescribedBy, pubmed_uri))

    # get the QualitativeModelPlugin
    qmodel_plugin = model.getPlugin("qual")

    # get the list of QualitativeSpecies objects
    qs_list = qmodel_plugin.getListOfQualitativeSpecies()

    # iterate through the QualitativeSpecies
    for i in range(qs_list.size()):
        qs = qs_list.get(i)
        species_uri = URIRef(model_uri + "#" + qs.getId())
        # qualitative species (title)  triple
        graph.add((species_uri, DC.title, Literal(qs.getName())))
        #
        graph.add((species_uri, DCTERMS.description, Literal(qs.getName())))
        # meta id of the species
        graph.add((species_uri, DCTERMS.identifier, Literal(qs.getMetaId())))


        # add UniProt ID annotations
        UniProt_IDs = extractUniProt(qs)
        for id in UniProt_IDs:
            uniprot_uri = URIRef(uniprot_ns + id)
            graph.add((species_uri, bqbiol_ns.isVersionOf, uniprot_uri))

        # add NCBI annotations
        NCBI_IDs = extractNCBI(qs)
        for id in NCBI_IDs:
            ncbi_uri = URIRef(ncbi_ns + id)
            graph.add((species_uri, bqbiol_ns.isEncodedBy, ncbi_uri))

        # add PubMed annotations
        PubMed = extractPubMed(qs)
        for id in PubMed:
            pubmed_uri = URIRef(pubmed_ns + id)
            graph.add((species_uri, bqbiol_ns.isDescribedBy, pubmed_uri))

    # get the list of QualitativeTransitions
    qt_list = qmodel_plugin.getListOfTransitions()

    # iterate through the QualitativeTransitions
    for i in range(qt_list.size()):
            qt = qt_list.get(i)
            transition_uri = URIRef(model_uri + "#" + qt.getId())
            # triple:
            graph.add((transition_uri, RDF.type, URIRef(sbml_ns['Transition'])))
            # triple: id of transition
            graph.add((transition_uri, DC.title, Literal(qt.getId())))

            # get the list of inputs within the qualitative species
            input_list = qt.getListOfInputs()

            if input_list is None:
                continue

            # iterate through the inputs
            for j in range(input_list.size()):
                input = input_list.get(j)
                input_uri = URIRef(model_uri + "#" + input.getQualitativeSpecies())

                # link transition to input
                graph.add((transition_uri, bqbiol_ns.hasInput, input_uri))
                # RDF type
                graph.add((input_uri, RDF.type, biopax_ns.PHYSICAL_ENTITY))
                # link qualitative species to input
                graph.add((input_uri, RDFS.label, Literal(input.getQualitativeSpecies())))

            # get the list of outputs within the qualitative species
            output_list = qt.getListOfOutputs()

            if output_list is None:
                continue

            # iterate through the outputs:
            for k in range(output_list.size()):
                output = output_list.get(k)
                output_uri = URIRef(model_uri + "#" + output.getQualitativeSpecies())

                # link transition to output
                graph.add((transition_uri, bqbiol_ns.hasOutput, output_uri))
                # link qualitative species to output
                graph.add((output_uri, RDFS.label, Literal(output.getQualitativeSpecies())))


    # Serialize the RDF graph into a file
    rdf_file = 'annotations.rdf'
    with open(rdf_file, 'w') as f:
        f.write(graph.serialize(format='xml'))
    return

# uses extractID() to extract all UniProt IDs
# from a given qualitative species (qs)
def extractUniProt(qs):
    ids = []
    UniProt_extraction_phrases = [("UniProt ID", "UniProt"), ("UniProt Accession ID", "Accession")]
    for target_phrase, index_phrase in UniProt_extraction_phrases:
        ids += extractID(qs, target_phrase, index_phrase)
    return ids

# uses extractID() to extract all NCBI IDs
# from a a given qualitative species (qs)
def extractNCBI(qs):
    ids = []
    NCBI_extraction_phrases = [("NCBI Gene ID", "Gene"), ("Gene Name", "Gene"), ("Gene ID", "Gene")]
    for target_phrase, index_phrase in NCBI_extraction_phrases:
        ids += extractID(qs, target_phrase, index_phrase)
    return ids

# extract all miriam:urn pubmed IDs
# from a given qualitative species (qs)
def extractPubMed(qs):

    # list of pubmeds in the qualitative species
    pubmed = []

    # get full annotation of species
    species_annotation = qs.getAnnotation()

    # get rdf annotation of species
    rdf_annotation = species_annotation.getChild(0)

    # get description annotation of rdf
    description_annotation = rdf_annotation.getChild(0)

    # iterate through each child of the annotation
    # (each pubmed annotation)
    for i in range(description_annotation.getNumChildren()):

        # get the current child
        bqbiol = description_annotation.getChild(i)

        # get "Bag" annotation
        rdf_bag = bqbiol.getChild("Bag")

        # get "li" annotation
        rdf_li = rdf_bag.getChild("li")

        # get string between quotes
        match = re.search(r'"([^"]+)"', rdf_li.toXMLString())

        if match is not None:
            miriam_urn = match.group(1)
            if "pubmed" in miriam_urn:

                # get everything after the last colon
                last_colon_index = miriam_urn.rfind(":")
                pubmed.append(miriam_urn[last_colon_index + 1:])

    return pubmed




# extracts all IDs from a given qualitative species (qs)
# using the given target_phrase and index_phrase
def extractID(qs, target_phrase, index_phrase):
    ids = []
    # get XML notes object
    qs_notes = qs.getNotes()

    # if no notes are found, return None:
    if qs_notes is None:
        return

    # get the p elements (list of <p> elements in notes)
    p_elements = qs_notes.getChild("body")
    for j in range(p_elements.getNumChildren()):

        # strip <p> and </p>
        p = p_elements.getChild(j)

        # convert XML notes object to string
        p_text = p.getChild(0).toXMLString()

        # add text if it contains the target_phrase
        if target_phrase.lower() in p_text.lower():

            # if href in text, add and skip
            # (will be processed later)
            if "href" in p_text:
                ids.append(extracthref(p_text, target_phrase, index_phrase))
                continue
            # if code not html junk
            elif "&" not in p_text:
                # gets everything after the colon
                # removes tabs and spaces
                extracted = p_text.split(":")[1].replace("\t", "").replace(" ", "")

                # extract each ID if it has multiple
                if "/" in extracted:
                    for id in extracted.split("/"):
                        ids.append(id.replace(" ", ""))
                else:
                    ids.append(extracted)
    return ids

# extract the id from p_text
# given the target_phrase and an index_phrase
def extracthref(p_text, target_phrase, index_phrase):

    # split the text by " "
    tokenized = p_text.split(" ")

    # find each index_phrase
    indices = [i for i in range(len(tokenized)) if index_phrase in tokenized[i]]

    # iterate over found indexes
    for i in indices:
        # look for the next token that contains "href"
        # max loop set to 20 or less than length of tokenized
        # this is because some don't have href links
        index = i
        while (index < i+5) and (index < len(tokenized)):

            # find the href and end
            if "href" in tokenized[index]:
                # extract after the last "/" and before "&quot
                start_index = tokenized[index].find('/',
                                                    tokenized[index].find('/',
                                                                          tokenized[index].find('/',
                                                                                                tokenized[index].find(
                                                                                                 '/') + 1) + 1) + 1) + 1
                end_index = tokenized[index].find('&quot;', start_index)
                extracted = tokenized[index][start_index:end_index]

                # add each id if there are multiple
                if "/" in extracted:
                    # add each id if there are multiple
                    return extracted.split("/")

                else:
                    return extracted
                break
            index += 1

        # some unique cases don't have href
        return
