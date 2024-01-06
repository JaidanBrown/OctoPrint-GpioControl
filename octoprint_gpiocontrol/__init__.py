# coding=utf-8
from __future__ import absolute_import, print_function
from octoprint.server import user_permission

import octoprint.plugin
import flask
#import RPi.GPIO as GPIO
from gpiozero import LED

class GpioControlPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.RestartNeedingPlugin,
):

    def __init__(self):
        self.devices = {}  # Initialize the devices dictionary
        
    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=True),
            dict(
                type="sidebar",
                custom_bindings=True,
                template="gpiocontrol_sidebar.jinja2",
                icon="map-signs",
            ),
        ]

    def get_assets(self):
        return dict(
            js=["js/gpiocontrol.js", "js/fontawesome-iconpicker.min.js"],
            css=["css/gpiocontrol.css", "css/fontawesome-iconpicker.min.css"],
        )

    def get_settings_defaults(self):
        return dict(gpio_configurations=[])

    def on_settings_save(self, data):
        super(GpioControlPlugin, self).on_settings_save(data)  # Save settings with parent method

        new_configurations = self._settings.get(["gpio_configurations"])
        updated_devices = {}

        for configuration in new_configurations:
            pin = int(configuration["pin"])

            # Check if this pin already has a device associated
            if pin in self.devices:
                # If device exists, you can update settings or recreate it
                # For simplicity, we'll just recreate it here
                self.devices[pin].close()  # Properly close the existing device

            # Create a new device for this pin
            # Replace 'LED' with the appropriate class for your device
            updated_devices[pin] = LED(pin)

            # Optionally, set the initial state of the device
            # Example: turning on/off the LED based on some configuration parameter
            if configuration.get("default_state") == "default_on":
                updated_devices[pin].on()
            elif configuration.get("default_state") == "default_off":
                updated_devices[pin].off()

        # Update the devices dictionary with the new configurations
        self.devices = updated_devices

    def on_after_startup(self):
        self.devices = {}
        for configuration in self._settings.get(["gpio_configurations"]):
            pin = int(configuration["pin"])
            # Example: creating an LED object for each pin
            self.devices[pin] = LED(pin)  # Adjust for different types of devices

    def on_api_command(self, command, data):
        pin = int(self._settings.get(["gpio_configurations"])[int(data["id"])]["pin"])
        device = self.devices.get(pin)

        if command == "turnGpioOn":
            device.on()
        elif command == "turnGpioOff":
            device.off()

    def get_update_information(self):
        return dict(
            gpiocontrol=dict(
                displayName="GPIO Control",
                displayVersion=self._plugin_version,
                type="github_release",
                user="catgiggle",
                repo="OctoPrint-GpioControl",
                current=self._plugin_version,
                stable_branch=dict(
                    name="Stable",
                    branch="master",
                    comittish=["master"],
                ),
                prerelease_branches=[
                    dict(
                        name="Prerelease",
                        branch="development",
                        comittish=["development", "master"],
                    )
                ],
                pip="https://github.com/catgiggle/OctoPrint-GpioControl/archive/{target_version}.zip",
            )
        )

__plugin_name__ = "GPIO Control"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = GpioControlPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
