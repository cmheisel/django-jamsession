from setuptools import setup, find_packages

setup(
    name="django-jamsession",
    version=__import__("jamsession").__version__,
    author="Chris Heisel",
    author_email="chris@heisel.org",
    description=("A Django application that allows users to create simple datastructures, store data in them collected via forms, load it from delimited files, and display it in simple views."),
    long_description=open("README.md").read(),
    url="http://github.com/cmheisel/django-jamsession",
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ]
)
