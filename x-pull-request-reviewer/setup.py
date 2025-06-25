from setuptools import setup, find_packages

setup(
    name='x-pull-request-reviewer',
    version='1.0.0',
    description='Enterprise-grade, offline, LLM-powered pull request reviewer',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        # requirements.txt will be used by pip, but for PyPI-style install, list main deps here
    ],
    entry_points={
        'console_scripts': [
            'xprr_agent = xprr_agent:cli',
        ],
    },
    include_package_data=True,
    python_requires='>=3.9',
) 