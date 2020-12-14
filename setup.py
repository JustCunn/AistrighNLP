import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name='aistrigh-nlp',
    version='0.1.0',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    author='Justin Cunningham',
    author_email='justincunningham@patriciansecondary.com',
    url="https://github.com/JustCunn/AistrighNLP",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['aistrigh-nlp=aistrigh_nlp.aistrigh:main']
    },
    description='AistrighNLP - A collection of NLP tools for Irish',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix"
    ]
)
