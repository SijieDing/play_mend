"""
This code operation on the KPI Config (e.g. sample_config.yaml file.)  It provide the following functionalities:
1. Sort the list of Metric in the YAML file, under the "metrics" tag.  (Note: you can
    define the keys, whose value will be used for sorting.)
2. Sort the dictionary within the list by the Key using specific order.  (Note: you can
    change the order in main)
"""

import os, sys
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap
import datetime
from typing import List, Dict, Any, Set, Union, Optional
from collections import OrderedDict


def get_value_by_path(dict_obj: Dict[str, Any], path: List[str]) -> Any:
    """
    Get the value of a field by the path.
    Example path:
        ["conditions", "resource.com.ibm.zou.resource_type"]
    """
    current = dict_obj
    for key in path:
        if key in current:
            current = current[key]
        else:
            return None
    return current


def set_value_by_path(dict_obj: Dict[str, Any], path: List, value: Any) -> bool:
    """
    Set the value of a field by the path.
    Example path:
        ["conditions", "resource.com.ibm.zou.resource_type"]
    """
    current = dict_obj
    path_len = len(path)
    for i in range(path_len - 1):
        key = path[i]
        if key in current:
            current = current[key]
        else:
            return False
    # Set the value
    current[path[path_len - 1]] = value
    return True


def get_list_by_path(dict_obj: Dict[str, Any], path: List[str]) -> List[Dict[Any, Any]]:
    """
    Get a list specified by a path.
    Example path:
        ["conditions", "resource.com.ibm.zou.resource_type"]
    """
    list_obj = get_value_by_path(dict_obj, path)
    if isinstance(list_obj, List):
        return list_obj
    else:
        raise Exception(f"path={str(path)} does not point to an array")


def sort_dict_keys(existing_map: Dict[str, Any], orderby_keys: List[str]):
    """
    Reorder a dictionary based on list of keys.  If there are fields that isn't included in the list,
    they will be appended at the end of the Dict using the same order as the original dict.

    Example for order_of_keys:
        keys_to_order_keys_in_map = [
            "name", "timestamp", "uuid", "group_bys", "group_by", "conditions", "threshold", "const", "training_exclusions",
        ]

    """
    new_map: CommentedMap = ruamel.yaml.CommentedMap()

    # Get the keys specified in the order_of_keys
    for key in orderby_keys:
        if key in existing_map:
            new_map[key] = existing_map[key]

    # Get the keys NOT in order_of_keys, and preserve the order.
    for key in existing_map:
        if key not in new_map:
            new_map[key] = existing_map[key]

    return new_map


def sort_dict_keys_in_list(
    list_of_dict: List[Dict[str, Any]], orderby_keys: List[str]
) -> None:
    """
    Reorder the keys of every dict object in the list.  The input object will be updated
    """
    for index in range(len(list_of_dict)):
        a_dict = list_of_dict[index]
        sorted_dict = sort_dict_keys(a_dict, orderby_keys)
        list_of_dict[index] = sorted_dict

    return None


def get_unique_values_from_list_of_dict(
    list_obj: List[Dict[str, Any]], relative_path_in_dict: List[str]
) -> List[str]:
    """
    In a list of dict, extract value from the dict using the relative_path.
    Collect these extract values, and return the unique values.
    """
    # list_obj = get_list_by_path(dict_obj, path_to_list)
    unique_value_set: Set = set()
    for dict_in_list in list_obj:
        unique_value: str = get_value_by_path(dict_in_list, relative_path_in_dict)
        if unique_value:
            unique_value_set.add(unique_value)
    the_list = list(*unique_value_set)
    the_list = sorted(the_list)
    return the_list


def get_concat_val_using_multi_pathlist(
    dict_obj: Dict[str, Any],
    multi_choices_of_pathlist: List[List[List[str]]],
    concat_separator="-",
):
    """
    This function will go through each "choice of path" to generate concatentated value.  When a paths return a value,
    the value will be returned.  If a paths doesn't result in value, it will try the next path.
    Example
        pathlist_cdp = [
            ["conditions", "resource.com.ibm.zou.cdp.resource_type"],
            ["name"],
        ]
        pathlits_odp = [
            ["conditions", "resource.com.ibm.zou.resource_type"],
            ["name"],
        ]
        multi_choices_of_pathlist = [ pathlist_cdp, pathlits_odp ]
    """
    for paths_to_value in multi_choices_of_pathlist:
        concatenated_value = get_concatenated_value_using_pathlist(
            dict_obj, paths_to_value, concat_separator
        )
        if concatenated_value:
            return concatenated_value

    print(
        f"Cannot find value using \n--> path={str(multi_choices_of_pathlist)}\n--> dict={str(dict_obj)}"
    )
    return None


def get_concatenated_value_using_pathlist(
    dict_obj: Dict[str, Any],
    paths_to_value: Optional[List[List[str]]] = None,
    concat_separator="-",
):
    """
    Generate a concatenated string by:
    - If paths_to_value wasn't specifieid
        - Use each key in the dict_obj as a path in paths_to_value
    - For each path (i.e. List[str])
        - extract the value using the path
        - concatenate the value

    If any one of the key within a path doesn't exist, return None.

    Example paths:
        e.g. keys_to_order_list_items_by_value = [
                ["conditions", "resource.com.ibm.zou.resource_type"],
                ["name"],
            ]

    In this example, the value from path=["conditions", "resource.com.ibm.zou.resource_type"]
        will be concatenated with value from path=["name]
    """
    values_to_sort: str = ""
    is_found_all_keys: bool = True

    if not paths_to_value:
        sorted_keys = sorted(dict_obj.keys())
        for key in sorted_keys:
            paths_to_value.append([key])

    for path in paths_to_value:
        value: str = get_value_by_path(dict_obj, path)
        if not value:
            is_found_all_keys = False
            break
        values_to_sort = values_to_sort + concat_separator + value

    if is_found_all_keys:
        return values_to_sort
    else:
        return None


# def get_concatentated_value_from_dict(
#     dict_obj: Dict[str, Any],
#     paths_to_obj: List[str],
#     concat_separator="-",
# ):
#     """
#     Generate a concatenated string using:
#     - Sort the list by key, then append the values.
#     """
#     values_to_sort: str = ""
#     cur_dict = get_value_by_path(dict_obj, paths_to_obj)
#     if isinstance(cur_dict, dict):
#         key_list = sorted(cur_dict.keys())
#         for key in key_list:
#             value = cur_dict[key]
#             values_to_sort = values_to_sort + concat_separator + value
#         return values_to_sort
#     elif isinstance(cur_dict, list):
#         key_list = sorted(cur_dict)
#         values_to_sort = concat_separator.join(key_list)
#         return values_to_sort
#     else:
#         print(
#             f"dictionary path doesn't have a list:\npath={str(paths_to_obj)}\ndict={str(dict_obj)}"
#         )
#         return None


def _sort_list_of_dict_by_values_using_orderedby_keys(
    dict_list: List[Dict[str, Any]],
    multi_pathlist: List[List[List[str]]],
    orderby_keys: List[str],
    concat_separator="-",
) -> List[Dict[str, Any]]:
    """
    This method will sort a list of Dictionary.  Ths sort will use multiple values from the dictionary.
    Each fo the value is specified by the path to the key.

    - multi_pathlist:
            e.g. pathlist_cdp = [
                    ["conditions", "resource.com.ibm.zou.cdp.resource_type"],
                    ["name"],
                ]
                pathlits_odp = [
                    ["conditions", "resource.com.ibm.zou.resource_type"],
                    ["name"],
                ]
                multi_pathlist = [ pathlist_cdp, pathlits_odp ]

    - keys_to_order_keys_in_map:   Key to sort each the keys in a dictionary.
            e.g. keys_to_order_keys_in_map = [
                    "name", "timestamp", "uuid", "group_bys", "group_by", "conditions", "threshold", "const", "training_exclusions",
                    ]
    """
    new_key_to_value_dict: Dict[str, Dict[str, Any]] = OrderedDict()
    repeated_count: int = 0
    # Sort the list by the values pointed to by the keys
    for a_dict in dict_list:
        concat_value: str = get_concat_val_using_multi_pathlist(a_dict, multi_pathlist)
        if concat_value:
            values_from_condition = get_concatenated_value_using_pathlist(
                a_dict["conditions"], paths_to_value=None
            )
            if values_from_condition:
                concat_value = concat_value + concat_separator + values_from_condition
        else:
            print(
                f"Cannot find unique key from \ndict={str(a_dict)}\nkey={str(multi_pathlist)}"
            )
            continue

        # For a yaml_item (type ruamel.yaml.CommentedMap), sort the keys.
        yaml_item_with_key_sorted = sort_dict_keys(a_dict, orderby_keys)

        # Check if the value already existed in the new dictionary
        if concat_value not in new_key_to_value_dict:
            new_key_to_value_dict[concat_value] = yaml_item_with_key_sorted
        else:
            yaml_item_with_key_sorted["name"] = (
                yaml_item_with_key_sorted["name"] + f".repeat.{repeated_count}"
            )
            new_key_to_value_dict[f"{concat_value}.repeat.{repeated_count}"] = (
                yaml_item_with_key_sorted
            )
            repeated_count = repeated_count + 1

            print(
                f"Error: key {concat_value} already existed \n--->{new_key_to_value_dict[concat_value]}\n--->{yaml_item_with_key_sorted}"
            )
    # Sort the new dict by the key.
    sorted_dict = sorted(new_key_to_value_dict.items(), reverse=False)
    print(f"Number of duplicated names : {repeated_count}")

    # Return the values of the dict as a list
    return [value for _, value in sorted_dict]


def sort_list_in_yaml(
    dict,
    path_to_list: List,
    keys_to_order_list_items_by_value: List[List[str]],
    keys_to_order_keys_in_map: List[str],
):
    """
    Sort a specific list within an YAML object
    """
    list_of_obj: List[Dict[str, Any]] = get_list_by_path(dict, path_to_list)
    list_of_obj = _sort_list_of_dict_by_values_using_orderedby_keys(
        list_of_obj,
        multi_pathlist=keys_to_order_list_items_by_value,
        orderby_keys=keys_to_order_keys_in_map,
    )
    success = set_value_by_path(dict, path_to_list, list_of_obj)
    if success:
        print("Successfully sorted the list")

    return dict


def sort_the_yaml(
    yaml_obj: Dict[Any, Any], yaml_path_to_list: List[Any], config_type: str
):
    pathlist_cdp = [
        ["conditions", "resource.com.ibm.zou.cdp.resource_type"],
        ["name"],
    ]
    pathlits_odp = [
        ["conditions", "resource.com.ibm.zou.resource_type"],
        ["name"],
    ]
    combined_keys_to_order_list_items_by_value = [
        pathlist_cdp,
        pathlits_odp,
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
    new_dict = sort_list_in_yaml(
        yaml_obj,
        yaml_path_to_list,
        keys_to_order_list_items_by_value=combined_keys_to_order_list_items_by_value,
        keys_to_order_keys_in_map=keys_to_order_keys_in_map,
    )
    new_filepath = add_date_to_filename(filepath)
    print(f"Outputting sorted yaml to: {new_filepath}")
    write_yaml(new_dict, new_filepath)


def print_table_names(config_type: str):
    relative_path_to_table_name_odp = [
        "conditions",
        "resource.com.ibm.zou.omegamon.table_name",
    ]
    relative_path_to_table_name_cdp = [
        "conditions",
        "resource.com.ibm.zou.cdp.source.name",
    ]

    if config_type == "cdp":
        relative_path_to_table_name = relative_path_to_table_name_cdp
    else:
        relative_path_to_table_name = relative_path_to_table_name_odp

    unique_tables = get_unique_values_from_list_of_dict(
        yaml_obj, yaml_path_to_list, relative_path_to_table_name
    )
    print("\n".join(unique_tables))


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
    config_type = "odp"
    filepath = "/home/chanyp/unite_workspace/DS_AnomalyDetection/libs/aiops_unite_pkg/aiops_unite/sample_config_ODP.yaml"

    # config_type = "cdp"
    # filepath = "/home/chanyp/unite_workspace/DS_AnomalyDetection/libs/aiops_unite_pkg/aiops_unite/sample_config_CDP.yaml"

    # filepath = "/home/chanyp/unite_workspace/DS_AnomalyDetection/libs/aiops_unite_pkg/aiops_unite/sample_config.yaml"
    yaml_obj = read_yaml(filepath)
    yaml_path_to_list = ["metrics"]

    """
    Uncomment to generate a sorted yaml
    """
    sort_the_yaml(yaml_obj, yaml_path_to_list, config_type)

    """
    Uncomment to generate a list of unique table names
    """
