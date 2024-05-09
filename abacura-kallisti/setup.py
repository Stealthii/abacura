from __future__ import annotations

from setuptools import find_packages, setup

setup(
    name="abacura_kallisti",
    description="Abacura extensions for Legends of Kallisti",
    python_requires=">3.10",
    version="0.0.4",
    packages=find_packages(),
    license="Proprietary",
    classifiers=[
        "License :: Other/Proprietary License",
    ],
    include_package_data=True,
    package_data={
        "abacura_kallisti": ["css/*.css"],
    },
    install_requires=[
        "abacura~=0.0.13",
        "pillow",
    ],
)
