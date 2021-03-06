# pymobiledevice [![GitHub license](https://img.shields.io/cran/l/devtools.svg)](LICENSE) [![Build Status](https://travis-ci.org/qtacore/pymobiledevice2.svg?branch=master)](https://travis-ci.org/qtacore/pymobiledevice2)

pymobiledevice is a cross-platform implementation of the mobiledevice library 
that talks the protocols to support iPhone®, iPod Touch®, iPad® and Apple TV® devices.


## Installation
```bash
pip install -e .
```

## Requirements
- Python 2.7
- M2Crypto
- Construct

## Usage
```python
import pymobiledevice as pm

d = pm.IDevice()

# remove
d.app_remove("com.apple.demo", "/Documents/log/log.txt")
d.app_remove("com.apple.demo", "/Documents/log/*.txt", glob=True)
d.app_remove("com.apple.demo", "/Documents/log", recursive=True)

# pull
d.app_pull("com.apple.demo", "/Documents/log", "localdir/")
d.app_pull("com.apple.demo", "/Documents/log/*.txt", "localdir/", glob=True)

# listdir
d.app_listdir("com.apple.demo", "/Documents") # output: ["log"]
d.app_listdir("com.apple.demo", "/Documents", absolute=True) # output: ["/Documents/log"]
```

## Lockdownd.py [com.apple.lockownd]

This script can be used in order to pair with the device & starts other services.
    
*/!\ Others services can only being accessed after succesful pairing.
Succesful pairing requiert the device to be unlocked and user to click on 
"Trust this device" on its phone screen.*
     

## afc.py [com.apple.afc]

This service is responsible for things such as copying music and photos. AFC Clients like iTunes 
are allowed accessing to a “jailed” or limited area of the device filesystem. Actually, AFC clients can 
only access certain files, namely those located in the Media folder.

## house_arrest.py [com.apple.mobile.house_arrest]

This service allows accessing to AppStore applications folders and their content.
In other words, by using an AFC client, a user/attacker can download the application resources and data. 
It also includes the “default preferences” file where credentials are sometimes stored. 

**Example code**

Pull file or directory

```python
from pymobiledevice import lockdown
from pymobiledevice import apps
from pymobiledevice.afc import AFCShell

ldc = lockdown.LockdownClient(udid=None) # only one device
myafc = apps.house_arrest(ldc, "--your-app-bundle-id--")

AFCShell(client=myafc).do_pull("Documents/log")

# Remove file
myafc.file_remove("/Documents/log/log.txt")

# Close session
myafc.stop_session()
```

## installation\_proxy.py [com.apple.mobile.installation\_proxy]

The installation proxy manages applications on a device. 
It allows execution of the following commands:
- List installed applications 
- List archived applications 
- ...


## mobilebackup.py & mobilebackup2.py [ com.apple.mobilebackup & com.apple.mobilebackup2 ]

Those services are used by iTunes to backup the device. 


## `diagnostics_relay.py` [com.apple.mobile.diagnostics_relay]

The diagnostic relay allows requesting iOS diagnostic information. 
The service handles the following actions: 
- [ Sleep ]Puts the device into deep sleep mode and disconnects from host. 
- [ Restart ] Restart the device and optionally show a user notification. 
- [ Shutdown ] Shutdown of the device and optionally show a user notification. 
- [ NAND, IORegistry, GasGauge, MobileGestalt ] Querry diagnostic informations.
- ...


## filerelay.py [com.apple.mobile.file_relay]

Depending of the iOS version, the file relay service may support the following commands:
    Accounts, AddressBook, AppleSupport, AppleTV, Baseband, Bluetooth, CrashReporter, CLTM 
    Caches, CoreLocation, DataAccess, DataMigrator, demod, Device-o-Matic, EmbeddedSocial, FindMyiPhone
    GameKitLogs, itunesstored, IORegUSBDevice, HFSMeta, Keyboard, Lockdown, MapsLogs, MobileAsset,
    MobileBackup, MobileCal, MobileDelete, MobileInstallation, MobileMusicPlayer, MobileNotes, NANDDebugInfo
    Network, Photos, SafeHarbor, SystemConfiguration, tmp, Ubiquity, UserDatabases, VARFS, VPN, Voicemail 
    WiFi, WirelessAutomation.

All the files returned by the iPhone are stored in clear text in a gziped CPIO archive. 


## pcapd.py [com.apple.pcapd]

Starting iOS 5, apple added a remote virtual interface (RVI) facility that allows mirroring networks trafic from an iOS device. 
On Mac OSX the virtual interface can be enabled with the rvictl command. This script allows to use this service on other systems.

## idb.py
Port of android adb tool

```bash
$ ./idb.py -u $UDID -b $BUNDLE_ID list
log
app.txt

$ ./idb.py -u $UDID -b $BUNDLE_ID rm app.txt
```

## References
- [iOS 测试利器：idb](https://cloud.tencent.com/developer/article/1004974)
