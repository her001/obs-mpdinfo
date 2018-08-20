#!/usr/bin/env python3

from mpd import MPDClient
import obspython as obs

source_name = ""
client = MPDClient()

def update_text():
	global source_name
	global client

	source = obs.obs_get_source_by_name(source_name)
	if source is not None:
		info = client.currentsong()
		text = ""
		title = info["title"]
		artist = info["artist"]
		if title != "":
			if artist != "":
				artist = artist + " - "
			text = artist + title
		else:
			text = info["file"]

		settings = obs.obs_data_create()
		obs.obs_data_set_string(settings, "text", text)
		obs.obs_source_update(source, settings)
		obs.obs_data_release(settings)

		obs.obs_source_release(source)

def refresh_pressed(props, prop):
	update_text()

def script_description():
	return "Updates a text source with info from the currently playing MPD song."

def script_update(settings):
	global source_name
	global client

	host = obs.obs_data_get_string(settings, "host")
	port = obs.obs_data_get_int(settings, "port")
	password = obs.obs_data_get_string(settings, "password")
	source_name = obs.obs_data_get_string(settings, "source")
	interval = obs.obs_data_get_int(settings, "interval")

        # TODO: Add error handling at connection
	client = MPDClient()
	if password != "":
		client.password(password)
	client.connect(host, port)

	obs.timer_remove(update_text)

	if host != "" and source_name != "":
		obs.timer_add(update_text, interval)

def script_defaults(settings):
	obs.obs_data_set_default_string(settings, "host", "localhost")
	obs.obs_data_set_default_int(settings, "port", 6600)
	obs.obs_data_set_default_int(settings, "interval", 500)

def script_properties():
	props = obs.obs_properties_create()

	obs.obs_properties_add_text(props, "host", "MPD Host Address", obs.OBS_TEXT_DEFAULT)
	obs.obs_properties_add_int(props, "port", "Port", 0, 65535, 1)
	obs.obs_properties_add_text(props, "password", "Password", obs.OBS_TEXT_PASSWORD)
	obs.obs_properties_add_int(props, "interval", "Update Interval (milliseconds)", 1, 30000, 1)

	p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
	sources = obs.obs_enum_sources()
	if sources is not None:
		for source in sources:
			source_id = obs.obs_source_get_id(source)
			if source_id == "text_gdiplus" or source_id == "text_ft2_source":
				name = obs.obs_source_get_name(source)
				obs.obs_property_list_add_string(p, name, name)

		obs.source_list_release(sources)

	obs.obs_properties_add_button(props, "refresh_button", "Refresh", refresh_pressed)

	return props
