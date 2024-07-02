import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()
    
setuptools.setup(
    name="TURCK_py",
    version="0.0.1",
    author="Jure Hudoklin",

    package_dir={"": "src"},
    packages=setuptools.find_packages('src'),
    install_requires=requirements,
    description="A python library that enables communication with TURCK I/O modules using ModbusTCP protocol.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)