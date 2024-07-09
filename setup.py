from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='CircuitCruncher',
    version='0.1.0',
    description='A library for circuit post analysis analysis fro ngspice and xschem',
    author='Abdelrahman Ali',
    author_email='abdo.5.2001@gmail.com',
    url='https://github.com/abdelrahmanali15/CircuitCruncher/tree/notebook_extratesting',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache v2.0 License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
