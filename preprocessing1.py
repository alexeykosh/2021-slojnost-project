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
	Convert the list of word frequencies to letter frequencies
	'''
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

# Concatenate frequencies from individual files
res_full = pd.concat(dfs)
# Sum frequencies by identical characters in each language
# (cause multiple files)
res_full = pd.DataFrame(res_full.groupby(['lang', 'unicode', 'textfile'])['Freq'].\
						agg({'Freq':'sum',
						 'file':'size'})).reset_index().set_index(['unicode'])
# Merge with Cognition paper dataset
res_full = res_full.merge(complexity,
	left_index=True, right_index=True).reset_index()
print(res_full.shape)
res_full['Sum_count'] = res_full['Freq'].groupby(res_full['lang']).transform('sum')
res_full['Rel_freq'] = res_full['Freq']/res_full['Sum_count']
# Remove cyrillic and latin characters
res_full = res_full[~res_full['folder'].isin(['Cyrl', 'Latn'])]
# Sum of probabilities (if language has occasional latin
# or cyrillic characters,
# we expect it to be at least 0.99, languages with smaller values are removed)
res_full['Sum_prob'] = res_full['Rel_freq'].groupby(res_full['lang']).transform('sum')
res_full = res_full[res_full['Sum_prob'] > 0.99]
# Removing outliers
i = res_full[(res_full['lang'] == 'pes') & (res_full['folder'] == 'Armn')].index
res_full = res_full.drop(i, axis=0)
# Count frequencies once again
res_full['Sum_count'] = res_full['Freq'].groupby(res_full['lang']).transform('sum')
res_full['Rel_freq'] = res_full['Freq']/res_full['Sum_count']
res_full.to_csv('final.csv')

print(res_full.shape)
