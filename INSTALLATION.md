# Installation

These instructions are for Ubuntu 16.04 or later. Please use the appropriate commands for your system.

### Install MySQL

DelegatorBot Uses MySQL. In short, to install execute these commands.

```
    sudo apt-get update
    sudo apt-get install mysql-server
    mysql_secure_installation

```

For a more detailed set of instructions please read [How To Install MySQL on Ubuntu 16.04](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04)

### Setup a MySQL user and database

Create a user for your MySQL database. You will need to know the username and password for this user in order to configure DelegarorBot.
Then create a database. You will also need to know the name of this database. Running the bot for the first time will create all necessary tables.

```
CREATE USER 'newuser'@'localhost' IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES ON * . * TO 'newuser'@'localhost';

FLUSH PRIVILEGES;

CREATE DATABASE databasename;

```

### Install DelegatorBot


To install Delegator bot:

```
pip3 install delegatorbot

```

Or from source

```
git clone https://github.com/ArtoLabs/DelegatorBot.git
```

### Setup DelegatorBot

After installation it's necessary to configure the settings file. You'll need to navigate to the source files directory, so if you used pip this
should be in your site-packages folder, or the folder you cloned into. There you will find a file named `settings.py`. It is best to copy this
file to a new file with a new name. This name will be used to execute commands. The name of this file can be anything, but it's recommended you
give it the same name as your bot.

### Setting up database tables and SimpleSteem

The first time DelegatorBot runs, it will step through a series of questions meant to configure SimpleSteem, the python module that handles all the connections to the blockchain. DelegatorBot uses it's own custom settings when interacting with SimpleSteem and so these initial questions can safely be left blank. For each question simply hit the enter key and that setting will be automatically configured. This list of questions only appears the very first time you run DelegatorBot.

Similarly, the first time DelegatorBot needs to interact with the database it will create all necessary tables if they don't already exist.


