from setuptools import setup, find_namespace_packages

setup(
    name="mathematica-check",
    version="0.1.0",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "mcp-mathematica-check=server:main",
        ],
    },
    install_requires=[
        "mcp[cli]>=1.0.0",
    ],
) 