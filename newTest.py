from kbart.reader import ReaderManager
import csv
import re
import string
import unicodedata
#from pprint import pprint


arts = {'a', 'an', 'the'}
def normalize(title):
    """
    Make an ugly but standard representation of titles for comparison

    Normalize and casefold unicode characters
    Take out punctuation marks, articles, and spaces

    >>>normalize('The Journal of O'donnell History!')
    >>>journalofodonnellhistory

    >>>normalize('Journal of o'Donnell History, The')
    >>>journalofodonnellhistory
    """
    title = unicodedata.normalize('NFC', title).casefold()

    for punc in string.punctuation:
        title = title.replace(punc, '')

    no_articles = [word for word in title.split() if word not in arts]
    title = ' '.join(no_articles)

    title = title.replace(' ', '')

    return title

with open('./refTitles.xls', 'r', encoding='utf-8') as f:
    reader = csv.reader(f, delimiter='\t')
    for i in range(3):
        next(reader)

    oclc_nums = set()
    isbn_nums = set()
    titles = set()

    exp = re.compile(r'\d+')

    for record in reader:
        broken = record[0].split(',')
        found = re.search(exp, broken[1])

        try:
            oclc_nums.add(int(found.group()))
        except ValueError:
            pass
        try:
            isbn_nums.add(int(record[10]))
        except ValueError:
            pass

        titles.add(normalize(record[4]))

with ReaderManager('./credoBooks.txt') as r, open('./inBoth.tsv', 'w', encoding='utf-8') as w:

    writer = csv.writer(w, delimiter='\t', lineterminator='\n')
    writer.writerow(['Title', 'ISBN', 'OCLC Number'])

    for record in r:
        try:
            oclc_num = int(record['oclc_number'])
        except ValueError:
            oclc_num = 0
        try:
            isbn = int(record['print_identifier'])
        except ValueError:
            isbn = 0

        if oclc_num in oclc_nums or isbn in isbn_nums or normalize(record.title) in titles:
            writer.writerow([record.title, record['print_identifier'], record['oclc_number']])
