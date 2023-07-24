import os
import json
import openai
from tqdm import tqdm
from utilities import get_data

# Load your API key from an environment variable or secret management service
openai.api_key = "YOUR-OPENAI-API-KEY"

experiments = [
    {
        'name': 'en_prompt_zero_shot',
        'lang': 'en',
        'prompt': "Write the following triples as fluent {lang} text.\n\nTriples: \"\"\"\n{triples_set}\n\"\"\"\n\nText:",
        'model': 'text-davinci-003',
        'temperature': 0,
        'maximum_length': 500,
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0,
        'triple_template': '{subject} {predicate} {object}',
        'triple_start_tag': '',
        'triple_end_tag': '',
        'triple_join_tag': '\n',
        'testset_filename': os.path.join('.', 'data', 'test', 'ga_test.xml')
    },
    {
        'name': 'en_prompt_few_shot',
        'lang': 'en',
        'prompt': "Write the following triples as fluent {lang} text.\n\nTriple 1: \"\"\"\nAdolfo_Suárez_Madrid–Barajas_Airport runwayName \"14R/32L\"\n\"\"\"\n\nText 1: 14R/32L is the runway name of Adolfo Suárez Madrid-Barajas Airport.\n##\nTriple 2: \"\"\"\nAmerican_Journal_of_Mathematics abbreviation \"Am. J. Math.\"\nAmerican_Journal_of_Mathematics firstPublicationYear 1878\nAmerican_Journal_of_Mathematics issnNumber \"1080-6377\"\n\"\"\"\nText 2: The American Journal of Mathematics was first published in 1878 and is also known by the abbreviated title of Am. J. Math. It has an ISSN number of 1080-6377.\n##\nTriples 3:{triples_set}\nText 3:",
        'model': 'text-davinci-003',
        'temperature': 0,
        'maximum_length': 500,
        'top_p': 1,
        'frequency_penalty': 0,
        'presence_penalty': 0,
        'triple_template': '{subject} {predicate} {object}',
        'triple_start_tag': '',
        'triple_end_tag': '',
        'triple_join_tag': '\n',
        'testset_filename': os.path.join('.', 'data', 'test', 'ga_test.xml')
    }
]

lang2langname = {
    'ga': 'Irish',
    'en': 'English',
    'br': 'Breton',
    'cy': 'Welsh',
    'mt': 'Maltese'
}


def get_triples_repr(triples_set, experiment_params):
  final_triples = []
  for triple in triples_set:
    subj, pred, obj = triple.split('|')
    final_triples.append(experiment_params['triple_start_tag']+experiment_params['triple_template'].format(subject=subj.strip(), predicate=pred.strip(), object=obj.strip())+experiment_params['triple_end_tag'])
  return experiment_params['triple_join_tag'].join(final_triples)


# Build the prompt using the correct triples representation and including examples if required
def build_prompt(experiment_params, sample):
    if experiment_params.get('examples') is not None and experiment_params.get('example_template') is not None:
        examples = [experiment_params['example_template'].format(triples_set=get_triples_repr(example['triples_set'], experiment_params), text=example['text']) for example in experiment_params['examples']]
        prompt = experiment_params['prompt'].format(triples_set=get_triples_repr(sample['triples_set'], experiment_params), examples=''.join(examples), lang=lang2langname[experiment_params['lang']])
    elif experiment_params.get('positive_examples') is not None and experiment_params.get('negative_examples') is not None and experiment_params.get('example_template') is not None:
        # Build positive examples text
        pos_examples = [experiment_params['example_template'].format(triples_set=get_triples_repr(example['triples_set'], experiment_params), explanation=example['explanation'], output=example['output']) for example in experiment_params['positive_examples']]
        # Build negative examples text
        neg_examples = [experiment_params['example_template'].format(triples_set=get_triples_repr(example['triples_set'], experiment_params), explanation=example['explanation'], output=example['output']) for example in experiment_params['negative_examples']]
        # Build entire prompt
        prompt = experiment_params['prompt'].format(triples_set=get_triples_repr(sample['triples_set'], experiment_params), lang=lang2langname[experiment_params['lang']], positive_examples=''.join(pos_examples), negative_examples=''.join(neg_examples))
    else:
        prompt = experiment_params['prompt'].format(triples_set=get_triples_repr(sample['triples_set'], experiment_params), lang=lang2langname[experiment_params['lang']])
    return prompt


# Send request to OpenAI APIs using the specified hyperparameters
def request_openai(experiment_params, prompt):
  while True:
    try:
       resp = openai.Completion.create(
          model=experiment_params['model'],
          prompt=prompt,
          max_tokens=experiment_params['maximum_length'],
          temperature=experiment_params['temperature'],
          top_p=experiment_params['top_p'],
          frequency_penalty=experiment_params['frequency_penalty'],
          presence_penalty=experiment_params['presence_penalty'])
       return resp, resp['choices'][0]['text']
    except Exception as e:
      print(str(e))
      print("Retrying...")


def execute_experiment(experiment_params):
  # Load the correct test set for the current experiment
  test_set = get_data(experiment_params['testset_filename'])
  print('Test set length:', len(test_set))

  results = []
  hypothesis = []
  tmp_file = 'tmp.json'
  for sample in tqdm(test_set, desc="Executing " + experiment_params['name']):
      current_prompt = build_prompt(experiment_params, sample)
      # print(current_prompt)
      # return

      response, text = request_openai(experiment_params, current_prompt)

      subquestions_responses = []
      if experiment_params.get('followup_questions') is not None:
          for q in experiment_params['followup_questions']:
              subquestions_responses.append(response)
              current_prompt += '\n' + text.replace('\n', '') + '\n' + q
              response, text = request_openai(experiment_params, current_prompt)

      pred_text = text.replace('\n', '').replace('<br>', '').strip()
      if experiment_params.get('split_condition') is not None:
          pred_text = pred_text.split(experiment_params['split_condition'])[experiment_params['answer_position']]

      results.append({
          'prompt': current_prompt,
          'triples_set': sample['triples_set'],
          'sentence': pred_text,
          'response': response,
          'subquestions_responses': subquestions_responses
      })
      hypothesis.append(pred_text)
      with open(tmp_file, 'w') as tmpfile:
          json.dump(results, tmpfile)

  # create results directory for the current experiment if it doesn't exist
  res_dir = os.path.join('.', 'results', experiment_params['name'])
  if not os.path.exists(res_dir):
      os.mkdir(res_dir)

  with open(os.path.join(res_dir, experiment_params['name'] + '_hypothesis.txt'), 'w') as hyp_file:
      hyp_file.write('\n'.join(hypothesis))

  # save the results of the experiment
  with open(os.path.join(res_dir, 'raw_{expname}.json'.format(expname=experiment_params['name'])), 'w') as res_file:
      json.dump({
          'experiment_settings': experiment_params,
          'results': results
      }, res_file)


for exp in experiments:
  execute_experiment(exp)


