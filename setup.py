from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name = 'twapture',
    version = '1.0',
    description = 'Capture tweets using the twitter streaming API',
    url = 'http://github.com/jterstriep/twapture',
    author = 'Jeff Terstriep',
    author_email = 'jterstriep@gmail.com',
    license='MIT',
    packages = ['twapture'],
    install_requires = [
        'tweepy',
        'pytz',
        'PyYAML',
        'objectpath',
        'unicodecsv',
        'elasticsearch',
    ],
    scripts = [
        'scripts/twapture',
        'scripts/twapture-stats',
        'scripts/twapturectl',
    ],
    include_package_data=True,
    zip_safe = False,
    )
