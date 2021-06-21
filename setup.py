from setuptools import find_packages, setup

REQUIREMENTS = [
    "gitpython<4",
    "requests<3",
    "decleverett==0.0.0",
    "pyjackson<0.1.0",
    "click<9.0.0",
    "pyyaml<6.0.0",
    "Jinja2<4",
    "docker<6",
    "cached_property; python_version < '3.8'",
]

config = dict(
    name="ssci",
    version="0.1.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    url="https://github.com/mike0sv/ssci",
    license="",
    author="mike0sv",
    author_email="mike0sv@gmail.com",
    description="Shit&Sticks CI",
    install_requires=REQUIREMENTS,
    extras_require={},
    package_data={"ssci": ["templates/*"]},
    test_suite="pytest",
    tests_require=["pytest-runner"],
    entry_points={"console_scripts": ["ssci = ssci.cli.main:cli"]},
)

if __name__ == "__main__":
    setup(**config)
