# 2021-slojnost-project

### preprocessing1.py

This script is transforming the word-frequency data from the FreqDists_50K folder into
letter frequencies. The preprocessing pipeline is as follows:

- Removing characters which weren't matched with the complexity database
- Removing Cyrillic and Latin scripts
- Removing languages that have data on more than one WS

This resulted in data on writing systems coming from 52 languages.
