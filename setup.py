from setuptools import setup, find_packages

from rest_framework_mvt import VERSION


def readme():
    # pylint: disable=invalid-name
    with open("README.md") as f:
        return f.read()


setup(
    author="Corteva Data Engineering",
    author_email="DL-Delta-Devs@corteva.com",
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: GIS",
    ],
    description="""
        A Django REST Framework extension for creating views that serialize model data to Google Protobuf encoded Map Box Vector Tiles via Postgres.
    """,
    include_package_data=True,
    install_requires=[
        "coreapi>=2.3",
        "django>=2.2.9",
        "djangorestframework>=3.9",
        "djangorestframework-gis>=0.14",
        "django-filter>=2.1.0",
    ],
    keywords="mvt,django,restframework,mapbox,vector,protobuf,tile,postgres",
    long_description=readme(),
    long_description_content_type="text/markdown",
    name="djangorestframework-mvt",
    packages=find_packages(include=["rest_framework_mvt*"]),
    extras_require={
        "dev": [
            "black",
            "coveralls",
            "mock",
            "pylint",
            "pytest",
            "pytest-cov",
            "sphinx",
            "sphinx_rtd_theme",
        ]
    },
    url="https://github.com/corteva/djangorestframework-mvt",
    version=VERSION,
    zip_safe=False,
    project_urls={
        "Documentation": "https://corteva.github.io/djangorestframework-mvt",
        "Source": "https://github.com/corteva/djangorestframework-mvt",
    },
)
