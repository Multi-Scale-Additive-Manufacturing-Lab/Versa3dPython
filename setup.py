import sys

from skbuild import setup

# The information here can also be placed in setup.cfg - better separation of
# logic and declaration, and simpler if you include description/version in a file.
setup(
    name="Versa3dPython",
    version="1.0.0a0",
    author="Marc Wang",
    author_email="marc.wang@uwaterloo.ca",
    description="STL Viewer",
    packages=['versalib'],
    package_dir={'': 'wrapping'},
    cmake_install_dir='wrapping/versalib',
    long_description="STL Viewer for the MSAM Lab. Still alpha phase"
)