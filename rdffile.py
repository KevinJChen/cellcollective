import libsbml
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, RDF, RDFS, XSD
import xml.etree.ElementTree as ET
import cc_sbml


# takes an sbml file name
def makeRDFfile(filepath):
    # load the SBML model from a file
    reader = libsbml.SBMLReader()
    document = reader.readSBMLFromFile(filepath)
    model = document.getModel()

    # Create an RDF graph
    graph = Graph()

    # Define namespace
    sbml_ns = Namespace("http://www.sbml.org/sbml-level3/version1/core")
    qual_ns = Namespace("http://www.sbml.org/sbml/level3/version1/qual/version1")
    dcterms_ns = Namespace("http://purl.org/dc/terms/")
    bqbiol_ns = Namespace("http://www.biopax.org/release/biopax-level3.owl#")
    uniprot_ns = Namespace("http://www.uniprot.org/uniprot/")
    ncbi_ns = Namespace("http://www.ncbi.nlm.nih.gov/gene/")
    graph.bind('bqbiol', Namespace('http://www.biopax.org/release/biopax-level3.owl#'))
    SBML = Namespace("http://biomodels.net/sbml#")
    graph.bind('sbml', SBML)

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

    # get the QualitativeModelPlugin
    qmodel_plugin = model.getPlugin("qual")

    # get the list of QualitativeSpecies objects
    qs_list = qmodel_plugin.getListOfQualitativeSpecies()

    # iterate through the QualitativeSpecies
    for i in range(qs_list.size()):
        qs = qs_list.get(i)
        species_uri = URIRef(model_uri + "#" + qs.getId())
        graph.add((species_uri, DC.title, Literal(qs.getName())))
        graph.add((species_uri, DCTERMS.description, Literal(qs.getName())))


        # add UniProt ID annotations
        UniProt_IDs = extractUniProt(qs)
        for id in UniProt_IDs:
            uniprot_uri = URIRef(uniprot_ns + id)
            graph.add((species_uri, bqbiol_ns.isVersionOf, uniprot_uri))

        NCBI_IDs = extractNCBI(qs)
        for id in NCBI_IDs:
            ncbi_uri = URIRef(ncbi_ns + id)
            graph.add((species_uri, bqbiol_ns.isEncodedBy, ncbi_uri))

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
# from a agiven qualitative species (qs)
def extractNCBI(qs):
    ids = []
    NCBI_extraction_phrases = [("NCBI Gene ID", "Gene"), ("Gene Name", "Gene"), ("Gene ID", "Gene")]
    for target_phrase, index_phrase in NCBI_extraction_phrases:
        ids += extractID(qs, target_phrase, index_phrase)
    return ids

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