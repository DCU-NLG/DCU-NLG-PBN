import os
from tqdm import tqdm
from os import environ

from google.cloud import translate


PROJECT_ID = environ.get("PROJECT_ID", "")
assert PROJECT_ID
PARENT = f"projects/{PROJECT_ID}"

def print_supported_languages(display_language_code: str):
    client = translate.TranslationServiceClient()

    response = client.get_supported_languages(
        parent=PARENT,
        display_language_code=display_language_code,
    )

    languages = response.languages
    print(f" Languages: {len(languages)} ".center(60, "-"))
    for language in languages:
        language_code = language.language_code
        display_name = language.display_name
        print(f"{language_code:10}{display_name}")

# print_supported_languages("en")

def translate_text(text: str, target_language_code: str) -> translate.Translation:
    client = translate.TranslationServiceClient()

    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        source_language_code="en",
        target_language_code=target_language_code,
        mime_type="text/plain"
    )

    return response.translations[0]


experiments  = ['en_prompt_zero_shot']
target_languages = ["ga", 'cy', 'mt']

for exp in experiments:
    print(exp)
    hyps = {
        'ga': [],
        'mt': [],
        'cy': []
    }
    with open(os.path.join('.', 'results', 'processed', exp+'_hypothesis_processed.txt'), 'r') as hyp_file:
        en_hyps = hyp_file.read().split('\n')
    for text in tqdm(en_hyps, desc ="Executing "+exp):
        for target_language in target_languages:
            translation = translate_text(text, target_language)
            source_language = translation.detected_language_code
            translated_text = translation.translated_text

            hyps[target_language].append(translated_text)

    for target_language in target_languages:
        with open(os.path.join('.', 'results', 'processed', exp.replace('en', target_language+'_tr') + '_hypothesis_processed.txt'), 'w') as hyp_file:
            hyp_file.write('\n'.join(hyps[target_language]))

