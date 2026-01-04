from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="silence-as-control",
    version="0.1.0",
    author="SemeAI",
    description="Control-layer primitive for AI systems: silence over misleading output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SemeAIPletinnya/silence-as-control",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
