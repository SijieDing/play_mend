"""
Detect anomalies with moving average base line
"""

import os
import time

os.environ["AP_ANOMALY_DETECTION_FUNCTION_CONFIG"] = os.path.join(
    os.path.dirname(__file__),
    "../../libs/aiops_unite_pkg/",
    "aiops_unite/sample-config.yaml",
)

import json
import traceback

import aiops_unite.data.OTELMetricData as oteldata_util
import flask
from aiops_change_detection import change_detection


def main(metric_event=None):
    """
    Fission function stub main
    """

    resp = None

    try:
        # load message body
        if metric_event is not None:
            body = json.loads(metric_event)
        else:
            body = flask.request.get_json()

        anomaly = change_detection.change_detection(body)

        if anomaly is not None:
            resp = flask.Response(json.dumps(anomaly))
            resp.status_code = 200
        else:
            raise Exception(f"Not an anomaly ({time.time_ns()})")
    except Exception as err:
        print(f"Exception caught: {err}")
        print(traceback.format_exc())
        resp = flask.Response(f"Change detection failed with error {err}")
        resp.status_code = 400

    return resp


def get_data_PST_Db2():
    return """
            {
            "resourceLogs": [
                {
                "resource": {
                    "attributes": [
                    {
                        "key": "com.ibm.zou.resource_type",
                        "value": {
                        "stringValue": "Db2Subsystem"
                        }
                    },
                    {
                        "key": "db.system",
                        "value": {
                        "stringValue": "db2"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.write_time",
                        "value": {
                        "intValue": "1742785814000000000"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.product_code",
                        "value": {
                        "stringValue": "kd5"
                        }
                    },
                    {
                        "key": "com.ibm.zou.collector.name",
                        "value": {
                        "stringValue": "otel-collector"
                        }
                    },
                    {
                        "key": "db.db2.version",
                        "value": {
                        "stringValue": "1215"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.dp_sy_exc.dsc_active",
                        "value": {
                        "stringValue": "YES"
                        }
                    },
                    {
                        "key": "com.ibm.zou.source.namespace",
                        "value": {
                        "stringValue": "omegamon"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.dp_sy_exc.global_trace_active",
                        "value": {
                        "stringValue": "False"
                        }
                    },
                    {
                        "key": "db.db2.data_sharing_group.name",
                        "value": {
                        "stringValue": "DC1G"
                        }
                    },
                    {
                        "key": "com.ibm.zou.collector.namespace",
                        "value": {
                        "stringValue": "z-aiops-unite"
                        }
                    },
                    {
                        "key": "db.db2.subsystem.name",
                        "value": {
                        "stringValue": "DC17"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.origin_node",
                        "value": {
                        "stringValue": "DC17:LP17:DB2"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.dp_sy_exc.dist_db_inactive",
                        "value": {
                        "stringValue": "False"
                        }
                    },
                    {
                        "key": "host.id",
                        "value": {
                        "stringValue": "LP17"
                        }
                    },
                    {
                        "key": "com.ibm.zou.source.name",
                        "value": {
                        "stringValue": "odp"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.table_version",
                        "value": {
                        "intValue": "1"
                        }
                    },
                    {
                        "key": "com.ibm.zou.collector.version",
                        "value": {
                        "stringValue": "development"
                        }
                    },
                    {
                        "key": "host.arch",
                        "value": {
                        "stringValue": "s390x"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.table_name",
                        "value": {
                        "stringValue": "dp_sy_exc"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.interval_seconds",
                        "value": {
                        "intValue": "60"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.dp_sy_exc.time",
                        "value": {
                        "stringValue": "2025-03-23T23:10:13.935-04:00"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.dp_sy_exc.group_or_subsystem_type",
                        "value": {
                        "stringValue": "DB2"
                        }
                    },
                    {
                        "key": "os.type",
                        "value": {
                        "stringValue": "z_os"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.dp_sy_exc.group_object_analysis_status",
                        "value": {
                        "stringValue": "No"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.interval_time",
                        "value": {
                        "intValue": "0"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.dp_sy_exc.status",
                        "value": {
                        "stringValue": "Online"
                        }
                    },
                    {
                        "key": "com.ibm.zou.omegamon.dp_sy_exc.wait_tape_mount",
                        "value": {
                        "stringValue": "False"
                        }
                    },
                    {
                        "key": "uuid",
                        "value": {
                        "stringValue": "55459860-5b3e-f3e7-967d-fe14ec4256b9"
                        }
                    },
                    {
                        "key": "com.ibm.zou.resource_name",
                        "value": {
                        "stringValue": "DC17"
                        }
                    }
                    ]
                },
                "scopeLogs": [
                    {
                    "scope": {},
                    "logRecords": [
                        {
                        "timeUnixNano": "1742785814000000000",
                        "observedTimeUnixNano": "1742785814034444065",
                        "body": {},
                        "attributes": [
                            {
                            "key": "com.ibm.zou.metrics.number_of_batch_users",
                            "value": {
                                "intValue": "7"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.global_cache_hit_ratio",
                            "value": {
                                "doubleValue": 91.6
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.output_buffer_size",
                            "value": {
                                "doubleValue": 40
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.bytes_written_to_log",
                            "value": {
                                "doubleValue": 130
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.cf_global_contention",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.dist_receive_rate",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.udf_timed_out",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.number_of_db2s",
                            "value": {
                                "intValue": "1"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.lock_escalation_rate",
                            "value": {
                                "doubleValue": 0
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.current_open_dataset",
                            "value": {
                                "intValue": "65"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.timeouts",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.dist_send_rate",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.transactions_per_second",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.lock_escalation_excl",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.class_castout_thresh",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.no_qp_bp_shortage",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.thread_wait_limit",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.udf_abended",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.storage_contractions",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.db_wait_percent",
                            "value": {
                                "doubleValue": 0
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.active_stored_procedures",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.edm_pool_full",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.smf_overruns",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.indoubt_urs",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.deadlocks",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.active_triggers",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.merge_error_bp_shortage",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.lock_conflict_count",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.allowed_locks_per_ts",
                            "value": {
                                "intValue": "2000"
                            }
                            },
                            {
                            "key": "com.ibm.zou.record_type",
                            "value": {
                                "stringValue": "metric"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.ridpool_fail_no_stor_rate",
                            "value": {
                                "doubleValue": 0
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.max_active_dbats",
                            "value": {
                                "intValue": "150"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.asids_user_functions",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.pages_read_from_bps",
                            "value": {
                                "intValue": "260219"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.dsmax_approaching_max",
                            "value": {
                                "doubleValue": 0.3
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.dsmax",
                            "value": {
                                "intValue": "20000"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.rid_pool_size",
                            "value": {
                                "intValue": "1024000000"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.migrated_ds_timed_out",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.sort_degraded_bp_small",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.incomp_retained_locks",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.dsc_size",
                            "value": {
                                "intValue": "125829120"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.edm_current_pages",
                            "value": {
                                "intValue": "136"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.sort_error_bp_shortage",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.sp_timed_out",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.max_tso_users",
                            "value": {
                                "intValue": "50"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.asids_stored_procedures",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.thread_wait_lock",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.max_kept_dyn_stmt",
                            "value": {
                                "intValue": "5000"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.nonstealable_pages",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.output_buffer_full",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.udf_start_failed",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.pages_castout",
                            "value": {
                                "intValue": "1329"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.edm_utilization",
                            "value": {
                                "doubleValue": 1.3
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.tape_volume_contention",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.gbp_castout_thresh",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.checkpoint_freq",
                            "value": {
                                "intValue": "3"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.current_thread_count",
                            "value": {
                                "intValue": "6"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.max_batch_users",
                            "value": {
                                "intValue": "50"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.object_analysis_db_count",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.dwqt_reached",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.write_failed_no_storage",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.max_db2_allied_users",
                            "value": {
                                "intValue": "200"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.number_of_active_dbats",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.max_opened_ds",
                            "value": {
                                "intValue": "20000"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.edm_total_pages",
                            "value": {
                                "intValue": "10240"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.resource_unavailable",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.ridpool_fail_no_storage",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.user_waiting_threads",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.sp_start_failed_rejected",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.indoubt_threads",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.trigger_depth",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.number_of_gbp_connections",
                            "value": {
                                "intValue": "2"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.resource_timeout",
                            "value": {
                                "intValue": "30"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.lock_escalations",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.rid_pool_size_too_small",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.number_of_tso_users",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.resync_attempted",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.lock_escalation_shared",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.dm_critical_thresh",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.pages_read_from_dasd",
                            "value": {
                                "intValue": "947"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.sp_abends",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.max_degree",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.active_user_functions",
                            "value": {
                                "intValue": "0"
                            }
                            },
                            {
                            "key": "com.ibm.zou.metrics.open_ds_thresh_reached",
                            "value": {
                                "intValue": "0"
                            }
                            }
                        ],
                        "traceId": "",
                        "spanId": ""
                        }
                    ]
                    }
                ]
                }
            ]
            }
"""


def get_data_PST_CICS():
    return """
    {
        "resourceLogs": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.sos",
                            "value": {
                                "stringValue": "No"
                            }
                        },
                        {
                            "key": "cics.region.id",
                            "value": {
                                "stringValue": "T11A"
                            }
                        },
                        {
                            "key": "cics.cicsplex.name",
                            "value": {
                                "stringValue": "PETPLEX"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.table_version",
                            "value": {
                                "intValue": "1"
                            }
                        },
                        {
                            "key": "os.type",
                            "value": {
                                "stringValue": "z_os"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.asid",
                            "value": {
                                "stringValue": "02D6"
                            }
                        },
                        {
                            "key": "com.ibm.zou.source.name",
                            "value": {
                                "stringValue": "odp"
                            }
                        },
                        {
                            "key": "com.ibm.zou.collector.namespace",
                            "value": {
                                "stringValue": "z-aiops-unite"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.write_time",
                            "value": {
                                "intValue": "1740416086000000000"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.interval_seconds",
                            "value": {
                                "intValue": "300"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.rls_status",
                            "value": {
                                "stringValue": "RLS_NO"
                            }
                        },
                        {
                            "key": "com.ibm.zou.source.namespace",
                            "value": {
                                "stringValue": "omegamon"
                            }
                        },
                        {
                            "key": "cics.region.name",
                            "value": {
                                "stringValue": "CICST11A"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.any_current_ws_faults",
                            "value": {
                                "stringValue": "No"
                            }
                        },
                        {
                            "key": "com.ibm.zou.collector.version",
                            "value": {
                                "stringValue": "development"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.table_name",
                            "value": {
                                "stringValue": "cicsrov"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.origin_node",
                            "value": {
                                "stringValue": "JB0.CICST11A"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.vtam_applid",
                            "value": {
                                "stringValue": "CICST11A"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.start_time",
                            "value": {
                                "stringValue": "2025-02-20T14:02:40-04:00"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.vtam_generic_applid",
                            "value": {
                                "stringValue": "CICST11A"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.product_code",
                            "value": {
                                "stringValue": "kc5"
                            }
                        },
                        {
                            "key": "com.ibm.zou.resource_type",
                            "value": {
                                "stringValue": "CICSRegion"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.vtam_acb_open",
                            "value": {
                                "stringValue": "Yes"
                            }
                        },
                        {
                            "key": "host.id",
                            "value": {
                                "stringValue": "JB0"
                            }
                        },
                        {
                            "key": "host.arch",
                            "value": {
                                "stringValue": "s390x"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.any_current_ws_timeouts",
                            "value": {
                                "stringValue": "No"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.cics_tod_updated",
                            "value": {
                                "stringValue": "Yes"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.region_status",
                            "value": {
                                "stringValue": "N/S"
                            }
                        },
                        {
                            "key": "com.ibm.zou.collector.name",
                            "value": {
                                "stringValue": "otel-collector"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.xcfgroup",
                            "value": {
                                "stringValue": "DFHIR000"
                            }
                        },
                        {
                            "key": "cics.version",
                            "value": {
                                "stringValue": "7.4.0"
                            }
                        },
                        {
                            "key": "uuid",
                            "value": {
                                "stringValue": "96e969ac-4e71-6b40-3ce0-e75f51c90b13"
                            }
                        },
                        {
                            "key": "com.ibm.zou.resource_name",
                            "value": {
                                "stringValue": "CICST11A"
                            }
                        }
                    ]
                },
                "scopeLogs": [
                    {
                        "scope": {},
                        "logRecords": [
                            {
                                "timeUnixNano": "1740416086000000000",
                                "observedTimeUnixNano": "1740416086736987344",
                                "body": {},
                                "attributes": [
                                    {
                                        "key": "com.ibm.zou.metrics.largest_contiguous_available_oscor",
                                        "value": {
                                            "intValue": "2172"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.highest_pct_class_maxt",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.queued_remote_requests",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.maximum_tasks_percent",
                                        "value": {
                                            "intValue": "1"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.ices",
                                        "value": {
                                            "intValue": "5"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.io_rate",
                                        "value": {
                                            "doubleValue": 0
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.current_vsam_buffer_waits",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.working_set_size",
                                        "value": {
                                            "intValue": "153476"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.cics_tod_clock",
                                        "value": {
                                            "doubleValue": 46486
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.current_vsam_string_waits",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.storage_violations",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.record_type",
                                        "value": {
                                            "stringValue": "metric"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.largest_contiguous_available_lsqa",
                                        "value": {
                                            "intValue": "2272"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.worst_region_performance_index",
                                        "value": {
                                            "doubleValue": 0
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.total_queued_transactions",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.cpu_utilization",
                                        "value": {
                                            "doubleValue": 0.2
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.aids",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.page_rate",
                                        "value": {
                                            "doubleValue": 0
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.transaction_rate",
                                        "value": {
                                            "intValue": "454"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.enqueue_waits",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    }
                                ],
                                "traceId": "",
                                "spanId": ""
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """


def get_data_for_218():
    return """
    {
        "resourceLogs": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.sos",
                            "value": {
                                "stringValue": "No"
                            }
                        },
                        {
                            "key": "cics.region.id",
                            "value": {
                                "stringValue": "2TBB"
                            }
                        },
                        {
                            "key": "cics.cicsplex.name",
                            "value": {
                                "stringValue": "PETPLEX"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.table_version",
                            "value": {
                                "intValue": "1"
                            }
                        },
                        {
                            "key": "os.type",
                            "value": {
                                "stringValue": "z_os"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.asid",
                            "value": {
                                "stringValue": "02D6"
                            }
                        },
                        {
                            "key": "com.ibm.zou.source.name",
                            "value": {
                                "stringValue": "odp"
                            }
                        },
                        {
                            "key": "com.ibm.zou.collector.namespace",
                            "value": {
                                "stringValue": "z-aiops-unite"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.write_time",
                            "value": {
                                "intValue": "1740416086000000000"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.interval_seconds",
                            "value": {
                                "intValue": "300"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.rls_status",
                            "value": {
                                "stringValue": "RLS_NO"
                            }
                        },
                        {
                            "key": "com.ibm.zou.source.namespace",
                            "value": {
                                "stringValue": "omegamon"
                            }
                        },
                        {
                            "key": "cics.region.name",
                            "value": {
                                "stringValue": "CICS2TBB"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.any_current_ws_faults",
                            "value": {
                                "stringValue": "No"
                            }
                        },
                        {
                            "key": "com.ibm.zou.collector.version",
                            "value": {
                                "stringValue": "development"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.table_name",
                            "value": {
                                "stringValue": "cicsrov"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.origin_node",
                            "value": {
                                "stringValue": "JB0.CICS2TBB"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.vtam_applid",
                            "value": {
                                "stringValue": "CICS2TBB"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.start_time",
                            "value": {
                                "stringValue": "2025-02-20T14:02:40-04:00"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.vtam_generic_applid",
                            "value": {
                                "stringValue": "CICS2TBB"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.product_code",
                            "value": {
                                "stringValue": "kc5"
                            }
                        },
                        {
                            "key": "com.ibm.zou.resource_type",
                            "value": {
                                "stringValue": "CICSRegion"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.vtam_acb_open",
                            "value": {
                                "stringValue": "Yes"
                            }
                        },
                        {
                            "key": "host.id",
                            "value": {
                                "stringValue": "JB0"
                            }
                        },
                        {
                            "key": "host.arch",
                            "value": {
                                "stringValue": "s390x"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.any_current_ws_timeouts",
                            "value": {
                                "stringValue": "No"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.cics_tod_updated",
                            "value": {
                                "stringValue": "Yes"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.region_status",
                            "value": {
                                "stringValue": "N/S"
                            }
                        },
                        {
                            "key": "com.ibm.zou.collector.name",
                            "value": {
                                "stringValue": "otel-collector"
                            }
                        },
                        {
                            "key": "com.ibm.zou.omegamon.cicsrov.xcfgroup",
                            "value": {
                                "stringValue": "DFHIR000"
                            }
                        },
                        {
                            "key": "cics.version",
                            "value": {
                                "stringValue": "7.4.0"
                            }
                        },
                        {
                            "key": "uuid",
                            "value": {
                                "stringValue": "96e969ac-4e71-6b40-3ce0-e75f51c90b13"
                            }
                        },
                        {
                            "key": "com.ibm.zou.resource_name",
                            "value": {
                                "stringValue": "CICS2TBB"
                            }
                        }
                    ]
                },
                "scopeLogs": [
                    {
                        "scope": {},
                        "logRecords": [
                            {
                                "timeUnixNano": "1740416086000000000",
                                "observedTimeUnixNano": "1740416086736987344",
                                "body": {},
                                "attributes": [
                                    {
                                        "key": "com.ibm.zou.metrics.largest_contiguous_available_oscor",
                                        "value": {
                                            "intValue": "2172"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.highest_pct_class_maxt",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.queued_remote_requests",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.maximum_tasks_percent",
                                        "value": {
                                            "intValue": "1"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.ices",
                                        "value": {
                                            "intValue": "5"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.io_rate",
                                        "value": {
                                            "doubleValue": 0
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.current_vsam_buffer_waits",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.working_set_size",
                                        "value": {
                                            "intValue": "153476"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.cics_tod_clock",
                                        "value": {
                                            "doubleValue": 46486
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.current_vsam_string_waits",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.storage_violations",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.record_type",
                                        "value": {
                                            "stringValue": "metric"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.largest_contiguous_available_lsqa",
                                        "value": {
                                            "intValue": "2272"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.worst_region_performance_index",
                                        "value": {
                                            "doubleValue": 0
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.total_queued_transactions",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.cpu_utilization",
                                        "value": {
                                            "doubleValue": 0.2
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.aids",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.page_rate",
                                        "value": {
                                            "doubleValue": 0
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.transaction_rate",
                                        "value": {
                                            "intValue": "454"
                                        }
                                    },
                                    {
                                        "key": "com.ibm.zou.metrics.enqueue_waits",
                                        "value": {
                                            "intValue": "0"
                                        }
                                    }
                                ],
                                "traceId": "",
                                "spanId": ""
                            }
                        ]
                    }
                ]
            }
        ]
    }
    """


if __name__ == "__main__":

    import os

    metric_event = get_data_for_218()
    # metric_event = get_data_PST_CICS()
    # metric_event = get_data_PST_Db2()
    # otelMetricData: oteldata_util.OTELMetricData = oteldata_util.get_OTELMetricData( metric_event)
    # body = json.loads(metric_event)

    main(metric_event)
