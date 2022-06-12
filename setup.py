import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().splitlines()

with open("version", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="scoped-singleton",
    version=version,
    author="Ed__xu__Ed",
    author_email="m.tofu@qq.com",
    description="Easier sharing data between objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ed-XCF/scoped-singleton",
    py_modules=["scoped_singleton"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires,
    include_package_data=True,
)
