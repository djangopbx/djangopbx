DjangoPBX
--------------------------------------
DjangoPBX - A full-featured domain based multi-tenant PBX driven by Django and FreeSWITCH.

The objective of this project is to provide a GUI wrap around FreeSWITCH using Django and the 
Python language and also code all the support scripts in Python (freeswitch-mod-python3) to 
provide a platform that is easy to learn and code owing to it's use of just one programming language.

DjangoPBX basically does two things.  
1. It provides a portal for end users and device configuration.
2. It generates FreeSITCH configuration from the data you provide in the Admin interface.

FreeSWITCH configuration can be delivered dynamically with mod-xml_curl
```xml
<configuration name="xml_curl.conf" description="cURL XML Gateway">
  <bindings>
    <binding name="example">
      <param name="gateway-url" value="http://127.0.0.1/xmlhandler/" bindings="dialplan|directory"/>
    </binding>
  </bindings>
</configuration>

```
or
semi-statically using wget (dialplan example):
```xml
<?xml version="1.0" encoding="utf-8"?>
<include>
    <X-PRE-PROCESS cmd="exec" data="wget -qO - http://127.0.0.1/xmlhandler/dialplan.xml" />
</include>
```
or
statically by writing out the XML files to the filing system.

## Key features
* Simple, straight forward and un-complicated.
* Uses the proven Django Application Framework, so upgrades and database migrations are handled for you.
* Easily extended by adding new application modules.
* Full REST API provided by the Django REST Framework.

## Under development
The code in this repository is not yet ready for download or testing.
