from setuptools import setup


def find_requirements():
    with open('requirements.txt') as f:
        required = [x.strip() for x in f.read().splitlines()]
        return [x for x in required if x.strip() and not x.strip().startswith("#")]

setup(
    name='boardroom',
    version='0.0.0',
    packages=['boardroom', 'boardroom.tests'],
    description='Observe and analyze insider trading from SEC filings.',
    url='https://github.com/cstoafer/boardroom',
    install_requires=find_requirements()
)
