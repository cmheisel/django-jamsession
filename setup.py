from setuptools import setup, find_packages

setup(
    name = "django-jamsession",
    version = __import__("jamsession").__version__,
    author = "Chris Heisel",
    author_email = "chris@heisel.org",
    description = ("A Django reusable app providing the ability for admin "
        "users to create their own forms."),
    long_description = open("README.md").read(),
    url = "http://github.com/stephenmcd/django-forms-builder",
    zip_safe = False,
    include_package_data = True,
    packages = find_packages(),
    classifiers = [
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
    ]
)
