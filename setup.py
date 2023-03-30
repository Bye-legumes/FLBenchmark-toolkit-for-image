from setuptools import setup

setup(
    name='flmedbenchmark',
    version='0.1.0',
    description='flmedbenchmark',
    author='zhilong',
    author_email='zhilong.chen@mail.mcgill.ca',
    url='https://github.com/Bye-legumes/FLBenchmark-toolkit-for-image',
    packages=['flmedbenchmark', 'flmedbenchmark.datasets', 'flmedbenchmark.logging'],
    package_dir={'flmedbenchmark': 'src'},
    install_requires=[
        'pandas>=0.25',
        'numpy>=1.18',
        'scipy',
        'Pillow',
    ],
    python_requires='>=3.6',
)
