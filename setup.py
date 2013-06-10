from setuptools import setup, find_packages

DESCRIPTION = "BitTorrent based deploys using BitTornado based on Twitter's Murder."

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()

VERSION = '0.1.0'

setup(
    name='swarm',
    version=VERSION,
    packages=find_packages(),
    author='Stanislav Vishnevskiy',
    author_email='stanislav@hammerandchisel.com',
    url='https://github.com/phoenixguild/swarm',
    license='MIT',
    entry_points={
        'console_scripts': [
            'swarm = swarm.cli:main',
        ],
    },
    include_package_data=True,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=[
        'docopt==0.6.1',
        'ansicolors==1.0.2',
    ],
    platforms=['any'],
    classifiers=[],
)