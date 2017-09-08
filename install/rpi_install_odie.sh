#!/usr/bin/env bash

# This script will install automatically everything needed for Kalliope
# usage: ./rpi_install_kalliope.sh [<branch_name>]
# E.g: ./rpi_install_kalliope.sh dev
# If no branch are set, the master branch will be installed

# name of the branch to install
branch="master"

# get the branch name to install from passed arguments if exist
if [ $# -eq 0 ]
  then
    echo "No arguments supplied. Master branch will be installed"
else
    branch=$1
    echo "Selected branch name to install: ${branch}"
fi

echo "Installing python pip..."
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
echo "Installing python pip... [OK]"

# install packages
echo "Installing system packages..."
sudo apt-get update
sudo apt-get install -y git python-dev libsmpeg0 libttspico-utils libsmpeg0 \
flac dialog libffi-dev libffi-dev libssl-dev portaudio19-dev build-essential \
libssl-dev libffi-dev sox libatlas3-base mplayer libyaml-dev libpython2.7-dev pulseaudio pulseaudio-utils libav-tools \
postgresql postgresql-contrib cython swig3.0 python-pyaudio python3-pyaudio sox

# this is used to help the RPI
sudo apt-get install -y libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
sudo apt-get install -y libffi-dev python-yaml python-pycparser python-paramiko python-markupsafe apt-transport-https
echo "Installing system packages...[OK]"

echo "Cloning the project"
# clone the project
git clone https://github.com/Drea1989/Odie_robo_assistant.git
echo "Cloning the project...[OK]"

# Install the project
echo "Installing Odie..."
cd Odie
git checkout ${branch}
sudo python setup.py install
echo "Installing Odie...[OK]"

#install postgres dependency
echo  "configuring postgres dependency..."
sudo -u postgres psql
create user admin with superuser password 'secret';
create database odie owner admin;
\q
echo "configuring postgres...[OK]"