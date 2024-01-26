# The Kester Weather Station

Version: beta-2.0
Previous Versions: [1](https://github.com/nkester/Kester-Weather-Station/tree/v-1.0)

### Table of Contents:  
  * [Why](#why)  
  * [High Level Diagram](#high-level-diagram)  
  * [References](#references)  
  * [The Approach](#the-approach)  
  * [The Equipment](#the-equipment)  
  * [Setting up the Raspberry Pi](#setting-up-the-raspberry-pi)  
  * [Setting up Chirpstack](#setting-up-chirpstack)  
  * [Setting up Chirpstack Gateway Bridge](#setting-up-chirpstack-gateway-bridge)  
  * [Connect the Gateway](#connect-the-gateway)  
  * [Storing and Preparing Data in PostgreSQL](#storing-and-preparing-data-in-postgresql)  
  * [Interacting with the Data](#interacting-with-the-data)  

**The following portions describe integration with Google Cloud Platform (GCP)**  

  * [Configure a Chirpstack Integration with Google Pub/Sub](#configure-a-chirpstack-integration-with-google-pubsub)  
  * [GCP References](#gcp-references)  
  * [Store Pub/Sub Messages to Google Cloud Storage](#store-chirpstack-published-messages-to-google-cloud-storage)  
  * [Store Pub/Sub Messages to Google BigQuery](#store-chirpstack-published-messages-to-google-bigquery)

## Why

...Why not? 

Through this project the kids can learn basics of sensors in the real world, wireless networks, databases, and the power of cloud technologies. At the end, they will be able to point their friends and family from around the world to a website to see how hot it is, how much rain we've gotten, the air quality, etc. near their home. 

## High Level Diagram  
  
The diagram below show, at a high level, what we want to set up. Essentially, we want to have one SEEED sensor (to start), the 8-in-1 Weather sensor, that is connected to a computer inside the house and communicates over a Long Range Wide Area Network (LoRaWAN). The sensor will connect to a LoRaWAN gateway that will convert the wireless communication into a digital, computer readable format. That will then connect to a ChirpStack server on our local Raspberry Pi computer. This ChirpStack server will feed the data recieved from the sensor into a PostgreSQL Database stored on the Raspberry Pi. The Raspberry Pi will then push that data periodically to a Google Cloud Platform (GCP) managed database (likely PostgreSQL initially for ease of use). Finally, we will create a static web-page using Quarto and Observable JS, deployed to Google Firebase to query the GCP database and chart the results.

![alt text](img/SeeedSolutionDiagram.png "Seeed Solution Diagram")  

[Return to TOC](#table-of-contents)

## References  

The following are links to resources we will use to set up the components show in the diagram above.  

  * Seeed Components:  
    * [SenseCAP S2120 8-in-1 LoRaWAN Weather Sensor](https://www.seeedstudio.com/sensecap-s2120-lorawan-8-in-1-weather-sensor-p-5436.html). This reference is the Seeed Studio page to purchase the item.  
      * [Getting Started with the SenseCAP S2120](https://wiki.seeedstudio.com/Sensor/SenseCAP/SenseCAP_LoRaWAN_Sensor/SenseCAP_S2120_8-in-1_LoRaWAN_Weather_Sensor/SenseCAP_S2120_8-in-1_LoRaWAN_Weather_Sensor_Introduction/). This reference is a technical wiki on getting started with this sensor and integrating it into the LoRaWAN network.  
    * [SenseCAP M2 Multi-Platform LoRaWAN Indoor Gateway (SX1302)](https://www.seeedstudio.com/SenseCAP-Multi-Platform-LoRaWAN-Indoor-Gateway-SX1302-EU868-p-5471.html). This reference is the Seeed Studio page to purchase the item.  
      * [Connecting SenseCAP M2 Gateway to ChirpStack](https://wiki.seeedstudio.com/Network/SenseCAP_Network/SenseCAP_M2_Multi_Platform/Tutorial/Connect-M2-Multi-Platform-Gateway-to-ChirpStack/). This reference is the technical wiki on how to connect the gateway to ChirpStack.  
  * Raspberry Pi:  
    * ChirpStack:  
      * [Main documentation](https://www.chirpstack.io/): "ChirpStack is an open-source LoRaWAN Network Server which can be used to setup LoRaWAN networks. ChripStack provides a web-interface for the management of gateways, devices, and tenants as well to setup data integrations with the major cloud providers, databases, and services commonly used for handling device data. ChirpStack provides a gRPC based API that can be used to integrate or extend ChirpStack."  
      * [Installing ChirpStack on Raspberry Pi](https://www.chirpstack.io/project/guides/raspberry-pi/) <- for version 3 or for version 4 -> [Quickstart Raspberry Pi](https://www.chirpstack.io/docs/getting-started/raspberry-pi.html)  
      * [Setting up a private LoRaWAN Sensor Network](https://forum.digikey.com/t/set-up-a-private-lorawan-sensor-network-with-machinechat-and-seeed-sensecap/18460). This includes more than what is shown on my diagram but may become useful as we go through this. I'm not sure how JEDI Pro SSE would be useful but if this can provide some basic dashboarding that we can deploy as an external website, that may be useful.  
    * Firebase:  
      * Firestore: [Interacting with Firestore from Observable from within Firebase](https://observablehq.com/@taeold/introduction-to-serverless-notebooks-firebase-edition)  
    * Quarto:  
      * Using Observable JS: [How to use Observable JS in Quarto](https://quarto.org/docs/interactive/ojs/#overview)  
      * Accessing data. You can do this in R or Python through an API call and then pass it to observable during render but this doesn't make the webpage interactive with current data. You can also call Firestore directly from observable JS which is probably the way to go. [Quarto - Data Sources](https://quarto.org/docs/interactive/ojs/data-sources.html#overview).  
      * [Google Cloud FireStore REST API documentation](https://firebase.google.com/docs/firestore/use-rest-api). This walks us through how we can query the FireStore collection via an REST API with a token.  
      * [Interacting with Data from Observable JS](https://observablehq.com/@observablehq/introduction-to-data?collection=@observablehq/notebook-fundamentals#apis)  

[Return to TOC](#table-of-contents)  

## The Approach  

I decided to take this approach rather than building our own sensors because it allows us to get a prototype up and operational quicker so we can see how the various components work. If we took the approach of building components ourselves, we would have gotten mired in figuring out how to deploy them into the environment while protecting them from corrosion, etc. These Seeed sensors do that for us and provide the networking required to make it work. In a future project I'd like to get them into buiding the circuits, etc.  

[Return to TOC](#table-of-contents)

## The Equipment  

This is the final list of equipment:  

  * Raspberry Pi 3, purchased in 2017  
    * Loaded with Ubuntu Server 22.04 LTS: We went with this so we had the full power and options of Ubuntu (as compared to Raspberry OS) while minimizing the overhead that comes with loading Ubuntu Desktop.  
    * 10 GB micro SD memory card
  * The Seeed Studio equipment  
    * SeeedStudio SenseCAP S2120 LoRaWAN 8-in-1 Weather Station ([Manual Here](./documents/SenseCAP%20S2120%20LoRaWAN%208-in-1%20Weather%20Station%20User%20Guide.pdf))  
    * SeeedStudio SenseCAP M2 LoRaWAN Indoor Gateway  
      * [M2 Quick Start](./documents/Quick%20Start%20for%20SenseCAP%20M2%20Gateway%20%26%20Sensors.pdf)
      * [Connecting the M2 to ChirpStack](./documents/Connect_M2_Multi-Platform_Gateway_to_ChirpStack.pdf)  

[Return to TOC](#table-of-contents)

## Setting up the Raspberry Pi  

The Raspberry Pi we used was originally purchased through Woot.com in 2017. I intended to use it to create an arcade game console with the kids but we weren't ready for that yet. The build comes from https://www.canakit.com/. The kit came with an SD card pre-loaded with the 2017 version of NOOBs. This did not have the option to install Ubuntu so I used the Raspberry Pi Installer, avalaible here at the [Raspberry Pi Website](https://www.raspberrypi.com/software/) and flashed the SD card with Ubuntu Server 22.04 LTS. Using this approach was helpful because it pre-loaded the login information for my WiFi network and performed some other configurations that made it easy to get started once in the Raspberry Pi.

Through the Raspberry Pi Installer we set our WiFi connection information, out hostname (`kesterweather`), our username (`kesterweather`), and our password.

Once we put the Raspberry Pi 3 kit together and started it up, we ran a standard `update` and `upgrade` before moving forward with the following code:  

```
sudo apt update

sudo apt upgrade -y
```  

At this point we were ready to start installing the required components for Chirpstack.  

[Return to TOC](#table-of-contents)  

## Setting up Chirpstack  

We used this project's companion, `1_initialplan` as well as these ChirpStack documents: [ChirpStack Ubuntu Docs](https://www.chirpstack.io/docs/getting-started/debian-ubuntu.html)  

### Install Required Libraries  

First to install the libraries required to support ChirpStack:  

```
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

```sql
-- create role for authentication
create role chirpstack with login password 'chirpstack';
```  

Then we want to create a database  
```sql
-- create database
create database chirpstack with owner chirpstack;
```


```sql
-- connect to the chirpstack database
\c chirpstack
```

The following extension to postgres supports better matching between text strings. I imagine we do this because of the messages `mosquitto` and the sensor will provide. Specifically, it deal with trigrams.  

[Documentation on pg_trm](https://www.postgresql.org/docs/current/pgtrgm.html)

```sql
---create pg_trgm extension
create extension pg_trgm;
```

Exit the `psql` tool  

```psql
\q
```  

### Install ChirpStack  

So that we can pull in and install the ChirpStack software we need to connect to its repository.  

### How Linux Software Works  

Software is stored in "repositories" or a "repo." This is like the app store where you go to download and install games. Unlike the app store, there are many repos where you can get linux software. There are the primary repos for the type of linux you are using and they are others for specific companies or developers. `ChirpStack` maintains their own so we need to point our computer to it (like its URL) so we can install software from it.  

The cool thing about this is that people make this (ChirpStack, PostgreSQL, and Ubuntu Linux) for free!

[What is a repo](https://aws.amazon.com/what-is/repo/#:~:text=A%20repository%2C%20or%20repo%2C%20is,of%20documents%20when%20developing%20software.)  

### Setting up the Repo  

Ensure we have the software required to connect to these other repositories.  

To ensure we get the correct software and don't end up downloading bad software that someone has put out there, we need to get the key for the ChirpStack repository.  

> This differs from the Chirpstack documentation because we are using `gpg` rather than `apt-key`

```
# Get the key from the trusted ubuntu key server

sudo gpg --no-default-keyring --keyring /usr/share/keyrings/chirpstack-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 1CE2AFD36DBCCA00
```  


Now add the URL to their repository to the list of repositories we check and have access to:  

```
sudo echo "deb [signed-by=/usr/share/keyrings/chirpstack-archive-keyring.gpg] https://artifacts.chirpstack.io/packages/4.x/deb stable main" | sudo tee /etc/apt/sources.list.d/chirpstack.list
```

Now that we have a new location for software, our computer needs to look at it to see what is available. We do this with:

```
sudo apt update
```  

IF the `sudo apt update` command above produces errors or you get a lot of `Ign` rather than `Get` and `Hit` responses, we may need to point back to the Google Domain Name Server. Do this with the following commands.

```
sudo cp /etc/resolv.conf etc/resolv.conf-2023-07-17
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf > /dev/null
```  

[Return to TOC](#table-of-contents)

## Setting up ChirpStack Gateway Bridge  

Finally we are to the point we can install the ChirpStack Gateway Bridge.  

Do that with:  

```
sudo apt install chirpstack-gateway-bridge
```  

### Configure

Now, to configure the bridge, we need to make a few changes. These are specified in this part of the [ChirpStack Documentation](https://www.chirpstack.io/docs/getting-started/debian-ubuntu.html#configuration).  

First, open the TOML (Tom's Obvious, Minimal Language) configuration file like this (note, we use `vim` because that is what we installed. We could use `nano` or another editor if we want to):  

```
sudo vim /etc/chirpstack-gateway-bridge/chirpstack-gateway-bridge.toml
```  

Now we want to find the `[integration.mqtt]` section for our region.  

> I do not know if we should set up our gateway as a US or EU region. I think EU but it may need to match the hardware.  

For now, I'll use the EU example.  

```toml
 # MQTT integration configuration.
  [integration.mqtt]
  # Event topic template.
  event_topic_template="eu868/gateway/{{ .GatewayID }}/event/{{ .EventType }}"

  # Command topic template.
  command_topic_template="eu868/gateway/{{ .GatewayID }}/command/#"
```  

### Start  

Now we start the ChirpStack Gateway Bridge service and enable it when the computer starts up.  

As explanation, we installed the gateway bridge but have not run the program yet. In linus, services run in the background and allow us to interact with them in various ways. If the service is not started then we will not be able to call it when we need to or it will not be actively "listening" for messages from our sensor or other systems.  

By enabling the service, that means that we want the service to automatically start each time the computer starts. This is helpful so that we don't need to remember each service that needs to always run so that we can start it again when the computer restarts.  

```
# start chirpstack-gateway-bridge
sudo systemctl start chirpstack-gateway-bridge

# start chirpstack-gateway-bridge on boot
sudo systemctl enable chirpstack-gateway-bridge
```

### Install Chirpstack

This may be confusing but at this point we need to install chirpstack. In the previous step we installed and configured the chirpstack gateway which is what allows us to connect to data services. This is the chirpstack program itself.  

```
apt install chirpstack
```

### Configuring Chirpstack

First we need to start the chirpstack service and enable it whenever the computer starts. This is similar to the gateway bridge we did previously.  

```
# start chirpstack
sudo systemctl start chirpstack

# start chirpstack on boot
sudo systemctl enable chirpstack

# We also need journalctl so we need to install systemd
#sudo apt install -y systemd
```

> A quick note on journals and logs. Computer programs produce logs of what they are doing to either help users de-bug, understand what the program is doing, or to serve as their outputs. It is useful to look at a program's logs since we aren't able to directly see what is happening inside the computer.  

Now that our ChirpStack service has started, lets see what it is doing in the output log.  

```
sudo journalctl -f -n 100 -u chirpstack
```  

These logs showed many errors where `chirpstack` tried to connect to all the regions listed. Looking into the `chirpstack` config file at `/etc/chirpstack/chirpstack.toml` all regions were enabled. I commented out all but `eu868` but this did not solve the issue. I think we will get there at the next step when we configure `chirpstack`.  

At this point we can access the Chirpstack Server at `http://localhost:8080` or from within the home network at `http://<raspberry pi IP address>:8080`  

[Return to TOC](#table-of-contents)

## Connect the Gateway  

### Provide a stable IP address  

At this point we have set up the Raspberry Pi as a server running the chirpstack network server that we can reach through the IP address assigned to the Raspberry Pi on our local area network (LAN). The issue though, is that each time the router or Raspberry Pi restarts our router's dynamic host configuration protocol (DHCP) server will assign it a new IP address. This is not useful if we want to have a stable address to access this server from. To fix this, we will assign our Raspberry Pi a static IP address.  

In this case, I chose `192.168.3.54` so I can always access my Kester Weather Station ChirpStack Network Server from within my local network at `192.168.3.54:8080`.  

### Next Steps  

The next step is to setup, configure, and connect our Seeed Studio M2 LoRaWAN Gateway to our Chirpstack Network Server. This is described in the [Seeed Studio M2 connection instructions](../documents/Connect_M2_Multi-Platform_Gateway_to_ChirpStack.pdf) located in this project.  

> Note: a similar product that seems more up-to-date and applies to version 4 of ChirpStack [Chirpstack Wiki for M2 Gateway](https://wiki.seeedstudio.com/Network/SenseCAP_Network/SenseCAP_M2_Multi_Platform/Tutorial/Connect-M2-Multi-Platform-Gateway-to-ChirpStack/)  

### Isolation  

Our intention is not to have anything from Seeed Studio reach out directly to the internet. To do this I will assign the gateway a static IP address in my LAN similar to the Raspberry Pi and block access to services for that address. This will allow it to communicate to devices within the LAN but not outside of it.  

To do this, I connect the M2 to my router. I then sign into my router, find the M2 listed in my "Connected Devices" and assign it a static IP address. To keep the devices associated with this project close, I assigned it the IP address `192.168.3.55`.  

> Note: You can connect the M2 to your router wirelessly as well. Do this by first connecting it via Ethernet and then connecting to your wireless network via the `Network` tab. **If you want to end up with a wireless connection, do this now or else you'll be required to put port blocking rules in again.**  

Next, I went into the security section of my router to the "Block Services" section. I created a new service to block, selected the M2's IP address, and blocked any service type. This blocks all ports to that device. 

After applying this block, I wanted to confirm this performed as expected. I accessed the M2 Web UI at its IP address (`192.168.3.55`), logged in with the username and password supplied on the device, and navigated to `Network` -> `Diagnostics`.   

To test the connection I tried to ping the built in network utility `sensecapmx.com` and conduct a speed test. As expected, both failed (see below).  

![alt text](img/seeedGatewayNetworkDiagnostics.png "Failed Network Diagnostics")  

### Connect the M2 Gateway to Chirpstack  

The following are useful references. The step-by-step used below is provided in the first.  
  1.  [Seeed Studio connecting to ChirpStack docs](https://wiki.seeedstudio.com/Network/SenseCAP_Network/SenseCAP_M2_Multi_Platform/Tutorial/Connect-M2-Multi-Platform-Gateway-to-ChirpStack/#11-add-gateway)  
  2. This ChirpStack [Connecting a Gateway](https://www.chirpstack.io/docs/guides/connect-gateway.html) guide  
  
 
First, log into the UI at `192.168.3.54:8080`. The chirpstack server uses port `8080` rather than the standard `80` or `443`. I'll look to change that in the future.  

At this point you should see a web user interface similar to this:  

![alt text](img/chirpstack_webui.png)  

The ChirpStack tenant is already installed as part of our previous work.  

The next step is to add a gateway. I'll call this one the `Seeed M2 Gateway`. We will need the gateway ID which we will get by logging into the gateway at `192.168.3.55`.  

Once we've created the gateway we need to add a device. Before we do that, we need to add a device profile. Give the device profile a name, the region should already be filled in based on previous work (EU868 for us), the MAC version is LoRaWAN 1.0.3, regional parameters revision is `A`, and leave the default ADR algorithm. I named it `Seeed Gateway`.  

Finally, in order to add the device, we create an application. Do this on the application tab. Simply give the application a name, I named mine `Kester Weather Station App` and create it.  

Once you have an application, you can add devices to it using the device profile you just created. I called the device `Seed Gateway M2	`.  

With the application and device created, we need to go back to the M2 web console at `192.168.3.55`, go to the `LoRa` -> `LoRa Network` tab. Put the gateway into `Packet Forwarder` mode give it the ChirpStack server IP as the Server Address then click `Save & Apply`. With this you should see a green check on both sides of the globe on the M2 web console `Status` -> `Overview` page.  Back in the ChirpStack server you should see the gateway as active now (green donut) rather than the orange donut previously.

### Configure and Connect the 8-in-1 Weather Station (S2120)  

Finally, we need to configure and connect the Weather Station to the network. Confusingly, this is done through ChirpStack, not the M2 gateway web console. This is poorly documented in the Seeed Studio documentation for both the M2 and S2120.  

First, we created a device profile for the weather station in ChirpStack. We named this device profile `Weather Station Profile` with the same settings at the M2 Gateway (Region = `EU868`, MAC Version = `LoRaWAN 1.0.3`, Regional parameters revision = `A`, ADR algorithm = `default`). Funder the `Join (OTAA/ABP)` tab, ensure the setting `Device supports OTAA` is enabled, and `Class-B` and `Class-C` are **Disabled**. The `Codec` tab is used to parse the sensor's payload (messages) into meaningful responses. While we did not find a published data model for the payload to build my own parser, we found one provided by Seeed Studios on GitHub for `The Things Network (TTN)`. We used this and it worked well. The codec is at the [TTN-Payload-Decoder](https://github.com/Seeed-Solution/TTN-Payload-Decoder/blob/master/SenseCAP_S2120_Weather_Station_Decoder.js) project in Seeed Studio's GitHub account. Finally, under the `Measurements` tab, ensure the `Automatically detect measurement keys` is selected. Save and submit all changes.  

Next, while still in the ChirpStack, navigate to the `Application` section and select the `Kester Weather Station App`. You should see the device for the M2 Gateway in the app. We want to add another device for the weather station. I called this `Weather Station`. Use the device profile you just created and use the EUI for the Weather Station (not the gateway).  

Once the device has been created in ChirpStack, we need to configure the weather station. Unfortunately, the SenseCap sensors only allow you to access their sensors via Blue Tooth through their phone application, `SenseCap Mate` (at least from what I found). After downloading the app (registration is not required), we put the app into search mode while powering up the weather station. The station should show a solid red light to indicate it is looking to connect. 

Once connected to our phone through the application, we set the frequency range (EU868), time, and application key. Get the application key from the ChirpStack device setting under `OTAA keys`. After changing anything else you want to and submitting those changes the sensor should connected to ChirpStack through the M2 Gateway. You'll know it successfully connected when the `Activation` tab in the ChirpStack device section has information about the device address and several keys. 

One additional setting we changed was to have the sensor wait to confirm the payload was received by ChirpStack before deleting the old. 

>This is the 2C + 1N Packet Policy setting in the configuration screen shot below. 

While this uses more power, it ensures the sensor confirms receipt of the reading before deleting the measurement onboard the sensor. Initially we set the measurement interval to 60 min but found that took too long and changed it to 15 min.

Below is an example of our weather station configuration completed through the `SenseCap Mate` app:  

![alt text](img/configuration_sensecapMate.png "Sensor Config")

Likewise, this is an example of a sensor measurement as shown through the `SenseCap Mate` app:  

![alt text](img/measurement_sensecapMate.png "Sensor Measurement")

### Reading the Measurements in ChirpStack  

With the codec (payload decoder) applied in ChirpStack and the weather sensor connected, we began recieving measurements logged in the `Events` tab of ChirpStack. Clicking on one of these allows you to see the parsed payload and all measurements. This is a sample parsed payload:  

![alt text](img/weatherSensorEvents.png)  

While this is neat, by default, ChirpStack only saves 10 readings. We can change this is the ChirpStack configuration but that doesn't do much good as we can't use the data through the ChirpStack interface.  

> ChirpStack assumes you're connecting it with some other capability like a cloud service provider (Google Cloud Platform, Azure, or AWS) or some other system.  

This is where the PostgreSQL server we installed previously will come in handy. ChirpStack uses this to store its application settins (users, device profiles, etc.) but it can also be integrated with PostgreSQL for data storage.  

[Return to TOC](#table-of-contents)  

## Storing and Preparing Data in PostgreSQL  

### Store Sensor Events in ChirpStack to PostgreSQL

Confusingly, the previous steps we took to configure ChirpStack with Postgres was to power the ChirpStack Server and it's configurations (users, device profiles, etc.). Now we need to setup an integration between the ChirpStack Server and PostgreSQL to store the events.

ChirpStack provides [Documentation](https://www.chirpstack.io/docs/chirpstack/integrations/postgresql.html) on how to configure the integration via ChirpStack's configuration files.  

In short, to enable the ChirpStack -> PostgreSQL integration there are two steps. First, create the required resources in postgres and second, edit the ChirpStack configuration file with the proper credentials to connect to the database.  

Connect to the postgres server with `sudo -u postgres psql` and then provide the following commands to create a role, password, and database.  

```sql
-- create role for authentication
create role chirpstack_integration with login password 'chirpstack_integration';

-- create database
create database chirpstack_integration with owner chirpstack_integration;
```
```psql
-- exit psql
\q
```

Next, open the ChirpStack configuration file with:

`sudo vim /etc/chirpstack/chirpstack.toml`  

Navigate to the bottom of the configuration to find the `[integration]` section. Add `postgresql` to the `enabled` array and add the `[integration.postgresql]` stanza.   


```toml
[integration]
  enabled=["mqtt","postgresql"]

  [integration.mqtt]
    server="tcp://localhost:1883/"
    json=true

  [integration.postgresql]
    dsn="postgres://chirpstack_integration:chirpstack_integration@localhost/chirpstack_integration?sslmode=disable"
```
Replace `chirpstack_integration:chirpstack_integration` with your selected `username:password`.

After making these changes, restart chirpstack service with `sudo systemctl restart chirpstack`.  

After some period of time (15 minutes for us) we saw some records begin to populate in this database. Chirpstack creates several tables (shown below) but our measurement data is in the `event_up` table. 

After connecting to the database with `\c chirpstack_integration` within the postgres commandline interface (`psql`), execute the commend `\dt` to list all tables. 

```
                         List of relations
 Schema |            Name            | Type  |         Owner
--------+----------------------------+-------+------------------------
 public | __diesel_schema_migrations | table | chirpstack_integration
 public | event_ack                  | table | chirpstack_integration
 public | event_integration          | table | chirpstack_integration
 public | event_join                 | table | chirpstack_integration
 public | event_location             | table | chirpstack_integration
 public | event_log                  | table | chirpstack_integration
 public | event_status               | table | chirpstack_integration
 public | event_tx_ack               | table | chirpstack_integration
 public | event_up                   | table | chirpstack_integration
(9 rows)
```

Using the `JSON` object referenced previously in the ChirpStack UI, we can see that the `time`, `data`, and `object` fields are of interest to us. We can get these with the following PostgreSQL query:  

```sql
 SELECT time, data, object FROM event_up LIMIT 1;
 ```
 ```
             time              |                               data                               |                                                          object
-------------------------------+------------------------------------------------------------------+--------------------------------------------------------------------------------------------------------------------------
 2023-09-14 04:13:13.094156+00 | \x0008010000031404f5200500000600000700000000000000000f100012ef0c | {"err": 0.0, "valid": true, "payload": "0008010000031404F5200500000600000700000000000000000F100012EF0C", "messages": []}
```  

Of note, when the `confirmed` field does not equal `t` we didn't find a payload (parsed JSON). This is likely because there was an error or the transmission did not include this type of data. An example is the one above with an empty `[]` message key. To remove those from our query we can modify it with a `WHERE` claus like below:  

```sql 
SELECT time, data, object FROM event_up WHERE confirmed = 't' LIMIT 1;
```

The resultant `object` field is a `jsonb` data type and looks like this:

```json
{
  "err": 0.0, 
  "valid": true, 
  "payload": "04640101010B003C05A00100C35E0000000000000002002A00000000278C", 
  "messages": [
    [
      {
        "Battery(%)": 100.0, 
        "gpsInterval": 86400.0, 
        "measureInterval": 3600.0, 
        "Firmware Version": "1.11", 
        "Hardware Version": "1.1"
        }
        ], 
        [
          {
            "type": "Air Temperature", 
            "measurementId": "4097", 
            "measurementValue": 19.5
            },
          {
            "type": "Air Humidity", 
            "measurementId": "4098", 
            "measurementValue": 94.0
            }, 
          {
            "type": "Light Intensity", 
            "measurementId": "4099", 
            "measurementValue": 0.0
            }, 
          {
            "type": "UV Index", 
            "measurementId": "4190", 
            "measurementValue": 0.0
            }, 
          {
            "type": "Wind Speed", 
            "measurementId": "4105", 
            "measurementValue": 0.0
            }
        ], 
        [
          {
            "type": "Wind Direction Sensor", 
            "measurementId": "4104", 
            "measurementValue": 42.0
            }, 
          {
            "type": "Rain Gauge", 
            "measurementId": "4113", 
            "measurementValue": 0.0
            }, 
          {
            "type": "Barometric Pressure", 
            "measurementId": "4101", 
            "measurementValue": 101240.0
            }
        ]
      ]
    }
```

This is great but we'd like the data to be organized in a nice rectangular manner to make it easy to query and chart.  

Here comes some PostgreSQL work to restructure the data so we can work with it.  

A few things, because the data constantly gets written to the database, we needed a way that updated regularly. Also, we wanted to limit the amount of duplicated data in the database since this lives on our RaspberryPi and thus has limited storate.  

For these reasons, we opted to codify our data transformation queries into a SQL `View`. This means the transformation will not happen until a call to the view is made and will thus  
  1) Always represent the full set of data present within the `event_up` table.  
  2) Take no additional storage space on the device.  

The downside, however, is that we will expend comutational power as we query the view. That is fine for no so we'll move on.  

### Transforming JSON into Rectangular Data in PostgreSQL  

First, here are some pertinent resources I used to develop this solution:  

  * [PostgreSQL Documentation](https://www.postgresql.org/docs/9.4/functions-json.html)  on the json parsing functions, specifically `json_populate_recordset`.  
  * [Database Stack Exchange](https://dba.stackexchange.com/questions/123053/function-json-populate-record-text-does-not-exist) description of how to make the function work.  
  * The major components of the final solution in this [Stack Overflow Response](https://stackoverflow.com/a/43914582). I found this answer to be most useful.  

The data from ChirpStack is stored as a `jsonb` data type but the various elements within the json are not specifically typed. For this reason we need to create a data type to tell PostgreSQL how to store the data elements we extract from this json.  

Each of the sensors on our weather station provide measurements in the same format of `type`, `measurementId`, and `measurementValue`. We will describe these data fields in the type with the SQL command below:

```sql
CREATE TYPE sensor AS (type text, "measurementId" text, "measurementValue" float);
```  

Now we will select elements of the `event_up` table, expand a portion of the `object` field `jsonb` object, and type them according to the `sensor` type we just created.  

As we saw in the example `json` object above, there are two arrays of measurements. We aren't sure why this is but it probably has something to do with either the weather station manufacturer or the codec we are using in Chirpstack to interpret the data.  

In addition to the expanded json object, we also want to record the time the measurement was taken. Below is the query that does this for one of those arrays.  

```sql
SELECT 
 time, 
 (jsonb_populate_recordset(null::sensor,object -> 'messages' -> 0)).* 
FROM event_up 
WHERE confirmed = 't';
```

The `->` operator is how we navigate into levels of json objects in PostgreSQL. The final `0` is the index (starting at 0) of the arrays within the `messages` object. This query returns a response like the one below:

```
             time              |      type       | measurementId | measurementValue
-------------------------------+-----------------+---------------+------------------
 2023-09-14 04:13:20.058726+00 |                 |               |
 2023-09-14 04:13:29.299782+00 |                 |               |
 2023-09-14 04:14:13.594204+00 |                 |               |
 2023-09-14 04:14:52.582875+00 |                 |               |
 2023-09-14 04:39:50.355121+00 |                 |               |
 2023-09-14 04:39:59.43616+00  |                 |               |
 2023-09-14 04:55:05.490106+00 | Air Temperature | 4097          |             19.5
 2023-09-14 04:55:05.490106+00 | Air Humidity    | 4098          |               94
 2023-09-14 04:55:05.490106+00 | Light Intensity | 4099          |              105
 2023-09-14 04:55:05.490106+00 | UV Index        | 4190          |                0
 2023-09-14 04:55:05.490106+00 | Wind Speed      | 4105          |                0
 2023-09-14 05:10:26.380747+00 | Air Temperature | 4097          |             19.3
 2023-09-14 05:10:26.380747+00 | Air Humidity    | 4098          |               95
 2023-09-14 05:10:26.380747+00 | Light Intensity | 4099          |              488
 2023-09-14 05:10:26.380747+00 | UV Index        | 4190          |                0
 2023-09-14 05:10:26.380747+00 | Wind Speed      | 4105          |                0
```


Aside from the few empty rows at the top, this is exactly what we are looking for. To confirm, we will do the same for the second array.

```sql
SELECT 
 time, 
 (jsonb_populate_recordset(null::sensor,object -> 'messages' -> 1)).* 
FROM event_up 
WHERE confirmed = 't';
```
Like the first array, this gives us the expected results:

```
             time              |         type          | measurementId | measurementValue
-------------------------------+-----------------------+---------------+------------------
 2023-09-14 04:13:20.058726+00 | Air Temperature       | 4097          |             19.5
 2023-09-14 04:13:20.058726+00 | Air Humidity          | 4098          |               94
 2023-09-14 04:13:20.058726+00 | Light Intensity       | 4099          |                0
 2023-09-14 04:13:20.058726+00 | UV Index              | 4190          |                0
 2023-09-14 04:13:20.058726+00 | Wind Speed            | 4105          |                0
 2023-09-14 04:13:29.299782+00 | Air Temperature       | 4097          |             19.5
 2023-09-14 04:13:29.299782+00 | Air Humidity          | 4098          |               94
 2023-09-14 04:13:29.299782+00 | Light Intensity       | 4099          |                0
 2023-09-14 04:13:29.299782+00 | UV Index              | 4190          |                0
 2023-09-14 04:13:29.299782+00 | Wind Speed            | 4105          |                0
 2023-09-14 04:14:13.594204+00 | Air Temperature       | 4097          |             19.5
 2023-09-14 04:14:13.594204+00 | Air Humidity          | 4098          |               94
 2023-09-14 04:14:13.594204+00 | Light Intensity       | 4099          |                0
 2023-09-14 04:14:13.594204+00 | UV Index              | 4190          |                0
 2023-09-14 04:14:13.594204+00 | Wind Speed            | 4105          |                0
 2023-09-14 04:14:52.582875+00 | Air Temperature       | 4097          |             19.5
 ```

Now, we want to combine both of these queries together into the same table for a response. The SQL operator for this is `UNION`. We do this with the following query:  

```sql
SELECT 
 time, 
 (jsonb_populate_recordset(null::sensor,object -> 'messages' -> 0)).* 
FROM event_up 
WHERE confirmed = 't'
UNION
SELECT 
 time, 
 (jsonb_populate_recordset(null::sensor,object -> 'messages' -> 1)).* 
FROM event_up 
WHERE confirmed = 't';
```

So that we don't need to write this query every time, we'll save it as a view. When we do this we'll also add order to the table with an `ORDER BY` statement for time and then type. We'll call this view `sensor_data` and create it with the following statement:

```sql
CREATE VIEW sensor_data 
 AS SELECT 
  time, 
  (jsonb_populate_recordset(null::sensor,object -> 'messages' -> 0)).* 
 FROM event_up 
 WHERE confirmed = 't'
 UNION
 SELECT 
  time, 
  (jsonb_populate_recordset(null::sensor,object -> 'messages' -> 1)).* 
 FROM event_up 
 WHERE confirmed = 't' 
 ORDER BY 
  time desc, 
  type;
```
Now we can query the view with the following command:
```sql
SELECT * FROM sensor_data;
```
and, more importantly, make modifiers to it like selecting only the `Air Temperature` measurements with:

```sql
SELECT * FROM sensor_data WHERE type = 'Air Temperature';
```  
which gives the following response:

```
             time              |      type       | measurementId | measurementValue
-------------------------------+-----------------+---------------+------------------
 2023-09-14 04:13:20.058726+00 | Air Temperature | 4097          |             19.5
 2023-09-14 04:13:29.299782+00 | Air Temperature | 4097          |             19.5
 2023-09-14 04:14:13.594204+00 | Air Temperature | 4097          |             19.5
 2023-09-14 04:14:52.582875+00 | Air Temperature | 4097          |             19.5
 2023-09-14 04:39:50.355121+00 | Air Temperature | 4097          |             19.5
 2023-09-14 04:39:59.43616+00  | Air Temperature | 4097          |             19.5
 2023-09-14 04:55:05.490106+00 | Air Temperature | 4097          |             19.5
 2023-09-14 05:10:26.380747+00 | Air Temperature | 4097          |             19.3
 2023-09-14 05:25:33.130726+00 | Air Temperature | 4097          |             19.3
 2023-09-14 05:40:39.188236+00 | Air Temperature | 4097          |             19.2
 2023-09-14 05:55:46.124893+00 | Air Temperature | 4097          |             19.6
 2023-09-14 05:56:00.464804+00 | Air Temperature | 4097          |             19.6
 2023-09-14 06:11:06.806951+00 | Air Temperature | 4097          |             19.8
 2023-09-14 06:26:13.662671+00 | Air Temperature | 4097          |             20.4
 2023-09-14 06:41:19.414583+00 | Air Temperature | 4097          |               21
 2023-09-14 06:56:25.728441+00 | Air Temperature | 4097          |             21.5
```  

Now we are ready to start interacting with the data!  

[Return to TOC](#table-of-contents)  

## Interacting with the Data  

Now that we have data formatted in the way we want it, we need to get to the data remotely with a user that has limited priviledges.  

### Configuring PostgreSQL to Accept Remote Connections

First, getting to the data...by default, PostgreSQL only allows connections coming from the `localhost`. This protects it from being accessed by other computers. To this point we've interacted with the database via the command line on our RaspberryPi.  

Here are some references I found useful. Of note, I didn't want to make the database accessible to anyone from anywhere (any IP address) so I've confined it to just IP addresses within my home network.  
  * [Good step-by-step instructions](https://tecadmin.net/postgresql-allow-remote-connections/) <-There is an issue in these instructions  
    *  [A solution to the issue](https://stackoverflow.com/a/18580598)  
  * [Explanation of a CIDR block](https://aws.amazon.com/what-is/cidr/)  
  * [Check the status of all pg services](https://dba.stackexchange.com/a/320672)

We need to change two configuration files: `postgresql.conf` and `pg_hba.conf`. 

Find where the `postgresql.conf` file is by running the following command on the RaspberryPi command line: `sudo -u postgres psql -c "SHOW config_file;"` For me, the file is located at ` /etc/postgresql/14/main/postgresql.conf`.  

Open the file with `sudo vim /etc/postgresql/14/main/postgresql.conf`, find the `listen_addresses` configuration and change it from `listen_addresses = 'localhost'` to `listen_addresses = '*'`.  

Next, open the `pg_hba.conf` file from the same directory with `sudo vim /etc/postgresql/14/main/pg_hba.conf`  

This file specifies which IP addresses are allowed to connect. Unlike the `techadmin.net` instructions above, I'm not going to specify anything from IPV6 addresses because I don't use those (the `::/0` line). Likewise, I don't want to allow any IP address to connect, which is what the `0.0.0.0/0` specification allows. Instead, I want only those addresses from within my home network to be able to connect. To do this we'll specify `192.168.3.0/24`

Our entry in the configuration file looked like this:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    all             all             192.168.3.0/24               md5
```  

Now that we have the configuration files updated we need to restart the postgres service with `sudo systemctl restart postgresql` and then check on its status with `sudo systemctl status 'postgresql*'`. The response from this should be one service `active (running)` and another `active (exited)`. 

The final step is to allow port `5432`, PostgreSQL's default port, through the Ubuntu firewall. Do this with `sudo ufw allow 5432`.  

### Create a Limited Permission User  

Before disconnecting from the RaspberryPi, we will get back into PostgreSQL to create a new user that we'll use to query the database remotely.  

Connect to PostgreSQL as normal with `sudo -u postgres psql` and then connect to the `chirpstack_integration` database with `\c chirpstack_integration`. I'll create a new role called `dataview` and give it a password authentication with:  
```sql
CREATE ROLE dataview WITH LOGIN PASSWORD '<my password>';
```  
The issue now, however, is that I created my view previously as the `postgres` role. This new user, by default, does not have permissions to these other resources. I'll change that by granting `dataview` "SELECT ON" permissions to that view with:

```sql
GRANT SELECT ON sensor_data TO dataview;
```  

Now we should be good to go.  

### Query the Database Remotely  

My analytic tool of choice is `R` so now from my personal computer I'll use `R` to query the `chirpstack_integration` database, specifically the `sensor_data` view we created.  

I connect to the database with the following script:

```R
library(RPostgreSQL)
library(DBI)

db <- 'chirpstack_integration'
host <- '192.168.3.54'
port <- '5432'
user <- 'dataview'
password <- '<dataview password>'


con <- DBI::dbConnect(drv = RPostgreSQL::PostgreSQL(),
                      dbname = db,
                      host = host,
                      port = port,
                      user = user,
                      password = password)

DBI::dbGetQuery(conn = con,
                statement = "SELECT * FROM sensor_data WHERE type = 'Air Humidity' ORDER BY time desc LIMIT 10")                      
```  

This query selects all columns from the `sensor_data` view but returns only the rows where `Air Humidity` is the `type` and it limits it to 10 responses, starting with the most recent.  

The result is:  
```
                  time         type measurementId measurementValue
1  2023-09-24 10:04:26 Air Humidity          4098               49
2  2023-09-24 09:49:20 Air Humidity          4098               45
3  2023-09-24 09:34:13 Air Humidity          4098               53
4  2023-09-24 09:19:07 Air Humidity          4098               51
5  2023-09-24 08:48:54 Air Humidity          4098               61
6  2023-09-24 08:33:48 Air Humidity          4098               60
7  2023-09-24 08:33:35 Air Humidity          4098               60
8  2023-09-24 08:18:27 Air Humidity          4098               70
9  2023-09-24 08:03:20 Air Humidity          4098               71
10 2023-09-24 07:48:14 Air Humidity          4098               75
```  

Which is what I expect. Now we can start building charts and tools!  

### Visualizing the Data  

Now that we have a local database with our data extracted into a rectangular dataset we can build tools to explore and visualize it. That work is beyond the scope of this project and is located in the projects below:  

  * `Kester Weather Visualization Site`  
    * Private: https://gitlab.com/nkester-projects/2023_kesterkids_weatherstation/kester-weather-visualization-site  
    * Public: https://github.com/nkester/Kester-Weather-Visualization-Site  

The `v-1.x` tag series of tags focus on static visualization sites built from data extracted from the local database and bound into the website. The `v-2.x` tag series focus on similar visualizations based on cloud based data which allows users to interactively query the data. The `v-1.x` approach is limited by the size of the dataset so at some point we can't include all the data we've collected. The `v-2.x` approach solves this but is less portable (I can't email the html file to you).  

Our intent is to implement new visualizations in both the `v-1.x` and `v-2.x` appraochs in the future.  

The following sections describe how we integrate cloud services into this project.  

[Return to TOC](#table-of-contents)  

## Configure a Chirpstack Integration with Google Pub/Sub  

In the previous steps we've focused on collecting, storing, and interacting with our weather station data locally. Next we are expanding out to leverage Cloud Computing solutions. Specifically, we've decided to use Google Cloud Platform.  

> Here is main [Google Cloud Platform (GCP)](https://cloud.google.com/) page.  
> Get to [GCP Console](https://console.cloud.google.com/) here to create projects, interact with GCP resources, etc.

### What is Google Pub/Sub and Why Use It?

Google Pub/Sub is a scalable cloud messaging service. It is compareable to Amazon Web Service's Simple Notification Service (SNS) and Microsoft Azure's Service Bus.  

Generally, it is a way to decouple data producers from data consumers. It is centered around topics to which data producers publish messages and that data consumers monitor for new data to consume. By doing this, if a data consumer is offline for some reason and then re-connects, it is able to consume messages it missed while offline. This is more robust than point-to-point solutions which fail if both ends (producer and consumer) are not both connected at the same time.  

> Learn more at the [Pub/Sub Google Docs Page](https://cloud.google.com/pubsub/docs/overview)  

### Set up a Google Project  

First and foremost, we must establish a project in Google Cloud Platform. This is important because all resources we create are contained within this project. I'll call my project `weather station`.  

### Configure Pub/Sub  

Create a Pub/Sub Topic at the [Gloud Pub/Sub Console](https://console.cloud.google.com/cloudpubsub). Give the topic a descriptive name, I called mine `weatherMeasures`.  

Next, in order for ChirpStack to publish messages to this topic it needs to have permissions. To do this, we will go to the [Identity and Access Management (IAM) console](https://console.cloud.google.com/iam-admin/iam) in GCP to create a service account with the specific permissions ChirpStack requires.  

Create a service account in the [Service Account console](https://console.cloud.google.com/iam-admin/serviceaccounts). I gave it the name `Chirpstack Publisher` and an explanatory description. Select `Create and Continue` and then choose a role. This role will give the service account the authority to do certain things. We only want it to publish to Pub/Sub, so I'll only add the `Pub/Sub Publisher` role.  

Confirm that the service account was properly applied to Pub/Sub by going back to that console, selecting the topic (blue box) and looking at the permissions tab to the right. There should be a portion named `Pub/Sub Publisher` that lists the service account just created in it.  

![alt text](img/pubSub_permissions.png "Pub/Sub Permissions Settings")  

### Configure the ChirpStack GCP Pub/Sub integration  

In order to set up a ChirpStack GCP Pub/Sub Integration, I had to interact through the web UI. because I couldn't find any instructions describing how to configure the integration via the CLI. The [ChirpStack documentation on GCP integration](https://www.chirpstack.io/docs/chirpstack/integrations/gcp-pub-sub.html) is not very helpful. This is how I got it to work:  

On the Web UI, navigate to the `Tenant -> Application -> Integrations -> GCP Pub/Sub`. The page should look like this:    

![alt text](img/chirpstack_webui_gcpPubsubIntegration.png "ChirpStack GCP Pub/Sub Integration")  

Create a new GCP Integration in which the "Payload encoding" is "JSON", the "GCP project ID" is that of the GCP project we just worked with in the previous step.  
>Note: Ensure this is not the name but the full ID which will likely replace spaces with `-` and have a set of numbers at the end.  

The topic name is the name you set up previously.  
>Note: Confusingly, **do not use** the topic name provided in your GCP Pub/Sub Console. This includes the project `projects/<project ID>/topics/<topic ID>`. Instead, use only the plain topic ID in the `Topic ID` column of the [GCP Pub/Sub Console](https://console.cloud.google.com/cloudpubsub/topic).  

Finally, we need the service account credentials for the `Chirpstack Publisher` principle we created in the previous section.  Within the IAM & Admin GCP Product, navigate to the [Service Account Section](https://console.cloud.google.com/iam-admin/serviceaccounts/).  

Click on the `Chirpstack Publisher` email and then the `Keys` tab. Select `Add Key` and `Create new key`. This should give an option to create a `JSON` or `P12` key, choose the `JSON` format.  

![alt text](img/service_account_key.png "Creating a new Service Account Key")  

This will download a new JSON Keyfile to your computer.  
>This is the only time this file will be generated so don't lose it.  

Copy the contents of the file as is (including the leading and trailing `{ }`) and paste it into the final section of the Chirpstack GCP Integration configuration.  

The final configuration should look something like this:

![alt text](img/chirpstack_webui_gcpPubsubIntegrationConfig.png "ChirpStack GCP Pub/Sub Integration")

At this point, each time the weather station provides a measurement. You can check that this is happening by going to the topic's `Metrics` section. You should see a spike around when each weather station measurement is recorded.  

![alt text](img/pubSub_publishedMessages.png "Metrics section")  

The way Pub/Sub works though, this only gets the data to GCP. How we need to establish a subscriber to do something with that data. If not, it is not retained and will be deleted.  

[Return to TOC](#table-of-contents)  

## GCP References

In this section I've consolidated various references I found useful when interacting with GCP references. Some are repeated in the sections I use them in. Some are only referenced here.  

### GCP Documentation  
  * [Google Docs: What is Cloud Storage](https://cloud.google.com/storage/docs/introduction)  
  * [Google Docs: What is Cloud Functions](https://cloud.google.com/functions/docs/concepts/overview)  
  * [Google Cloud Function Triggers](https://cloud.google.com/functions/docs/calling#2nd-gen-triggers)  
  * [Google Cloud Function Execution Environments (runtimes)](https://cloud.google.com/functions/docs/concepts/execution-environment)

### Function Development  
  * [Medium: GCP - Cloud Functions - Develop it the right way](https://medium.com/google-cloud/gcp-cloud-functions-develop-it-the-right-way-82e633b07756)  
  * [SO: Python Flask App Using Google Cloud Functions](https://stackoverflow.com/questions/62654837/python-flask-app-using-google-cloud-functions)  
  * [Medium: Cloud Run and Cloud Functions](https://medium.com/google-cloud/cloud-run-and-cloud-function-what-i-use-and-why-12bb5d3798e1)  
  * [GitHub: Google Cloud Functions Framework](https://github.com/GoogleCloudPlatform/functions-framework-python) and [PyPI: Google Cloud Functions Framework](https://pypi.org/project/functions-framework/)  
  * [Google Docs: Cloud Functions Best Practices](https://cloud.google.com/functions/docs/bestpractices/tips)  
  * [Medium: Multiple Paths in Cloud Function](https://medium.com/google-cloud/use-multiple-paths-in-cloud-functions-python-and-flask-fc6780e560d3)


### General  

  * [Google Blog: Microservices Architecture on Google Cloud Platform](https://cloud.google.com/blog/topics/developers-practitioners/microservices-architecture-google-cloud)  
  * [Google Blog: Serverless from the Ground Up - Part 1](https://cloud.google.com/blog/products/serverless/serverless-from-the-ground-up-building-a-simple-microservice-with-cloud-functions-part-1)  
  * [SO: Convert Pandas dataframe to JSON Lines](https://stackoverflow.com/questions/51775175/pandas-dataframe-to-jsonl-json-lines-conversion)  
  * [Flask: Quickstart](https://flask.palletsprojects.com/en/3.0.x/quickstart)  
  * [Full Stack Python: Web Server Gateway Interface (WSGI)](https://www.fullstackpython.com/wsgi-servers.html)  


### Big Query  

  * [SO: GCP Cloud Function write to BigQuery](https://stackoverflow.com/questions/60844628/gcp-cloud-function-to-write-data-to-bigquery-runs-with-success-but-data-doesnt)  
  * [SO: Pandas dataframe to JSON Lines](https://stackoverflow.com/questions/51775175/pandas-dataframe-to-jsonl-json-lines-conversion)  

[Return to TOC](#table-of-contents)  

## Store ChirpStack Published Messages to Google Cloud Storage  

The first thing I want to do with the messages published to my Pub/Sub topic is to simply store them in a Google Cloud Storage bucket. This ensures that I don't lose the data and it gives me the opportunity to learn how the GCP products work.  

I will use two GCP products: `Google Cloud Storage` and `Google Cloud Functions`. In the following sections I'll describe what each product is and then how I'm integrating them. 

### What is Google Cloud Storage  

According to the [documentation](https://cloud.google.com/storage/docs/introduction):  

>"Cloud Storage is a service for storing your objects in Google Cloud. An object is an immutable piece of data consisting of a file of any format. You store objects in containers called buckets."

So, Cloud Storage is just a place to save files and a bucket allows us to manage permissions and associate files with a specific project, etc.  

This is a link to the [GCP Cloud Storage console](https://console.cloud.google.com/storage)

### What is Google Cloud Functions

According to the [documentation](https://cloud.google.com/functions/docs/concepts/overview):  

> "Google Cloud Functions is a serverless execution environment for building and connecting cloud services."  

This is useful for me because serverless means I only pay when the function is executed rather than for maintaining a server all the time. This is also referred to as FaaS (Function as a Service).  

Google Cloud Functions are triggered through several means. The one that is applicable to this operation is the event trigger. We can configure that event to be a Pub/Sub publishing event. This means that I can write a Cloud Function that executes every time a message is published to a specific Pub/Sub topic. Here is information on [Google Cloud Function Triggers](https://cloud.google.com/functions/docs/calling#2nd-gen-triggers)  

Google Cloud Functions operate on several [runtimes](https://cloud.google.com/functions/docs/concepts/execution-environment) or programming languages. The service provides several versions of: `python`, `Go`, `Node.js`, `Java`, etc. Of those, I am most comfortable with `python` so I'll use that in all my work. 

>Note: We can use other runtimes by providing our own container image to `Cloud Run`. I could use this approach to use `R` but to reduce complexity I'll stick with the built in `python` runtime for `Cloud Functions`.  

Because I plan to use `python` as the execution environment (specifically, `python 3.12`), I need to become acquainted with the python client library with its methods and functions that allow us to provide the function with needed information and to interact with other portions of GCP.  

We can find this documentation on [PyPI: functions-framework](https://pypi.org/project/functions-framework/) and [GitHub: functions-framework](https://github.com/GoogleCloudPlatform/functions-framework-python).  

Likewise, the microservices references provided in the [General References](#gcp-references) above is useful to review.  

In the most basic sense, a Cloud Function consists of two files: `main.py` and `requiremetns.txt`. The `main.py` file contains the function and describes the means of triggering the function and the `requirements.txt` file contains the dependencies required for the function. 

### Using Google Cloud Functions to store data in Google Cloud Storage

Throughout the rest of this guide, I have stored all Google Cloud Function files in the `Cloud Functions` folder.  

As a stop gap until I learned more about the various databasing options within GCP, I created this function to simply store the data our weather station sent to the Pub/Sub topic. Without doing this, we would have lost after a few days (see the section on [What is GCP Pub/Sub](#what-is-google-pubsub-and-why-use-it)).  

This is a useful Google Docs resource: [Write event-driven functions](https://cloud.google.com/functions/docs/writing/write-event-driven-functions).  

This function is named: `weather_measurement_transformation`  

The following are the elements I wanted this function to accomplish:  

  1. Trigger on a cloud event (Published message to the `weather` topic). ChirpStack published its message in JSON format after expanding the payload using the Codec described in the ChirpStack section.  
  2. Extract the data corresponding to the following JSON keys: `["message"]["data"]`  
  3. The data is stored in two arrays within the `["object"]["messages"]` object of the previous key, both in the format of: `{"measurementId", "measurementValue", "type"}` so I want to convert both to a pandas dataframe and combine them.  
  4. Next, I want to add a new new column to this pandas dataframe with the measurment time  
  5. Finally, I want to convert the pandas dataframe to a JSON object again and store it as a file with a unique name within my Cloud Storage bucket. 

Along the way, I want to print out pertinent information to the function's logs to track its status.  

If successful, I should see a new JSON file every 15 minutes in my bucket that contains one measurement.  

[Return to TOC](#table-of-contents)  

## Store ChirpStack Published Messages to Google BigQuery

This function is named: `weather_measurement_transformation_bigquerywrite`  

Similar to the other function, I imported the python libraries: `base64`, `functions_framework`, `json`, `pandas`, and `google.cloud`.  

The elements I wanted this function to accomplish were the same as the previous function except that I wrote the results to a BigQuery table rather than a JSON file. 

In order to make this possible, I needed to properly configure BigQuery. There is a list of appropriate and useful resources for BigQuery in the [references section](#gcp-references) above.   

First, visit the [BigQuery Console](https://console.cloud.google.com/bigquery) for the project. Next, create a dataset with a Dataset ID and region. I named my dataset `weather_measures`.  

Within the dataset, create a table. When doing so, the user is required to provide a schema. With the JSON files created with the previous cloud function, you can select one of these files from your bucket, and select "Auto detect" the schema. I gave my table the name `measures`.    

Now that we have a BigQuery dataset and table set up, I can go back to the Cloud Function and provide that as a text string within the script. To save time and be more dynamic during the test, I chose to **"hard code" the ** table_id into the script. I will change this as I continue development. This table ID should take the form of `project-ID.dataset name.table name`. We can then pass the pandas dataframe along with the table ID to a `BigQuery` client object and insert the rows. To deal with errors returned from that call, we check that anything was returned and if so we assume it is an error.  

When triggered, we can check the status of the event in the `LOGS` tab of the cloud function module. We should see a print of the measurement values or "Success". If not, there will be an error. Finally, we can check the `measures` table in BigQuery by clicking on the table, clicking `QUERY`, and providing the following SQL query:  

> Note: the `table ID` below (`weather-station-ef6ca.weather_measures.measures`) is the same table ID provided to the cloud function above and is found in the `DETAILS` tab when selecting the BigQuery table.

```SQL
SELECT * FROM `weather-station-ef6ca.weather_measures.measures` LIMIT 100
```

> Note: the quotes around the table ID above are not normal single quotes (`'`) but the "Grave Accent" on the tilda (`~`) key.

[Return to TOC](#table-of-contents)  


## Store ChirpStack Published Messages in Google Firestore  

There is not a need to store this information yet a third time but an initial solution to the storage issue was to use one of Google's document (NoSQL) databases in the FireBase ecosystem called `Firestore`.  

I abandoned this approach to learn more about BigQuery but that may prove to not be the best solution for this project. For that reason, I've retained this function so I can return to it if needed.  

Similar to the other two approaches, we use the same python libraries: `base64`, `functions_framework`, `json`, `pandas`, and `google.cloud`. This approach also uses `firebase_admin`.  

The data extraction and transformation steps are the same as the previous approaches. To load the data into firestore, we create a firestore client with `google.cloud.firestore.Client` and add the records to the `messages` collection.  

One difference is the initialization of an `app` in line 8. I am not clear on what this does and need to do further research in the future.  

Through the [Firebase web console](https://console.cloud.google.com/firestore/databases) we can create, configure, and interact with the project's Firestore Databases. Each project has a `(default)` database which we will use here.  

**This may be an approach to investigate further later**

[Return to TOC](#table-of-contents)  

## Extract Data from BigQuery Based on an HTTPS Request

This function is named: `flask_function`  

Its dependent python libraries are: `flask`, `markupsafe`, `google.cloud`, and `pandas`  

In this function I wanted to create a RESTful API that would serve as the interface between my website and the big query database. In this implementation I've just created an API that provides a common response when requested. I've used `flask` to provide the option to develo a full RESTful API in the future. `flask` is a light weight python web application framework to develop APIs with.  

This API will allow my website to send requests to GCP to make specific queries of data from BigQuery. If I am unable to get Cloud Functions to access parameters as part of the API call I will create different functions for each type of data my user is allowed to request. 

  [Flask: Quickstart](https://flask.palletsprojects.com/en/3.0.x/quickstart)  

### Explanation of the Function Code  

The first thing to do is to create an app object. This is required to help determine what goes with your application.  

Then we create a route with `@app.route`. This is missleading because the route provided here does not actually work. For the same reason, I have not found a way to implement multiple end points for a single Cloud Function. This will be developed further later.  

We pass the `request` object to the `common_cloud_functions_function` and return the results from another function. This is helpful because it sets us up to be able to write and call multiple functions defined in other files or parts of the `main.py` file and imported to serve this work.  

Once the baseline is set, we move on to set up the function that will actually be providing information to the website. I have called this fuction `my_function` for now. An important aspect of these functions is that each potential response path ends with a `return` argument that includes the body, the status code, and the headers object. If not, the website may not interpret it properly.  

If an `"OPTIONS"` request method is recieved by the function, it sets the `CORS` headers and tells the requester what type of requests are allowed, etc. It responds with a `204` response which is "No Content".  

If the request method is not `"OPTIONS"`, `CORS` is enabled in the header and we run a set query on our BigQuery database. In this basic example I just return 10 light intensity measurements. I store the results of that request in the `results` object, convert that to a pandas dataframe and then convert that to a JSON object formated in a way required by my website which is running ObservableJS. Finally, I send the response with a `200` status code.  

> I need to do more testing to see if the conversions are required. I got this solution from this SO article [SO: How to convert results returned from bigquery to JSON format using Python?](https://stackoverflow.com/questions/55681206/how-to-convert-results-returned-from-bigquery-to-json-format-using-python)  





[Return to TOC](#table-of-contents)  