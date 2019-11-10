import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import open_dir  # for opening index directory
from whoosh import scoring  # used in Search section
from whoosh.query import *  # used in Search section

# Define Schema.  Defines fields to be searched.

schema = Schema(
    herb=TEXT(
        stored=True),  # Set stored=True if field should be returned in results
    other_names=TEXT,
    description=TEXT,
    effectiveness=TEXT,
    safety=TEXT,
    effect=TEXT,
    safe=TEXT,
    interact=TEXT)

# Create index directory

if not os.path.exists("index"):
    os.mkdir("index")
ix = create_in("index", schema)

# Open Directory

ix = open_dir("index")

# one of the fields was throwing an error because it was too long so expand the csv field size that can be imported
csv.field_size_limit(131072000)

# Write all the data from the csv file to the index
writer = ix.writer()

with open(r'.\medline_natmeds_extract.csv', encoding='utf8') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        writer.add_document(herb=row[1],
                            other_names=row[2],
                            description=row[3],
                            effectiveness=row[4],
                            safety=row[6],
                            effect=row[9],
                            safe=row[10],
                            interact=row[11])
writer.commit()

# Search on field in index using given search term.
with ix.searcher(weighting=scoring.BM25F) as s:
    myquery = (Term("description",
                    u"fertility"))  #which field to search on, which word
    results = s.search(myquery)
    print(len(results))
    for r in results:
        print(r, r.score)
