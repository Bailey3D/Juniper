:: Adds an extra directory to the plugins search location during startup
:: use this script to add extra plugin locations (E.g. for your internal plugins)
:: Note: This is stored in the `Cached/UserConfig/user_settings.json` so will need redoing if the cache is wiped!
:: Installs Juniper to the system and runs the requirements.txt
cd "../../../"
"Binaries/Python/3.7/python.exe" "Source/Scripts/Internal/add_plugin_search_directory.py"
pause