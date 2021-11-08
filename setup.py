from setuptools import setup, find_packages

with open("xcc/_version.py") as f:
    version = f.readlines()[-1].split()[-1].strip("\"'")

requirements = [
    "appdirs",
    "fire",
    "numpy",
    "pydantic[dotenv]",
    "python-dateutil",
    "requests",
]

info = {
    "description": "XCC is a Python API and CLI for the Xanadu Cloud.",
    "entry_points": {"console_scripts": ["xcc=xcc.commands:main"]},
    "install_requires": requirements,
    "license": "Apache License 2.0",
    "long_description_content_type": "text/x-rst",
    "long_description": open("README.rst").read(),
    "maintainer_email": "software@xanadu.ai",
    "maintainer": "Xanadu Inc.",
    "name": "xanadu-cloud-client",
    "packages": find_packages(where="."),
    "provides": ["xcc"],
    "url": "https://github.com/XanaduAI/xanadu-cloud-client",
    "version": version,
}

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: Apache Software License",
    "Natural Language :: English",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Scientific/Engineering :: Physics",
]

setup(classifiers=classifiers, **(info))
