DjangoPBX
--------------------------------------
DjangoPBX - A full-featured domain based multi-tenant PBX driven by [Django](https://www.djangoproject.com/) and [FreeSWITCH™](https://freeswitch.com).

The objective of this project is to provide a GUI wrap around FreeSWITCH™ using Django and the
Python language. To minimise the number of .lua support scripts by utilising the FreeSWITCH modules
mod_xml_curl and mod_httapi, and also provide a platform that is easy to learn and code owing to
it's use of just one programming language.

DjangoPBX basically does two things.  
1. It provides a portal for end users and device configuration.
2. It generates FreeSITCH configuration from the data you provide in the Admin interface.

## Key features
* Simple, straight forward and un-complicated.
* Use of Python leads to more robust applications through exception handling and strong types.
* Uses the proven Django Application Framework, so upgrades and database migrations are handled for you.
* Multi language, all user text is passed through the Django translation mechanism.
* Easily extended by adding new application modules.
* Full REST API provided by the Django REST Framework.

From an ITSP or end user perspective DjangoPBX provides all the facilities of a modern call handling platform.
Telephony features include:

- Multi Tenancy
- Device Provisioning
- Voicemail
- Messages and notifications by email
- Call Centres
- Call Centre Wallboards
- Conference Centres
- Music on Hold
- Call Parking
- Dynamic Call Routing
- Ring Groups
- IVR Menus
- Find Me / Follow Me
- Ability to directly edit XML in the Web UI

## Documentation

Documentation is available on the [DjangoPBX Site](https://www.djangopbx.com/static/documentation/) and can be contributed to via its own [respository](https://github.com/djangopbx/djangopbx-docs)

## Under development
This code has entered a stage of Alpha Testing.
Several test deployments have been made and testing is underway.

Installation has been scripted at [djangopbx-install.sh](https://github.com/djangopbx/djangopbx-install.sh)

## License Agreement

If you contribute code to this project, you implicitly allow your code to be distributed under the MIT license. You are also implicitly verifying that all code is your original work.

Copyright (c) 2016-2024, [The DjangoPBX authors](https://github.com/djangopbx/djangopbx/graphs/contributors) (MIT License)<br>
