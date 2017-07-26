# pykbart
pykbart is a library for dealing with data created according to the [KBART standard](http://www.niso.org/workrooms/kbart, "Kbart page on NISO"). It should work under Python 2.7 or 3.x, and should also work for KBART Recommended Practice 1 and 2. It is mostly a convenience wrapper for reading and representing TSV files containing knowledge base data, but can also be used to modify item data in bulk or create KBART files of data from other formats.

## Installation
Installation is easiest with pip.

`pip install pykbart`

You can also manually install by cloning this repository into your project and running

`python setup.py install`

## Examples
### Reading
The primary use case is reading information from a KBART file, either for analysis or moving it somewhere. To do so:
```python
from pykbart import KbartReader

with KbartReader('./my_kbart.txt') as KBART:
    for record in KBART:
        print(record.title)
```
As long as my_kbart.txt is formatted as according to KBART conventions (i.e. as a tsv with field names corresponding to KBART protocol) the above will print the title of every work.

KbartReader and KbartWriter (below) are context managers, they will take care of opening and closing your files in the appropriate ways, you just provide the path to the file.

__Note__: Reader objects are essentially generators, they go forward and not backwards. To be able to get random access and the ability to move forward and back, do something like `kbart_as_list = list(KBART)` on the above, which will read the whole file into a list. Be aware that this might incur significant memory overhead depending on the size of your file.

### Writing
You can also bulk edit items. Say for instance a vendor has changed the URL their items are housed at:
```python
from pykbart import KbartReader, KbartWriter

with KbartReader('./my_kbart.txt') as reader, KbartWriter('./new_kbart.txt') as writer:
    first_item = next(reader)
    first_item = change_url(first_item)
    writer.writeheader(first_item)
    writer.writerow(first_item)
    for item in reader:
        item = change_url(item)
        writer.writerow(item)
```
Writing the header row in this way is clunky and will be fixed soon.

### Field access
You can reference KBART fields similar to dict access:

`print(my_kbart['publication_title']) # prints 'Spam Quarterly'`

There are also convenience properties defined to make access of some common fields a bit less laborious than the KBART spec names them. All can be accessed by dot notation (`kbart.title`) and nearly all can be both read and set with the exception of compound properties like coverage_length and coverage which require calculating information.:

__coverage_length__: returns a timedelta object representing the length of coverage. You can call .days to see it expressed in days. Will calculate embargos or to present as appropriate, but may throw an IncompleteDateInformation exception if a record does not have enough information to at least infer a start and end date.

__coverage__: A pretty-printed representation of an items coverage range.

__start_date__: A textual representation of the first date in an items coverage. Corresponds to field 'date_first_issue_online'.

__end_date__: A textual representation of the last date in an items coverage. Roughly corresponds to field 'date_last_issue_online', but will print 'Present' if coverage continues to present day.

__title__: Corresponds to 'publication_title'

__url__: Corresponds to 'title_url'

__print_id__: Corresponds to 'print_identifier'

__e_id__: Corresponds to 'online_identifier'

__publisher__: Corresponds to 'publisher_name'

### Comparing Coverage
If you want to compare coverage of specific journals, say between a journals package you are considering and one you already have that has significant title overlap, you can define a way to match titles (a normalized title, issn, etc.) then use the compare_coverage method. For instance, in the below, let's assume *package_one* is a journal in a journals package I have, and *package_two* is one I'm considering.

```python
comparison = package_one.compare_coverage(package_2)
if comparison > 0:
    print('We already have better coverage.')
elif comparison < 0:
    print('Package 2 would give us lengthier coverage.')
else:
    print('The coverage is the same.')
```
