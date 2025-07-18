from setuptools import setup, find_packages

setup(
    name="matlab-server",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "mcp-matlab-server=matlab_server.server:main",
        ],
    },
    install_requires=[
        "mcp[cli]>=1.0.0",
    ],
)
