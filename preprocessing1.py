import re
import os
import pandas as pd
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from collections import Counter
from hangul_utils import split_syllables

dfs = []

complexity = pd.read_csv('data_bothC-namesOK.csv', sep=',')
complexity['character'] = complexity['character'].str.strip()
complexity = complexity.set_index('character')

exceptions_l = ['arz', 'pes', 'prs', 'snd', 'urd' , 'grt', 'grc']
exceptions_s = ['Deva', 'Limb']


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


########### Parsing bible corpora ######################################


# lgs = ['Armenian', 'Cherokee', 'Coptic', 'Thai',
# 	   'Telugu', 'Syriac', 'Malayalam', 'Myanmar',
# 	   'Kannada', 'Korean', 'Amharic', 'Cherokee']

# fls = []

# for filename in os.listdir('bibles'):
# 	if any(s in filename for s in lgs):
# 		try:
# 			root = ET.fromstring(open('bibles/' + filename).read())
# 		except ParseError:
# 			print(filename)
# 		with open('texts2/' + filename.strip('.xml') + '.txt', 'w', encoding='utf-8') as out:
# 			for n in root.iter('seg'):
# 				try:
# 					out.write(n.text.strip() + '\n')
# 				except AttributeError:
# 					pass

dfs = []

for txtfile in os.listdir('texts'):
	print(txtfile)
	if txtfile not in '.DS_Store':
		with open('texts/' + txtfile, 'r') as file:
			text = file.read()
			if 'chr' in txtfile:
				text = ''.join(e for e in text if e.isalnum())
			elif 'kor' in txtfile:
				text = split_syllables(''.join(e for e in text if e.isalnum()))
			else:
				text = ''.join(e for e in text.lower() if e.isalnum())
			df = pd.DataFrame.from_dict(Counter(text), orient='index').reset_index()
			df['lang'] = txtfile[:-4]
			print(txtfile[:-4])
			dfs.append(df)

data_2 = pd.concat(dfs)
data_2.columns = ['textfile', 'Freq', 'lang']
data_2['unicode'] = data_2['textfile'].apply(char_to_unicode)
data_2 = data_2.set_index('unicode').merge(complexity,
	left_index=True, right_index=True).reset_index()
data_2 = data_2[~data_2['folder'].isin(['Cyrl', 'Latn', 'Cyrs', 'Grek'])]
data_2['Sum_count'] = data_2['Freq'].groupby(data_2['lang']).transform('sum')
data_2['Rel_freq'] = data_2['Freq']/data_2['Sum_count']

########### Bentz data #################################################


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
res_full['Sum_count'] = res_full['Freq'].groupby(res_full['lang']).transform('sum')
res_full['Rel_freq'] = res_full['Freq']/res_full['Sum_count']
# Remove cyrillic and latin characters
res_full = res_full[~res_full['folder'].isin(['Cyrl', 'Latn', 'Cyrs'])]
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
diff = list(set(res_full.folder.unique()) - set(data_2.folder.unique()))
# Making the final dataset
res_full = res_full[res_full.folder.isin(diff)]
data = pd.concat([res_full, data_2]).reset_index(drop=True)
data = data[~data.lang.isin(exceptions_l)]
data = data[~data.folder.isin(exceptions_s)]
data['Unicode'] = data['textfile'].apply(char_to_unicode)
data = data.rename(columns={"Rel_freq": "Relative_frequency",
 "compressed": "Compression",
 "folder": "ISO_script",
 'lang': 'ISO_language',
 'PCComplexity': 'Perimetric_complexity',
 'Freq': 'Frequency'})
print(data.columns)
data.reset_index(drop=True).to_csv('final.csv')
# print(data.columns)
