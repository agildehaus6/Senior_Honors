from setuptools import setup

setup(
    name='predict_app',
    packages=['predict_app'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)