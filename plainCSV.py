import string
import csv

arts = {'a': '', 'an': '', 'the': ''}

def normalize(title):

    rest = []

    for word in title.split():
        if word not in arts:
            rest.append(word)

    title = ' '.join(rest)

    for punc in string.punctuation:
        title = title.replace(punc, '')

    title.replace(' ', '')

    return title.lower()
'''
fulltext = []
ebooks = []
music = []
videos = []
#titles = 0
'''
fulltext = set()
ebooks = set()
music = set()
videos = set()

with open('../../../../journals.txt', 'r') as f:

    reader = csv.reader(f, delimiter='\t')
    for record in reader:
        title = normalize(record[0])

        if record[13] == 'ebook':
            ebooks.add(title)
        elif record[13] == 'fulltext':
            fulltext.add(title)
        elif record[13] == 'audio' and 'naxos' in record[21].lower():
            music.add(title)
        elif record[13] == 'video':
            videos.add(title)
            #titles += 1

print('FullText: {}\nEbooks: {}\nMusic: {}\nVideo: {}\n'.format(len(fulltext), len(ebooks), len(music), len(videos)))