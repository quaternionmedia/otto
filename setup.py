import setuptools
from otto._version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
    'moviepy',
    'pillow',
    'gizeh',
]
setuptools.setup(
    name="otto",
    version=__version__,
    author="Quaternion Media",
    author_email="info@quaternion.media",
    description="automatic video creation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quaternionmedia/otto",
    packages=setuptools.find_packages(),
    install_requires=INSTALL_REQUIRES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
