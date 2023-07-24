import os
import html


exps = ['en_prompt_zero_shot']

# for dirname in os.listdir(os.path.join('.', 'results')):
for dirname in exps:
    if not dirname.startswith('.') and dirname != 'processed':
        with open(os.path.join('.', 'results', dirname, dirname+'_hypothesis.txt'), 'r') as res_file:
            texts = res_file.read().split('\n')

        processed_texts = []
        for text in texts:
            text = text.replace('_', '')
            if text[0] == '"' and text[-1] == '"':
                text = text[1:len(text)-1].strip()
            processed_texts.append(html.unescape(text))

        with open(os.path.join('.', 'results', 'processed', dirname+'_hypothesis_processed.txt'), 'w') as proc_file:
            proc_file.write('\n'.join(processed_texts))


