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


with ReaderManager('./credoBooks.txt') as r:

    oclc_nums = set()
    isbn_nums = set()
    titles = set()

    for record in r:
        try:
            oclc_nums.add(int(record['oclc_number']))
        except ValueError:
            pass
        try:
            isbn_nums.add(int(record['print_identifier']))
        except ValueError:
            pass
        titles.add(normalize(record.title))

with open('./refTitles.xls', 'r', encoding='utf-8') as f, open('./inBoth2.tsv', 'w', encoding='utf-8') as w:
    reader = csv.reader(f, delimiter='\t')
    writer = csv.writer(w, delimiter='\t')
    writer.writerow(['Title', 'OCLC Number', 'ISBN',
                     'Call Number', 'Publication Date'])
    for i in range(3):
        next(reader)

    exp = re.compile(r'\d+')

    for record in reader:
        broken = record[0].split(',')
        found = re.search(exp, broken[1])

        try:
            oclc = int(found.group())
        except ValueError:
            oclc = 0
        try:
            isbn = int(record[10])
        except ValueError:
            isbn = 0

        if oclc in oclc_nums or isbn in isbn_nums or normalize(record[4]) in titles:
            writer.writerow([record[4], oclc, isbn, record[21], record[6]])