"""
Detect anomalies with moving average base line
"""

import json
import traceback

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
            resp = flask.Response()
            resp.status_code = 200
    except Exception as err:
        print(f"C4Z Error: ${err}")
        print(traceback.format_exc())
        resp = flask.Response()
        resp.status_code = 200

    return resp


if __name__ == "__main__":
    metric_event = """
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
    main(metric_event)
