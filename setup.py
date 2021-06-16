import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geospaas_rest_api",
    version=os.getenv('GEOSPAAS_REST_API_RELEASE', '0.0.0dev'),
    author="Adrien Perrin",
    author_email="adrien.perrin@nersc.no",
    description="REST API for GeoSPaaS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nansencenter/django-geo-spaas-rest-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7',
    install_requires=[
        'django_geo_spaas',
        'django-filter',
        'djangorestframework',
        'djangorestframework-filters==1.0.0dev2',
        'markdown'
    ],
    include_package_data=True,
)
