# Checking_Aeroflot_tickets_with_Selenium
I used this script to automate tracking of the subsidized tickets availability on Aeroflot site using Selenium framework. 


### How to run ###
In order to run this script I use **CentOS 7** or **8** with **Firefox** browser.

To run script copy and paste it to the file
```bash
cat > tickets_upd.py
```
For CentOS 7 setup of epel repository can be required
```bash
yum install epel-release
yum -y update
```

Install python3, pip (if not yet) and all libraries required by script
```bash
sudo yum –y install python3
sudo yum –y install python3-pip
pip3 install bs4
pip3 install selenium
```

Make script file executable in order to run it
```bash
chmod +x tickets_upd.py
```
In order for Selenium to be able to communicate with the Firefox browser – download **GeckoDriver** for your system from this [link](https://github.com/mozilla/geckodriver/releases) via browser or use wget
```bash
wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz -O geckodriver
```
Untar the driver to the folder which is already included to the PATH environment variable. To check it run ***echo $PATH***
```bash
sudo tar -xzvf geckodriver -C /usr/local/bin
```
Change to the script directory and run it providing required arguments
```bash
./tickets_upd.py 11.08.2023 20000
```
