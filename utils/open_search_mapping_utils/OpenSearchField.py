"""
Class that encapculate a Field from OpenSearch
"""

from typing import Dict, Any, List, Set, Optional
from collections import OrderedDict
from abc import ABC
import logging


class OpenSearchField(ABC):
    """
    This class encapsulte the OpenSeach Field:
    """

    def __init__(self, field_name: str):
        """
        Initialize this object
        """
        self._field_name = field_name
        self._field_type_list: List[OpenSearchFieldType] = list()

    def add_field(
        self, opensearch_field_json: Dict[Any, Any], filename: str, index_name: str
    ):
        """
        Added a mapping current the field.

        The input data could come from multiple indices (from the same opensearch or multiple opensearch),
        therefore, it's possible to have multiple field mappings.
        """

        # Loop through all existing field to find a match
        matching_field_type: Optional[OpenSearchFieldType] = None
        for field_type in self._field_type_list:
            if field_type.is_same_field_type(opensearch_field_json):
                matching_field_type = field_type
                break

        if not matching_field_type:
            # Didn't find a matching field type, then create a new field
            matching_field_type = OpenSearchFieldType(
                self._field_name, opensearch_field_json, filename, index_name
            )
            self._field_type_list.append(matching_field_type)
        else:
            # add the file and index
            matching_field_type.add_filename_and_index(filename, index_name)

    def is_keyword(self, is_print_warning: bool = False) -> bool:
        """
        Return True is any one of the field type is a keyword
        """
        if is_print_warning:
            self.print_field_with_multiple_type_definition()
        for field_type in self._field_type_list:
            if field_type.is_keyword():
                return True
        return False

    def get_first_field_type(self, is_print_warning: bool = False) -> str:
        """
        Return the field type
        """
        if is_print_warning:
            self.print_field_with_multiple_type_definition()
        return self._field_type_list[0].get_field_type()

    def get_number_of_field_types(self, is_print_warning: bool = False) -> int:
        """
        Return the count of distinct field types are mapped to this field
        """
        if is_print_warning:
            self.print_field_with_multiple_type_definition()
        return len(self._field_type_list)

    def get_field_type_list_as_json(self) -> List[Dict[Any, Any]]:
        """
        Return the list of field types as a json object (i.e. Dict)
        """
        list_of_json: List[Dict[Any, Any]] = list()
        for field_type in self._field_type_list:
            orig_json = field_type.get_original_field_mapping_json()
            list_of_json.append(orig_json)
        return list_of_json

    def print_field_with_multiple_type_definition(self):
        """
        If there are multiple type mapping for this field, print the types to the log as error
        WARNING: This method should avoid calling other method in this class.  It might result
                 in endless recursive calls
        """
        number_of_field_type = len(self._field_type_list)
        if number_of_field_type > 1:
            str_to_print = ""
            for field_type in self._field_type_list:
                orig_json: Dict[Any, Any] = field_type.get_original_field_mapping_json()
                index_list: List[str] = field_type.get_indices_from_all_files()
                str_to_print = (
                    str_to_print
                    + "\n---> "
                    + str(orig_json)
                    + "\n---> "
                    + str(index_list)
                )
            logging.error(
                f"Field={self._field_name} has {number_of_field_type} mapping types"
                + str_to_print
            )


class OpenSearchFieldType(ABC):
    """
    This class encapsulte the OpenSeach Field Mapping:
    """

    def __init__(
        self,
        field_name: str,
        opensearch_field_mapping_json: Dict[Any, Any],
        filename: str,
        index_name: str,
    ):
        """
        Example field mapping:
            "uid": {
                "type": "keyword",
            }
            "uid": {
                "type": "text",
                "fields": {
                    "keyword": {
                        "type": "keyword",
                        "ignore_above": 256
            }   }   }
            "severityNumber": {
                    "type": "long"
            }
            "k_max": {
                "type": "float"
            },
        """
        self._field_name = field_name

        self._filenames_to_index_dict: Dict[str, Set] = dict()
        self._filenames_to_index_dict[filename] = set()
        self._filenames_to_index_dict[filename].add(index_name)

        self._type = opensearch_field_mapping_json["type"]

        self._original_json: Dict[Any, Any] = opensearch_field_mapping_json
        self._flattened_field_mapping: OrderedDict = self._flatten_json(
            opensearch_field_mapping_json
        )

        self._is_keyword = False
        if "keyword" in self._flattened_field_mapping.values():
            self._is_keyword = True

    def get_field_type(self) -> str:
        return self._type

    def get_original_field_mapping_json(self) -> Dict[Any, Any]:
        """
        Return the original field mapping used to create this object
        """
        return self._original_json

    def get_indices_from_all_files(self) -> List[str]:
        index_list: List[str] = list()
        # list(*self._filenames_to_index_dict.values())
        for key, lst in self._filenames_to_index_dict.items():
            for value_in_list in lst:
                index_list.append(f"{key}.{value_in_list}")
        index_list.sort()
        return index_list

    def add_filename_and_index(self, filename: str, index_name: str) -> None:
        """
        Add the filename and index name
        """
        if filename not in self._filenames_to_index_dict:
            self._filenames_to_index_dict[filename] = set()

        self._filenames_to_index_dict[filename].add(index_name)

    def is_keyword(self) -> bool:
        """
        Return whether this field is a "keyword"
        """
        return self._is_keyword

    def is_same_field_type(self, input_field_mapping_json: Dict[Any, Any]) -> bool:
        """
        Return whether an input field mapping has the same key and value as this OpenSearchFieldMap
        """
        input_flatted_field_mapping: OrderedDict = self._flatten_json(
            input_field_mapping_json
        )

        if len(input_flatted_field_mapping) != len(self._flattened_field_mapping):
            return False
        elif input_flatted_field_mapping == self._flattened_field_mapping:
            return True
        else:
            return False

    def _flatten_json(self, json_obj, parent_key="", sep=".") -> OrderedDict:
        """
        Return a flattened dictionary (e.g. attribute.com.ibm.cpu) from a nested JSON structure.
        """
        flattened = OrderedDict()
        for key, value in json_obj.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                flattened.update(self._flatten_json(value, new_key, sep=sep))
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    flattened.update(
                        self._flatten_json({str(i): item}, new_key, sep=sep)
                    )
            else:
                flattened[new_key] = value

        sorted_flattened = OrderedDict(sorted(flattened.items()))
        return sorted_flattened
