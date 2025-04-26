from setuptools import setup, find_packages

setup(
    name='posthaste-cli',
    version='0.1.0',
    description='A CLI tool to upload text to a hastebin server quickly and cleanly.',
    author='PJ Hayes',
    author_email='archood2next@gmail.com',
    url='https://github.com/ArchooD2/posthaste',
    packages=find_packages(),
    install_requires=[
        'requests',
        'snaparg',
    ],
    entry_points={
        'console_scripts': [
            'posthaste=posthaste.__main__:main'
        ],
    },
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
