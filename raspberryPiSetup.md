# Raspberry Pi software set-up and WiFi dongle drivers install


This write up is to get you started on setting up the raspberry pi with kali OS and the drivers installed.

HARDWARE REQUIREMENTS
--------------

Raspberry Pi (a pi 3 and above is recommended. Will discuss later on)

RC car chassis or your preferred method of transporting the pi

External WiFi dongle (you will need a dongle that can be in monitor mode and send injection packets). Here is a [link](https://deviwiki.com/wiki/List_of_Wireless_Adapters_That_Support_Monitor_Mode_and_Packet_Injection) to find out what WiFi dongles can perform such tasks.
The dongle we used for this project is [BrosTrend](https://www.amazon.com/BrosTrend-1200Mbps-Adapter-Wireless-Antennas/dp/B01IEU7UZ0/ref=sr_1_4?crid=2WD555C8HO8JW&dib=eyJ2IjoiMSJ9.1RoOXZhpDLoXglp84TKBjMLZp32RpUamYpqU2VyewkskX6mXvPThqx0m4pL0htVhNbWWFNdMGxBoK8JHjfI6ttLL4SKViS-8g81BMIlQj32yRy16E2kbQfMUDM5XTSi-ntL8PlwaEuCtOEBiMDPE3MhnkTJERtLQ-8JDu-IoeSOQNNvmQfHea_0xEW_ONEXQXQVpaQf39AO717a2q2gm3z0YK0CGOO6xZsCJaH_B_Bc.wwgo9_5NtiZUto06pyx-BAbdnaAS6XhLhGhmX5AJVb8&dib_tag=se&keywords=brostrend+wifi+adapter&qid=1708889102&sprefix=brostrend+%2Caps%2C133&sr=8-4)

Power bank (anything that is relatively smart that can have multiple out-puts)
We are using the [ANKER](https://www.amazon.com/Delivery-PowerCore-Nintendo-Official-13400mAh-Portable/dp/B07DMFL3SJ/ref=cm_cr_arp_d_pb_opt?ie=UTF8&th=1) This power bank is discontinued on Amazon, but something similar is fine.

SOFTWARE REQUIREMENTS
--------------------

Raspberry Kali OS

Aircrack-ng

Drivers for the WiFi dongle (The drivers will be listed in the instructions manual when you receive the device.) If you are unable to see them, google the name of the device with "driver install" for help getting the driver.


THE STEPS INCLUDE
======

**RASPBERRY PI IMAGER:**

* The simplest way to install the OS is to download the [raspberry pi imager](https://www.raspberrypi.com/software/)
Once installed and the window is open you should see something like this. ![image](https://github.com/RCAttack/byteBuggy/assets/112519100/9aa846d8-c07d-47d3-a5bf-89a296224906)
* Insert a blank SD card into your computer above 8Gb.

**CHOOSE YOUR DEVICE:**

* Choose a device you are using. We went with the Raspberry pi 4 4Gb ram, but a raspberry pi 3 or above will work.
You should see this on your page when you click on CHOOSE DEVICE. ![image](https://github.com/RCAttack/byteBuggy/assets/112519100/1e6e04ef-b168-4836-887d-430eb786092a)

**CHOOSING THE OPERATING SYSTEM:**

* Choose your operating system. Navigate to CHOOSE OS. ![image](https://github.com/RCAttack/byteBuggy/assets/112519100/26d22924-b172-42a6-a754-782a8f5fbf5d)
* Scroll down to other specific purpose OS ![image](https://github.com/RCAttack/byteBuggy/assets/112519100/3c997ce7-94ef-4161-bab0-b820a1f2e134)
* Then on the Kali image we went with the 64bit version as it will handle more data. This is the reason why we recommend a pi 3 or above. ![image](https://github.com/RCAttack/byteBuggy/assets/112519100/30ac7a3b-3fd1-4470-bfb2-6a0b629c4764)

**YOUR STORAGE:**

* Lastly the SD card you inserted after installing the raspberry pi imager should show up when you click on CHOOSE STORAGE.
* Let it flash the image onto your SD card. Once finished, it will prompt that it has completed flashing and you may remove your SD card.
* install the SD card to your pi and provide power with an HDMI out-put.

The Amazon links are not affiliates. We recive no proceeds.

KALI OS SET-UP
======

On first boot you should see the kernel loading then restarting. Then the Kali OS will appear like so. Type `kali` for the username and `kali` for the password.

![image](https://github.com/RCAttack/byteBuggy/assets/112519100/2d1b0c67-efcb-402f-b6a7-b7778f0249d0)

You now have access to the Kali OS!

![image](https://github.com/RCAttack/byteBuggy/assets/112519100/e9ca1b01-e710-47fa-b79d-13e35768872f)

**CONNECTING TO A WIFI NETWORK:**

On the top right screen you will see a network icon click it and this window will pop up.
![image](https://github.com/RCAttack/byteBuggy/assets/112519100/391f4ffe-e075-47a8-854e-473fb8e4ce55)

Click on available networks and type in your WiFi credentials.

**UPDATING KALI:**

Ensuring your newly installed Kali OS is up to date so that new downloaded files don't have missing dependencies.
  Navigate to the command line on the top left corner next to firefox (black box).
 
```
sudo apt update
```
Reboot when the update is completed.

```
reboot
```

**CHANGING PASSWORD:**

It is highly recommended that you change your password. Change '<userName>' to the username you have.

```
sudo passwd <userName>
```

Enter the password you would like to use ( you won't be able to see your password as you type it, but it will ask you to retype it).


**ENSURING YOU HAVE SSH ENABLED:**

To install ssh in kali.

```
sudo apt install ssh
```

  * Enabling ssh and automatic user login
    
    ```
    sudo raspi-config
    ```
  * Navigate to interface options
  * ssh
  * yes
  * Navigate to Boot / Auto Login
  * Desktop autologin
  * put in the information if you have then save
  * Go to console auto login and do the same as desktop (I am not sure if this step is necessary, but I did it anyway)
  * Exit
  * then reboot


**DOWNLOADING YOUR WIFI DRIVER:**

* As stated above, the manufacturer should have instructions on downloading the drivers.
* If it is not clear, then google the `name` of the WiFi dongle with `linux driver install` in the search bar.
* Our driver is [link](https://linux.brostrend.com/)

SETTING STATIC IP
======

**ip ADDRESS for the pi and your router:**

```
ip r | grep default
```

The squared text is the static router ip and domain_name_servers, 'eth0' is the interface, '10.0.2.15' is the pi's ip address. All of this information needs to be saved, take a photo or copy and paste it to your liking.

![image](https://github.com/RCAttack/byteBuggy/assets/112519100/4fe01633-08e2-4c0b-b1b2-831e5e30e34d)

In the home directory type

```
sudo nano /etc/dhcpcd.conf
```

Once in nano type
for [cidr-suffix] people normally put 24 in that block I am not sure why but that seems like it is the convention.

```
interface [interface-name]
static ip_address=[ip-address]/[cidr-suffix]
static routers=[router-ip-address]
static domain_name_servers=[dns-address]
```

![image](https://github.com/RCAttack/byteBuggy/assets/112519100/8ed2bdac-94d2-4485-8215-769138758d94)


you will need to save the `ip-address` number in order to ssh into your pi.


SSH INTO THE PI LINUX
======

Open your laptop terminal if on linux

type in your terminal. <ip-address> is the ip-address you have saved from earlier

```
sudo kali@<ip-address>
```

enter your PC's password

then the raspberry pi password



SSH INTO THE PI WINDOWS
======

**WITH PUTTY:**

Download [Putty](https://www.putty.org/) if not installed already

Open Putty

![image](https://github.com/RCAttack/byteBuggy/assets/112519100/e1819f28-fe67-4ea0-a0dd-56222fd84ee3)


Under Host Name (or IP address), enter your Raspberry Pi’s IP address or hostname.

Under Connection type, select SSH.

Select Open, and enter your username and password.

**WITH POWERSHELL:**

In the Windows search bar type PowerShell

Enter the same steps as in the linux terminal



























