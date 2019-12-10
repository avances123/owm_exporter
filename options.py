#!/usr/bin/env python
import argparse
import json
import os
import sys

# DEFAULT_OPTIONS is a dictionary of string keys and values representing
# defaultable commandline options.
DEFAULT_OPTIONS = {
  'owm_api_key' : '',
  'scrape_interval': 600,
  'endpoint_port': 9265,
  'cities': 'madrid,tres cantos,colmenar viejo',
}

# PARSER is an instance of argparse.ArgumentParser.
PARSER = argparse.ArgumentParser(
  description='Prometheus exporter for weather reports from https://openweathermap.org')

# We add default options and enforce their type based on the default
# values in DEFAULT_OPTIONS
for option, default_val in DEFAULT_OPTIONS.items():
  option_type = type(default_val)
  PARSER.add_argument("--{0}".format(option), type=option_type, help="default value: {0}".format(default_val))


# config files are a special case with no default value, so we add the
# commandline option manually
PARSER.add_argument("--config", type=argparse.FileType('r'))

def get():
  '''
  Fetches options from file, environment, and commandline
  commandline options are given priority, then environment, then file
  ```
  #> cat '{"foo": "c"}' > conf.json
  #> owm_exporter --config=conf.json
  // foo is 'c'

  #> env FOO=b
  #> owm_exporter --config=conf.json
  // foo is 'b'

  #> env FOO=b
  #> owm_exporter --config=conf.json --foo=a
  // foo is 'a'
  ```
  '''

  # fetch out environment options
  env_options = {k: os.getenv(k.upper()) for k in DEFAULT_OPTIONS.keys()}
  # clear env options with null values
  env_options = {k: v for k, v in env_options.items() if v}

  # fetch out commandline options
  cmdline_options = vars(PARSER.parse_args(sys.argv[1:]))
  # clear commandline options with null values
  cmdline_options = {k: v for k, v in cmdline_options.items() if v}

  # fetch file options
  file_options = {}
  if 'config' in cmdline_options.keys():
    file_options = json.load(cmdline_options['config'])

  # merge down defaults < file < env < commandline
  final_options = DEFAULT_OPTIONS.copy()

  final_options.update(file_options)
  final_options.update(env_options)
  final_options.update(cmdline_options)

  if not final_options['owm_api_key']:
    print("ERROR; NO API KEY FOUND. make sure to set your api key. See readme")
    exit(1)

  return final_options