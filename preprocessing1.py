import re
import os

import pandas as pd

dfs = []

complexity = pd.read_csv('data_bothC-namesOK.csv', sep=',')
complexity['character'] = complexity['character'].str.strip()
complexity = complexity.set_index('character')


def char_to_unicode(char):
	'''
	Convert char into respective unicode pointer
	in the same format as in Helena's and Olivier's
	database
	'''
	code = hex(ord(char)).upper()[2:]
	return ('0'*(5-len(code)) + code).strip()


def convert_list_of_words(file):
	name = re.match(r'^(\w+)', file.split('/')[1]).group(0)
	freq = pd.read_csv(file)
	freq['textfile'] = freq['textfile'].astype('str')
	freq['textfile'] = freq['textfile'].apply(list)
	freq = freq.explode('textfile')[['textfile', 'Freq']].\
	groupby('textfile').\
	sum().sort_values(by='Freq', ascending=False).reset_index()
	freq['unicode'] = freq['textfile'].apply(char_to_unicode)
	freq['lang'] = str(name)
	freq['file'] = file
	return freq


exceptions = ['eng-x-bible-scriptures.csv']

for filename in os.listdir('FreqDists_50K/'):
	if filename not in exceptions:
		dfs.append(convert_list_of_words('FreqDists_50K/'+filename))

res_full = pd.concat(dfs)
res_full['Sum_count'] = res_full['Freq'].\
groupby(res_full['lang']).transform('sum')
res_full['Rel_freq'] = res_full['Freq']/res_full['Sum_count']
res_full = pd.DataFrame(pd.DataFrame(res_full.\
	groupby(['lang', 'unicode', 'textfile'])[['Freq']].\
	sum()).reset_index()).set_index(['unicode'])
res_full = res_full.merge(complexity,
	left_index=True, right_index=True).reset_index()
res_full_cl = res_full[~res_full['folder'].isin(['Cyrl', 'Latn'])]
res_full_cl = res_full_cl.dropna(subset=['PCComplexity'])
res_full_cl.to_csv('bentz_final.csv')

print(res_full_cl.shape)
