# 2_configuring

This project uses the references and plan put forward in the `1_initialplan` project and documents our implementation.  

## The Equipment  

This is the final list of equipment:  

  * Raspberry Pi 3, purchased in 2017  
    * Loaded with Ubuntu Server 22.04 LTS: We went with this so we had the full power and options of Ubuntu (as compared to Raspberry OS) while minimizing the overhead that comes with loading Ubuntu Desktop.  
    * 10 GB micro SD memory card
  * The Seeed Studio equipment **To be added**  

## Setting up the Raspberry Pi  

The Raspberry Pi we used was originally purchased through Woot.com in 2017. I intended to use it to create an arcade game console with the kids but we weren't ready for that yet. The build comes from https://www.canakit.com/. The kit came with an SD card pre-loaded with the 2017 version of NOOBs. This did not have the option to install Ubuntu so I used the Raspberry Pi Installer, avalaible here at the [Raspberry Pi Website](https://www.raspberrypi.com/software/) and flashed the SD card with Ubuntu Server 22.04 LTS. Using this approach was helpful because it pre-loaded the login information for my WiFi network and performed some other configurations that made it easy to get started once in the Raspberry Pi.

Through the Raspberry Pi Installer we set our WiFi connection information, out hostname (`kesterweather`), our username (`kesterweather`), and our password.

Once we put the Raspberry Pi 3 kit together and started it up, we ran a standard `update` and `upgrade` before moving forward with the following code:  

```{bash}
sudo apt update

sudo apt upgrade -y
```  

At this point we were ready to start installing the required components for Chirpstack.  

## Setting up Chirpstack  

We used this project's companion, `1_initialplan` as well as these ChirpStack documents: [ChirpStack Ubuntu Docs](https://www.chirpstack.io/docs/getting-started/debian-ubuntu.html)  

### Install Required Libraries  

First to install the libraries required to support ChirpStack:  

```{bash}
sudo apt install -y \
    mosquitto \
    mosquitto-clients \
    redis-server \
    redis-tools \
    postgresql 
```  

### What are these things??

  *[Mosquitto](https://www.eginnovations.com/documentation/Mosquitto-MQTT/What-is-Mosquitto-MQTT.htm#:~:text=Eclipse%20Mosquitto%20is%20an%20open,board%20computers%20to%20full%20servers.): is a message broker the implements the MQTT protocol. This allows us to use a publish/subscribe mode (pub/sub). This allows things to send messages to each other as needed. In this example our weather station is able to publish messages every time it has new readings. That will be however often we tell it to. They are organized like this:  
    * Publisher: The device that sends messages (our weather station)  
    * Messages: This is the information that the devices are sending to each other
    * Topics: These are the categories of information. For instance, there may be (I'm not sure yet) a topic for each type of sensor on our weather station. One topic for temperature, one for wind speed, one for wind direction, etc.  
    * Broker: This is the system that receives the messages and sends them on to the subscribers subscribed to that topic. This is probably our Raspberry Pi. More precisely it is probably the `Mosquitto` program on the Raspberry Pi.  
  * [Redis Server](https://backendless.com/redis-what-it-is-what-it-does-and-why-you-should-care/#:~:text=Redis%20is%20an%20open%20source,transactions%20and%20publish%2Fsubscribe%20messaging): is a database or message broker for publish/subscribe messaging (pub/sub). It is used, normally, to temporarily store data. It is good because it is very fast because it holds everything in memory. 
  * [Postres](https://www.postgresql.org/about/): PostgreSQL is a powerful relational database used to easily store very large volumes of data.  
    * What is a [relational database](https://aws.amazon.com/relational-database/#:~:text=A%20relational%20database%20is%20a,be%20represented%20in%20the%20database.)? They are a group of tables (rows and columns) of data that each store a certain type of information but can also be related to each other and combined to get more information. 

### Setting up PostgreSQL  

This will configure our `postgres` server (*note*: we refer to PostgreSQL as either PostgreSQL or postgres).  

First, start PostgreSQL (CLI tool is `psql`) as the default user `postgres`  

```
sudo -u postgres psql
```  

Now we want to create a role for chirpstack 

```{sql}
-- create role for authentication
create role chirpstack with login password 'chirpstack';
```  

Then we want to create a database  
```{sql}
-- create database
create database chirpstack with owner chirpstack;
```


```{sql}
-- connect to the chirpstack database
\c chirpstack
```

The following extension to postgres supports better matching between text strings. I imagine we do this because of the messages `mosquitto` and the sensor will provide. Specifically, it deal with trigrams.  

[Documentation on pg_trm](https://www.postgresql.org/docs/current/pgtrgm.html)

```{sql}
---create pg_trgm extension
create extension pg_trgm;
```

Exit the `psql` tool  

```{sql}
\q
```