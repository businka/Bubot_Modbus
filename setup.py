import setuptools
from bubot_modbus.buject.OcfDevice.subtype.ModbusMaster import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='Bubot_Modbus',
    version=__version__,
    author="Razgovorov Mikhail",
    author_email="1338833@gmail.com",
    description="IoT OCF Modbus bridge",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/businka/Bubot_Modbus",
    package_dir={'': 'src'},
    package_data={
        '': ['*.md', '*.json'],
    },
    packages=setuptools.find_namespace_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
    ],
    python_requires='>=3.7',
    zip_safe=False,
    install_requires=[
        'Bubot_Core',
        'aio_modbus_client'
    ]
)
