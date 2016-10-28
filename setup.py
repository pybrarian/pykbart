from distutils.core import setup
import setuptools

setup(
    name='pykbart',
    version='.01',
    packages=['pykbart'],
    url='https://github.com/chill17/pykbart',
    license='',
    author='Ed Hill',
    author_email='hill.charles2@gmail.com',
    install_requires=['six>=1', 'unicodecsv'],
    test_suite='pykbart.test',
    description='Models, reads, and writes KBART files'
)
