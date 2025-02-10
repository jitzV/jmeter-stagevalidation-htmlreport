from setuptools import setup, find_packages

setup(
    name='jmeter-report',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'generate-jmeter-report=jmeter_report.report_generator:main',
        ],
    },
    author='Jithin',
    description='A tool to generate JMeter performance test reports.',
    url='https://github.com/yourusername/jmeter-report',
)
