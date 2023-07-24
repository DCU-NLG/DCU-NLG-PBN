import xml.etree.ElementTree as ET


# Load data file and put it in json format
def get_data(filepath, lang='ga'):
    tree = ET.parse(filepath)
    root = tree.getroot()

    data = []
    # Extract all entries
    for entry in root.findall('./entries/entry'):
        triples = []
        # Extract the triples associated to the current entry
        for triple in entry.find('modifiedtripleset').findall('mtriple'):
            triples.append(triple.text)

        sentences = []
        # Extract the verbalization associated to the current entry
        for lex in entry.findall('lex'):
            target = lex.text

            if lex.attrib['lang'] == lang:
                #print(lex.tag, lex.attrib)
                sentences.append(target)

        data.append({
            'triples_set': triples,  # List of triples (string)
            'sentences': sentences  # List of sentences
        })
    return data


def get_data_w_trcount(filepath, lang='ga'):
    tree = ET.parse(filepath)
    root = tree.getroot()

    data = []
    count = {}
    # Extract all entries
    for entry in root.findall('./entries/entry'):
        triples = []
        # Extract the triples associated to the current entry
        for triple in entry.find('modifiedtripleset').findall('mtriple'):
            triples.append(triple.text)

        sentences = []
        # Extract the verbalization associated to the current entry
        for lex in entry.findall('lex'):
            target = lex.text

            if lex.attrib['lang'] == lang:
                #print(lex.tag, lex.attrib)
                sentences.append(target)

        data.append({
            'triples_set': triples,  # List of triples (string)
            'sentences': sentences,  # List of sentences,
            'num_triples': len(triples)
        })
    return data
