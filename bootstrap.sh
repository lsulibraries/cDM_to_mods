#! /bin/bash

sudo apt-get update
sudo apt-get install -y libxml2-dev libxslt1-dev python-dev python3-pip python3-lxml zlib1g-dev lib32z1-dev

# install java
echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections
echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections
sudo apt-get -y install oracle-java8-installer

sudo pip install --upgrade lxml mock pytest
