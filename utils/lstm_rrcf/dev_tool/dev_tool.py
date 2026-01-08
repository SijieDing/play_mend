# This tool generator fake data in streaming way.
# It help developers implementing features quickly without waiting for streaming data from kafka for many days
# Author: Eric Ding

# When start this tool, user use the command python main.y -c config.yaml
# The config.yaml has the following properties:
# template_string: It is a json similar format string like {"abc": "d", "ddd": ${fake1}, "mm": ${fake_timestamp}}.
#                  Any content need be replaced has tag wrapped in ${tag_id}
# tags: has all detail of the tag_id in the template_string
#       each tag has following detail:
#       tag_id:
#         arg: The list of values will be use for *argv. It is in yaml format. And the list support string, integer, float and bool
#         argv: A dictionary for **argv. It is is yaml format.
#       For example:
#       fake_timestamp:
#         argv:
#           starttime: ${REF_STARTTIME} . All tag "REF_" means reference property in the root path of the confguration.
#           interval: 60. It means when create message, this function return a timestamp whose time is 69 seconds later than the previous timestamp
# count: 60000
# STARTTIME: 2025-01-01:00:00:00 

import yaml
import argparse
from datetime import datetime, timedelta
import sys
sys.path.extend(['/app/libs/nab_detection_pkg', '/app/libs/nab_detection_pkg/nab_detection', '/app/libs/aiops_unite_pkg', '/app/libs/fake_data_generator_pkg'])
import os

from fake_data_generator.data_generator import DataGenerator

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    parser = argparse.ArgumentParser(description='Fake Data Streaming Generator')
    parser.add_argument('-c', '--config', required=True, help='Path to config.yaml file')
    args = parser.parse_args()

    # Removing the result log when testing start
    results_file = os.environ.get('LOCAL_RESULT_FILE', '/app/libs/fake_data_generator/results.log')
    if os.path.exists(results_file):
        os.remove(results_file)
        print(f"Removed existing log file: {results_file}")
    results_file = os.environ.get('LOCAL_RESULT_KAFKA_FILE', '/app/libs/fake_data_generator/results_kafka.log')
    if os.path.exists(results_file):
        os.remove(results_file)
        print(f"Removed existing kafka event log file: {results_file}")

    config = load_config(args.config)
    generator = DataGenerator(config)
    generator.generate_stream()
    

if __name__ == "__main__":
    main()
    