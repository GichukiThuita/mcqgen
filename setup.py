from setuptools import find_packages, setup

setup(
    name='mcqgenerator',
    version='0.0.1',
    author='Gichuki Thuita',
    author_email='timorithy21@gmail.com',
    install_requires=["openai", "langchain", "langchain-openai", "streamlit", "python-dotenv", "pypdf"],
    packages=find_packages()
)