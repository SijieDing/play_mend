"""
Visualize anomalies stored in OpenSearch
"""

import json

import matplotlib.pyplot as plt
import pandas as pd
from aiops_unite import config
from aiops_unite import data_opensearch
from aiops_unite import logger
from aiops_unite import opensearch
from aiops_unite import utils


def load_anomalies(opensearch_index, metric_config, date_from, date_to, data_group, record_count=10000):
    """
    Load metric anomalies from OpenSearch for specified date range and data group
    """
    # FIXME: query 10000 records, need to scroll properly
    query = {
        "fields": [
            "attributes.event.source_timestamp",
            "attributes.event.metric.expected_value",
            "attributes.event.metric.outlier",
            "attributes.event.metric.value",
        ],
        "_source": False,
        "size": record_count,
        "query": {
            "bool": {
                "filter": [
                    {"match_phrase": {"attributes.com.ibm.zou.record_type": "metric_anomaly"}},
                    {
                        "range": {
                            "attributes.event.source_timestamp": {
                                "gte": date_from,
                                "lte": date_to,
                                "format": "strict_date_optional_time",
                            }
                        }
                    },
                ]
            }
        },
    }

    for cond_key, cond_val in metric_config["conditions"].items():
        query["query"]["bool"]["filter"].append({"match_phrase": {f"{cond_key}.keyword": cond_val}})
    query["query"]["bool"]["filter"].append(
        {"match_phrase": {"attributes.event.information.group_by.keyword": metric_config["group_by"]}}
    )
    query["query"]["bool"]["filter"].append(
        {"match_phrase": {"attributes.event.information.group_data.keyword": data_group}}
    )

    # query prepared, send to opensearch
    result = opensearch.doc_search(opensearch_index, query, timeout=600)

    # transform
    anomalies = []
    for anomaly in result["hits"]["hits"]:
        anomalies.append(
            {
                "_id": anomaly["_id"],
                "source_timestamp": anomaly["fields"]["attributes.event.source_timestamp"][0],
                "value": anomaly["fields"]["attributes.event.metric.value"][0],
                "expected_value": anomaly["fields"]["attributes.event.metric.expected_value"][0],
                "outlier": anomaly["fields"]["attributes.event.metric.outlier"][0],
            }
        )

    return anomalies


def visualize_anomalies():
    """
    visualize anomalies
    """

    # adjust here what want to visualize
    # metric_config_id = 0
    # data_group = "UTCPLXJ8:J90:MVSSYS"
    metric_config_id = 15
    data_group = "DBWC"
    opensearch_anomaly_events_index = "events_from_kafka"

    gc = config.init()
    log = logger.init(gc, __name__)

    utils.object_must_have_key(gc, "opensearch_indexes.read", "configurations")
    utils.object_must_have_key(gc, "opensearch_indexes.baseline", "configurations")
    utils.object_must_have_key(gc, "training.rolling_window_size", "configurations")
    utils.object_must_have_key(gc, "training.date_range.from", "configurations")
    utils.object_must_have_key(gc, "training.date_range.to", "configurations")
    utils.object_must_have_key(gc, "training.interval", "configurations")
    utils.object_must_have_key(gc, "metrics[0].name", "configurations")

    log.info(
        f"- training index [{gc['opensearch_indexes']['read']}]\n"
        f"- baseline index [{gc['opensearch_indexes']['baseline']}]\n"
        f"- anomaly events index [{opensearch_anomaly_events_index}]\n"
        f"- date range: [{gc['change_detection']['date_range']['from']} ~ {gc['change_detection']['date_range']['to']}]"
    )

    metric_config = gc["metrics"][metric_config_id]

    # load base line
    base_line = data_opensearch.load_latest_metric_base_line(
        gc["opensearch_indexes"]["baseline"], metric_config, data_group
    )
    df_base_line = pd.DataFrame(base_line)
    print(df_base_line)

    # load anomalies
    anomalies = load_anomalies(
        opensearch_anomaly_events_index,
        metric_config,
        gc["change_detection"]["date_range"]["from"],
        gc["change_detection"]["date_range"]["to"],
        data_group,
    )
    df_anomalies = pd.DataFrame(anomalies)
    df_anomalies["source_timestamp"] = pd.to_datetime(df_anomalies["source_timestamp"])
    df_anomalies = df_anomalies.sort_values(by="source_timestamp")
    print(df_anomalies)

    # load actual metric values
    result = data_opensearch.load_metrics(
        gc["opensearch_indexes"]["read"],
        metric_config,
        gc["change_detection"]["date_range"]["from"],
        gc["change_detection"]["date_range"]["to"],
        data_group,
    )
    data = []
    for hit in result:
        if metric_config["timestamp"] in hit["fields"] and metric_config["name"] in hit["fields"]:
            data.append(
                {
                    "timestamp": hit["fields"][metric_config["timestamp"]][0],
                    "metric_value": round(hit["fields"][metric_config["name"]][0], 2),
                }
            )
    # sampling result for debugging output
    if len(data) > 10:
        log.debug(f"formatted result (10 samples of {len(data)}): {json.dumps(data[:10])}")
    elif len(data) == 0:
        log.debug("no data is applicable")
        return 1
    else:
        log.debug(f"formatted result: {json.dumps(result)}")

    # Convert data to a DataFrame
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by="timestamp")
    # Calculate the 15-minute intervals within a day
    df["time_index_no"] = (
        (df["timestamp"].dt.hour * 60 + df["timestamp"].dt.minute) // gc["training"]["interval"]
    ).astype(int)
    # Calculate the exact timestamp for each 15-minute interval
    df["time_index"] = (
        pd.to_timedelta(df["time_index_no"] * gc["training"]["interval"], unit="minutes").astype(str).str[7:]
    )
    df = pd.merge(df, df_base_line, how="left", on=["time_index", "time_index_no"])
    print(df)

    # Plot anomalies
    # plt.plot(df['timestamp'], df['metric_value'], 'g-')
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(df_anomalies["source_timestamp"], df_anomalies["value"], "ro", label="Anomaly")
    ax1.plot(df["timestamp"], df["metric_value"], label="Current value", color="blue")
    # ax1.set_xlim(gc['change_detection']['date_range']['from'], gc['change_detection']['date_range']['to'])
    ax1.plot(df["timestamp"], df["moving_max"], label="Upper threshold")
    ax1.plot(df["timestamp"], df["moving_min"], label="Lower threshold")
    ax1.plot(df["timestamp"], df["moving_avg"], label="Moving average", color="green", linestyle="dashed")
    ax1.fill_between(df["timestamp"], df["moving_max"], df["moving_min"], color="gray", alpha=0.5)
    # ax1.fill_between(df["timestamp"], 0, 1, where=df["anomaly"], color="red", alpha=0.5, label="Anomaly")
    # ax1.fill_between(df["timestamp"], 0, 1, where=df["anomaly"], color="red", alpha=0.5, label="Anomaly")
    # ax1.set_xlabel("Timestamp")
    # ax1.set_ylabel(metric_config["name"])
    ax1.grid(True)
    plt.title(f"{metric_config['name']} anomalies of {data_group}")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    visualize_anomalies()
