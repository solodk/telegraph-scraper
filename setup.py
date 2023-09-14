from setuptools import find_packages, setup


setup(
    name="telegraph-scraper",
    version="1.0.4",
    description="A Python scraper for Telegraph pages",
    author="Mykola Solodky",
    author_email="solodk.m@gmail.com",
    packages=find_packages(),
    url="https://github.com/solodk/telegraph-scraper",
    install_requires=[
        "tqdm",
        "requests"
    ],
    entry_points={
        'console_scripts': [
            'telegraph-scraper = scraper:main',
        ],
    },
    keywords="telegraph scrape image images download",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)