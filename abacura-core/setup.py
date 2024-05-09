from __future__ import annotations

from setuptools import find_packages, setup

setup(
    name="abacura",
    description="Multi-session MUD client written in Python with Textual library",
    python_requires=">3.10",
    version="0.0.13",
    packages=find_packages(),
    license="Proprietary",
    classifiers=[
        "License :: Other/Proprietary License",
    ],
    include_package_data=True,
    package_data={
        "abacura": ["css/*.css"],
    },
    install_requires=["asynctelnet~=0.2.5", "click==8.1.3", "textual>=0.35.0", "tomlkit==0.11.8", "numpy", "plotext"],
    entry_points="""
        [console_scripts]
        abacura=abacura.abacura:main
    """,
)
