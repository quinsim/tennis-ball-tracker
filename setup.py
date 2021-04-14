# Standard library imports
import setuptools

# Third party imports

# Local application imports

setuptools.setup(
    name="tennis-ball-tracker",
    version="0.1",
    author="Quinten Simet",
    author_email="quinsim@gmail.com",
    description="Tennis Ball Tracker",
    url="https://github.com/quinsim/tennis-ball-tracker.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7.15",
        "Operating System :: Linux",
    ],
    include_package_data=True,
    install_requires=[
        "zmq",
        "msgpack",
        "pylint",
    ],
)