from distutils.core import setup
import setuptools

setup(
    name='pykbart',
    version='0.1.0',
    packages=['pykbart'],
    url='https://github.com/chill17/pykbart',
    license='MIT',
    author='Ed Hill',
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
