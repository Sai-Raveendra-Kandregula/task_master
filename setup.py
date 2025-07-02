from setuptools import setup, find_packages

setup(
    name="task_master",  # Replace with your project name
    version="0.1.0",  # Initial version
    author="Sai Raveendra Kandregula",
    author_email="sairaveendrakandregula@gmail.com",
    description="A Brokerless Task Queue",
    long_description=open("README.md").read(),  # Ensure you have a README.md file
    long_description_content_type="text/markdown",
    url="https://github.com/Sai-Raveendra-Kandregula/task_master",  # Replace with your project's URL
    packages=find_packages(),  # Automatically find and include packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Replace with your license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Specify the minimum Python version
    install_requires=[
        # List your project's dependencies here
        "asyncio",
    ],
    # entry_points={
    #     "console_scripts": [
    #         "your_command=your_module:main_function",  # Optional CLI entry point
    #     ],
    # },
)
