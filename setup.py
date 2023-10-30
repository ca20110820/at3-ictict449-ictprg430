from setuptools import find_packages, setup

setup(
    name="smartpark",
    version="0.1.0",
    packages=find_packages(),
    package_data={"smartpark": ["config/*.toml"]},
    install_requires=[
        "paho-mqtt",
        "toml"
    ],
    entry_points={
        "console_scripts": [
            "smartpark = smartpark.main:main",
        ],
    },
    python_requires=">=3.10",
)
