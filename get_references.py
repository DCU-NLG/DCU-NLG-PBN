import os
from utilities import get_data

langs = ['br', 'cy', 'ga', 'mt'] # br | cy | ga | mt | ru


def save_references(references, dir_path, lang):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    max_sent = max([len(s) for s in references])
    print(lang, max_sent)
    for i in range(max_sent):
        tmp = []
        for r in references:
            if len(r) > i:
                tmp.append(r[i])
            else:
                tmp.append('')
        with open(os.path.join(dir_path, f'{lang}_reference{str(i)}'), 'w') as ref_file:
            ref_file.write('\n'.join(tmp))


for lang in langs:
    datapath = os.path.join('.', 'data', 'test', f'{lang}_test.xml')
    data = get_data(datapath, lang=lang)

    references = []
    for sample in data:
        references.append(sample['sentences'])

    save_references(references, os.path.join('.', 'data', 'references'), lang)

