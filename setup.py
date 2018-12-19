import setuptools


setuptools.setup(
    name='epcsunspecdemo',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'click',
        'pysunspec',
    ],
    extras_require={
        'development': [
            'gitignoreio',
        ],
    },
    entry_points={
        'console_scripts': [
            (
                'epcsunspecdemo = epcsunspecdemo.cli:cli',
            ),
        ],
    },
)
