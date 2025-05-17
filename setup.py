from setuptools import setup, find_packages

setup(
    name="ffiec-call-reports",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "pandas>=1.3.0",
        "requests>=2.26.0",
        "beautifulsoup4>=4.9.3",
        "lxml>=4.9.0",
        "streamlit>=1.0.0",  # Optional, only needed for web interface
    ],
    author="Mayank Bambal",
    author_email="your.email@example.com",
    description="A Python library for downloading and processing FFIEC Call Reports",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ffiec_call_reports",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="ffiec, call-reports, banking, financial-data, xbrl",
    project_urls={
        "Documentation": "https://github.com/yourusername/ffiec_call_reports#readme",
        "Source": "https://github.com/yourusername/ffiec_call_reports",
        "Tracker": "https://github.com/yourusername/ffiec_call_reports/issues",
    },
) 