from setuptools import setup, find_packages

setup(
    name="grapRag",  # Replace with your project's name
    version="0.1.0",  # Replace with your project's version
    author="Your Name",  # Replace with your name
    author_email="your_email@example.com",  # Replace with your email
    description="A short description of my project",
    long_description=open("README.md").read(),  # Make sure you have a README.md file
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_project",  # Replace with your project's URL if available
    packages=find_packages(
        where="src"
    ),  # Automatically find packages in the 'src' directory
    package_dir={"": "src"},  # Tell setuptools that packages are under 'src'
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with an appropriate license if needed
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Adjust according to your requirements
    install_requires=[  # List your project dependencies here
        # e.g., "requests>=2.25.1"
    ],
)
