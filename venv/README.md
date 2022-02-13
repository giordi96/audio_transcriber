# Socomec Virtual Environment - socomecenv
This folder contains the tool to build the Virtual Environment (VE) folder (socomecenv) to run and develop the project.
VE contains all the specific libraries required for the projects.
A list of the project required libraries can be find in _requirements.txt_.
VE local Python should be used as interpreter for this project, for example inside a code editor (e.g. Eclipse)

## Install new libraries on Virual Environment
First step to install or update libraries in the VE is to run the _venv-creator.bat_.
This will open a command shell with thw VE already activated.
Once the shell is opened, libraries will be installed in the VE using the usual _pip_ syntax.

## Update Virual Environment
In case the libraries installed at the previous point became required by the project, they must be permanently added to the VE. 

1. launch the _update_requirements.bat_ inside your project, which will update the _requirements.txt_ and recreate the VE in _venv_ folder;
2. add new files to the versioning system in order to keep track of the VE modifications and deposit them.

## Note
This document is still under development, it could be different in next revisions.