import setuptools

BASE_REQUIREMENTS = []
SERVER_REQUIREMENTS = []
CLIENT_REQUIREMENTS = []

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
     name='easyschedule',
     version='0.100',
     packages=setuptools.find_packages(include=['easyschedule'], exclude=['build']),
     author="Joshua Jamison",
     author_email="joshjamison1@gmail.com",
     description="Easily schedule single or recurring sync/async tasks",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/codemation/easyschedule",
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
     python_requires='>=3.7, <4',   
     install_requires=BASE_REQUIREMENTS
 )