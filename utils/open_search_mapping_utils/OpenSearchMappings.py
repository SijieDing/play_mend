"""
Tools that read the OpenSearch Mapping, and determine the type
"""

from abc import ABC
from typing import Any, Dict, List, Set, Optional
import json
import glob, os

from aiops_unite import config
from aiops_unite import logger
from utils.open_search_mapping.OpenSearchField import OpenSearchField

log = None
filename_prefix = "mapping_opensearch_"
filename_postfix = ".json"


class OpenSearchMappings(ABC):
    """
    This class provide the following function:
    - Read files in a directory, each file is the result from openSearch query "GET _mappings".   Then, this class will
      read all the indices in the file.   Process the mapping for each indice, by adding them to a dictionary.
    - Detect if any "field" has multiple mapping types (this could happen because there are multiple indices and multiple files)
    - Provide a query for whether a specific field name is a "keyword"
    """

    def __init__(self):
        """ """
        global log
        gc = config.init()
        log = logger.init(gc, __name__)

        self._file_path_list: List = list()
        self._name_to_field_obj_dict: Dict[str, Any] = dict()

    def get_shorter_filename(self, filename: str) -> str:
        short_filename = filename.replace(filename_prefix, "").replace(
            filename_postfix, ""
        )
        short_filename = short_filename[0 : short_filename.find("_", 4)]
        return short_filename

    def read_json_file(self, filename_path: str) -> bool:
        """
        Read a JSON file contining the ElasticSearch mapping, and process the content
        """
        try:
            if not os.path.exists(filename_path):
                log.error("Path doesn't exist: " + filename_path)
                return False
            filename: str = os.path.basename(filename_path)
            directory: str = os.path.dirname(filename_path)
            log.info(
                "Start processing file: "
                + filename
                + "\n         --> from dir: "
                + directory
            )
            with open(filename_path, "r") as f:
                opensearch_mapping_json: Dict[Any, Any] = json.loads(f.read())
                short_filename = self.get_shorter_filename(filename)

                self.read_mapping_for_indices(opensearch_mapping_json, short_filename)
                log.info(
                    "Finished Start processing file: "
                    + filename
                    + ", from dir: "
                    + directory
                )
                return True
        except Exception as e:
            log.error("Error while processing file: " + filename_path)
            log.exception(e)
            return False

    def read_mapping_for_indices(
        self, opensearch_mapping_json: Dict[Any, Any], filename
    ) -> bool:  # NOSONAR
        keys_to_skip: Set = {"@timestamp"}
        """
        The expected format of the opensearch_mapping_json, returned from OpenSearch query "GET _mappings"
        {
            ".ql-datasources": {
                "mappings": {
                    ........ mappings for the index .....
                }
            },
            "unite-logs-000031": {
                "mappings": {
                    "dynamic_templates": [],
                    "properties": {
                        ........ mappings for the index .....            
                    }
                }
            },
            "unite-logs-000032": { ... },
            "unite-events-000032": { ... }, 
            ..... more indices .....
        }
        """
        for index_name in opensearch_mapping_json:
            if index_name.startswith("unite"):
                log.info(
                    f"Start processing index={index_name}\n         --> from file={filename}"
                )
                try:
                    index_mappings: Dict[Any, Any] = opensearch_mapping_json[
                        index_name
                    ]["mappings"]
                    if "properties" not in index_mappings:
                        log.warning(
                            f"Index={index_name} doesn't have field mapping, skipped index.\n         --> from file="
                            + filename
                        )
                    else:
                        index_mappings_properties: Dict[Any, Any] = index_mappings[
                            "properties"
                        ]
                        self._process_json_recursively(
                            "",
                            index_mappings_properties,
                            keys_to_skip,
                            filename,
                            index_name,
                        )
                        log.info(
                            f"Finished processing index={index_name}\n         --> from file={filename}"
                        )
                except Exception:
                    log.error(
                        f"Error during processing index={index_name}\n         --> from file={filename}"
                    )
                    raise

    def _process_json_recursively(
        self,
        name_prefix: str,
        properties: Dict[Any, Any],
        keys_to_skip: set,
        filename: str,
        index_name: str,
    ):
        """
        "properties": {
            "@timestamp": { "type": "date" },
            "attributes": {
                "properties": {
                    "com": {
                        "properties": {
                            "ibm": { ... }
                    }   }
                    "log" : {
                        "properties": {
                            "ibm": { ... }
                    }   }
        }   }    }
        """
        for key in properties.keys():
            value = ""
            try:
                if key in keys_to_skip:
                    continue

                if name_prefix:
                    concatenated_name = f"{name_prefix}.{key}"
                else:
                    concatenated_name = key
                # log.debug(f"{index_name} -> {key}")
                value = properties[key]
                if "properties" in value.keys():
                    self._process_json_recursively(
                        concatenated_name,
                        value["properties"],
                        keys_to_skip,
                        filename,
                        index_name,
                    )
                    if len(value) > 1:
                        log.error(
                            "Error: object with 1+ keys: properties and other keys are not supported: "
                            + value.keys
                            + "\n in index="
                            + index_name
                            + "\n in file="
                            + filename
                        )
                else:
                    # There are no properties object, that means this is the leaf node.
                    self._add_opensearch_field_to_dict(
                        concatenated_name, value, filename, index_name
                    )
            except Exception:
                log.error("Error when processing key=" + key + " value=" + str(value))
                raise

    def _add_opensearch_field_to_dict(
        self,
        field_name: str,
        field_mapping_json: Dict[Any, Any],
        filename: str,
        index_name: str,
    ):
        """
        Add the current field name and mapping to the dictionary.

        The input data could come from multiple indices (from the same opensearch or multiple opensearch),
        therefore, it's possible to have multiple field mappings for the same field name.
        """
        open_search_field_obj: Optional[OpenSearchField] = None
        if field_name in self._name_to_field_obj_dict:
            open_search_field_obj = self._name_to_field_obj_dict[field_name]
        else:
            open_search_field_obj = OpenSearchField(field_name)
            self._name_to_field_obj_dict[field_name] = open_search_field_obj

        open_search_field_obj.add_field(field_mapping_json, filename, index_name)

    def print_fields_with_multiple_type_definition(self):
        for field_name in self._name_to_field_obj_dict:
            opensearch_field_obj: OpenSearchField = self._name_to_field_obj_dict[
                field_name
            ]
            opensearch_field_obj.print_field_with_multiple_type_definition()

    def is_field_a_keyword(self, field_name: str) -> bool:
        if field_name in self._name_to_field_obj_dict:
            opensearch_field_obj: OpenSearchField = self._name_to_field_obj_dict[
                field_name
            ]
            opensearch_field_obj.is_keyword(is_print_warning=True)
        else:
            log.error(f"Cannot find field: {field_name}")

    def write_field_to_keyword_map_to_file(self, file_path: str):
        with open(file_path, "w") as file:
            file.write("field_name,is_keyword,number_of_field_type,first_field_type")
            sorted_field_name: List = sorted(list(self._name_to_field_obj_dict.keys()))
            for field_name in sorted_field_name:
                opensearch_field_obj: OpenSearchField = self._name_to_field_obj_dict[
                    field_name
                ]
                is_keyword: bool = opensearch_field_obj.is_keyword(
                    is_print_warning=True
                )
                number_of_field_types: int = (
                    opensearch_field_obj.get_number_of_field_types(
                        is_print_warning=False
                    )
                )
                first_field_type: str = opensearch_field_obj.get_first_field_type(
                    is_print_warning=False
                )
                file.write(
                    f"{field_name},{is_keyword},{number_of_field_types},{first_field_type}\n"
                )


if __name__ == "__main__":

    os.environ["AP_ANOMALY_DETECTION_FUNCTION_CONFIG"] = os.path.join(
        os.path.dirname(__file__),
        "../../libs/aiops_unite_pkg/",
        "aiops_unite/sample-config.yaml",
    )
    open_search_mappings = OpenSearchMappings()
    # gc = config.init()
    # logger = logging.init()
    cur_path = os.path.abspath(__file__)
    cur_path = os.path.dirname(cur_path)

    file_pattern = f"{filename_prefix}*{filename_postfix}"
    opensearch_file_search_path = os.path.join(
        cur_path, "open_search_data", file_pattern
    )
    matching_file_list = glob.glob(opensearch_file_search_path)
    matching_file_list.sort(reverse=True)

    log.info(
        "Processing files from "
        + opensearch_file_search_path
        + ": \n"
        + str(matching_file_list)
    )

    for file in matching_file_list:
        success = open_search_mappings.read_json_file(file)
    open_search_mappings.print_fields_with_multiple_type_definition()
    """ Here are some example outputs from the print:
    ERROR:root:Field=resource.messaging.ibmmq.buffer_pool.id has 2 mapping types
    ---> {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}
    ---> ['DEV_218.unite-metrics-000110', 'DEV_218.unite-metrics-000111', 'DEV_218.unite-metrics-000113', 'DEV_218.unite-metrics-000114', 'DEV_218.unite-metrics-000115', 'DEV_218.unite-metrics-000116', 'DEV_218.unite-metrics-000117', 'DEV_218.unite-metrics-000119', 'DEV_218.unite-metrics-000120', 'DEV_218.unite-metrics-000121', 'DEV_218.unite-metrics-000122', 'DEV_218.unite-metrics-000123', 'DEV_218.unite-metrics-000124', 'DEV_218.unite-metrics-000125', 'DEV_218.unite-metrics-000129', 'DEV_218.unite-metrics-000130', 'DEV_218.unite-metrics-000131', 'DEV_218.unite-metrics-000143']
    ---> {'type': 'long'}
    ---> ['DEV_218.unite-metrics-000118', 'DEV_218.unite-metrics-000126', 'DEV_218.unite-metrics-000127', 'DEV_218.unite-metrics-000128', 'DEV_218.unite-metrics-000137', 'DEV_218.unite-metrics-000144', 'DEV_218.unite-metrics-000145']
    ERROR:root:Field=resource.messaging.ibmmq.page_set.id has 2 mapping types
    ---> {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}
    ---> ['DEV_218.unite-metrics-000110', 'DEV_218.unite-metrics-000111', 'DEV_218.unite-metrics-000113', 'DEV_218.unite-metrics-000114', 'DEV_218.unite-metrics-000115', 'DEV_218.unite-metrics-000116', 'DEV_218.unite-metrics-000117', 'DEV_218.unite-metrics-000118', 'DEV_218.unite-metrics-000119', 'DEV_218.unite-metrics-000120', 'DEV_218.unite-metrics-000121', 'DEV_218.unite-metrics-000122', 'DEV_218.unite-metrics-000123', 'DEV_218.unite-metrics-000124', 'DEV_218.unite-metrics-000125', 'DEV_218.unite-metrics-000128', 'DEV_218.unite-metrics-000129', 'DEV_218.unite-metrics-000130', 'DEV_218.unite-metrics-000131', 'DEV_218.unite-metrics-000143']
    ---> {'type': 'long'}
    ---> ['DEV_218.unite-metrics-000126', 'DEV_218.unite-metrics-000127', 'DEV_218.unite-metrics-000137', 'DEV_218.unite-metrics-000144', 'DEV_218.unite-metrics-000145']
    ERROR:root:Field=resource.messaging.ibmmq.version has 2 mapping types
    ---> {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}
    ---> ['DEV_218.unite-metrics-000111', 'DEV_218.unite-metrics-000113', 'DEV_218.unite-metrics-000114', 'DEV_218.unite-metrics-000116', 'DEV_218.unite-metrics-000117', 'DEV_218.unite-metrics-000118', 'DEV_218.unite-metrics-000121', 'DEV_218.unite-metrics-000123', 'DEV_218.unite-metrics-000124', 'DEV_218.unite-metrics-000125', 'DEV_218.unite-metrics-000127', 'DEV_218.unite-metrics-000128', 'DEV_218.unite-metrics-000129', 'DEV_218.unite-metrics-000130', 'DEV_218.unite-metrics-000131', 'DEV_218.unite-metrics-000137', 'DEV_218.unite-metrics-000143', 'DEV_218.unite-metrics-000144', 'DEV_218.unite-metrics-000145', 'PST_tvt2025.unite-metrics-000045', 'PST_tvt2025.unite-metrics-000046', 'PST_tvt2025.unite-metrics-000047', 'PST_tvt2025.unite-metrics-000048', 'PST_tvt2025.unite-metrics-000050', 'PST_tvt2025.unite-metrics-000051', 'PST_tvt2025.unite-metrics-000052', 'PST_tvt2025.unite-metrics-000053', 'PST_tvt2025.unite-metrics-000054', 'PST_tvt2025.unite-metrics-000055', 'PST_tvt2025.unite-metrics-000056', 'PST_tvt2025.unite-metrics-000057', 'PST_tvt2025.unite-metrics-000058', 'PST_tvt2025.unite-metrics-000059', 'PST_tvt2025.unite-metrics-000060', 'PST_tvt2025.unite-metrics-000061', 'PST_tvt2025.unite-metrics-000062', 'PST_tvt2025.unite-metrics-000063', 'PST_tvt2025.unite-metrics-000064', 'PST_tvt2025.unite-metrics-000065', 'PST_tvt2025.unite-metrics-000068', 'PST_tvt2025.unite-metrics-000069', 'PST_tvt2025.unite-metrics-000070']
    ---> {'type': 'long'}
    ---> ['DEV_218.unite-metrics-000110', 'DEV_218.unite-metrics-000115', 'DEV_218.unite-metrics-000119', 'DEV_218.unite-metrics-000120', 'DEV_218.unite-metrics-000122', 'DEV_218.unite-metrics-000126']

    """

    out_csv_filename = os.path.join(os.path.dirname(__file__), "field_mapping.csv")
    open_search_mappings.write_field_to_keyword_map_to_file(out_csv_filename)
