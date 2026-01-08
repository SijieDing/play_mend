import datetime
import os
import sys
from collections import OrderedDict
from typing import Any, Dict, List

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap


def read_yaml(filename: str):
    with open(filename, "r") as file:
        # Note: ruamel.yaml.YAML(typ="safe", pure=True) - the safe loader doesn't presever order
        yaml = ruamel.yaml.YAML()
        yaml.indent(mapping=4, sequence=4, offset=2)
        # yaml.preserve_quotes = True

        yaml_obj = yaml.load(file)
        print(type(yaml_obj))
        return yaml_obj


def add_date_to_filename(filepath, date_format="%Y-%m-%d_%H-%M-%S"):
    """
    Adds the current date to a filename.
    """
    dirname = os.path.dirname(filepath)
    filename = os.path.basename(filepath)

    name, ext = os.path.splitext(filename)
    date_str = datetime.datetime.now().strftime(date_format)
    new_filename = f"{name}_{date_str}{ext}"

    new_filepath = os.path.join(dirname, new_filename)
    return new_filepath


def write_yaml(data, filename: str):
    with open(filename, "w") as file:
        yaml = ruamel.yaml.YAML()
        yaml.indent(mapping=4, sequence=4, offset=2)

        yaml.dump(data, file)


def deep_copy_yaml(item):
    if isinstance(item, dict):
        # This could be dict, OrderedDict, ruamel.yaml.comments.CommentedMap (which interit OrderedDict, which interit dict)
        class_type: type = type(item)
        new_dict = class_type()
        for key, value in item.items():
            new_dict[key] = deep_copy_yaml(value)
        return new_dict
    elif isinstance(item, list):
        # This could be list, ruamel.yaml.comments.CommentedSeq (which interit list)
        class_type: type = type(item)
        new_list = class_type()
        for element in item:
            new_list.append(deep_copy_yaml(element))
        return new_list
    else:
        return item


if __name__ == "__main__":

    """
    Example Data:
        metrics:
            - name: attributes.com.ibm.zou.metrics.total_send_sessions_in_use
                timestamp: "@timestamp"
                uuid: resource.uuid
                conditions:
                    resource.com.ibm.zou.omegamon.table_name: cicscos
                    resource.com.ibm.zou.resource_type: CICSRegion
                threshold: 1
                const: 0
                group_bys:
                  - resource.cics.region.name
            - name: attributes.com.ibm.zou.metrics.total_receive_sessions_in_use
                timestamp: "@timestamp"
                uuid: resource.uuid
                conditions:
                    resource.com.ibm.zou.omegamon.table_name: cicscos
                    resource.com.ibm.zou.resource_type: CICSRegion
                threshold: 1
                const: 0
                group_bys:
                    - resource.cics.region.name
    """
    # yaml_list = yaml_obj["metrics"]
    # filepath = "/home/chanyp/unite_workspace/DS_AnomalyDetection/libs/aiops_unite_pkg/aiops_unite/sample_config_merge.yaml"
    # filepath = "/home/chanyp/unite_workspace/DS_AnomalyDetection/libs/aiops_unite_pkg/aiops_unite/sample_config_timothy.yaml"
    # filepath = "/home/chanyp/unite_workspace/DS_AnomalyDetection/libs/aiops_unite_pkg/aiops_unite/sample_config_timothy2.yaml"
    filepath = "/home/chanyp/unite_workspace/DS_AnomalyDetection/libs/aiops_unite_pkg/aiops_unite/sample_config_original.yaml"
    yaml_obj = read_yaml(filepath)
    array_to_sort = ["metrics"]
    keys_to_order_list_items_by_value = [
        ["conditions", "resource.com.ibm.zou.resource_type"],
        ["name"],
    ]
    keys_to_order_keys_in_map = [
        "name",
        "timestamp",
        "uuid",
        "group_bys",
        "group_by",
        "conditions",
        "threshold",
        "const",
        "training_exclusions",
    ]

    new_dict = deep_copy_yaml(yaml_obj)

    new_filepath = add_date_to_filename(filepath)
    print(f"Outputting new yaml to: {new_filepath}")
    write_yaml(new_dict, new_filepath)


# TODO
# Run through all data in ODP, and confirm if a machine record is found
