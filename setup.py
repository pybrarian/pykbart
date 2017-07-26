from distutils.core import setup
import setuptools

setup(
    name='pykbart',
    version='0.1.0a1',
    packages=['pykbart'],
    url='https://github.com/chill17/pykbart',
    license='MIT',
    author='Ed Hill',
    long_description='pykbart is a library for dealing with data created according to the [KBART standard](http://www.niso.org/workrooms/kbart, "Kbart page on NISO"). It should work under Python 2.7 or 3.x, and should also work for KBART Recommended Practice 1 and 2. It is mostly a convenience wrapper for reading and representing TSV files containing knowledge base data, but can also be used to modify item data in bulk or create KBART files of data from other formats.',
    author_email='hill.charles2@gmail.com',
    install_requires=['six>=1', 'unicodecsv'],
    test_suite='pykbart.test',
    description='Models, reads, and writes KBART files',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Wrapping Library',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords=['libraries', 'library holdings', 'e-resources', 'KBART',
              'Knowledge Bases']
)
