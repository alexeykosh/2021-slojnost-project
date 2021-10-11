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
	'''
	Transforming word frequencies to letter frequencies
	'''
	name = re.match(r'^(\w+)', file.split('/')[1]).group(0) # get lang name
	freq = pd.read_csv(file) # frequencies
	freq['textfile'] = freq['textfile'].astype('str') # transform words to str type
	freq['textfile'] = freq['textfile'].apply(list) # separate words into letters
	freq = freq.explode('textfile')[['textfile', 'Freq']].\
		groupby('textfile').\
		sum().sort_values(by='Freq', ascending=False).reset_index() # word frequencies to letter freq
	freq['unicode'] = freq['textfile'].apply(char_to_unicode) # get unicode pointers
	freq['Freq_rel'] = freq['Freq']/sum(freq['Freq']) # get relative frequencies
	freq['lang'] = str(name) # add language info
	freq = pd.concat([freq.set_index('unicode'), complexity],
		axis=1, sort=True).dropna(subset=['Freq']).reset_index() # concat with complexity dataset
	freq['rank'] = freq['Freq'].rank() # get frequency rank
	return freq


for filename in os.listdir('FreqDists_50K/'):
    dfs.append(convert_list_of_words('FreqDists_50K/'+filename))


res_full = pd.concat(dfs)
res_full_cl = res_full.dropna(subset=['PCComplexity'])
ref = pd.DataFrame(res_full_cl.groupby(["lang", "folder"]).size()\
	.reset_index())
langs = ref[~ref.duplicated(subset='lang', keep=False)]['lang']
langs_d = ref[ref.duplicated(subset='lang', keep=False)]['lang']
res_full_cl_no_dub = res_full_cl[res_full_cl['lang'].isin(langs)]
res_full_cl_no_dub = res_full_cl_no_dub[~res_full_cl_no_dub['folder']\
	.isin(['Cyrl', 'Latn'])]
res_full_cl_no_dub.to_csv('bentz_final.csv')

print(res_full_cl_no_dub.shape)
