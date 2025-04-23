from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="po-translator",
    version="0.1.0",
    author="Marco Meo",
    author_email="marco@meonet.ch",
    description="A tool to translate PO files using DeepL API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marco-meo/translator-django",
    packages=find_packages(),
    py_modules=["po_translator"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Localization",
    ],
    python_requires=">=3.13",
    install_requires=[
        "polib>=1.1.0",
        "deepl>=1.14.0"
    ],
    entry_points={
        "console_scripts": [
            "po-translator=po_translator:main",
        ],
    },
)
