import flask
import pandas as pd

import aiops_unite.config as config
import aiops_unite.opensearch as opensearch

app = flask.Flask(__name__)


@app.route("/baseline")
def get_baseline():
    gc = config.init()
    metric_name = "attributes.com.ibm.zou.metrics.asynchronous_requests_per_minute"
    conditionKey = "resource.com.ibm.zou.omegamon.table_name"
    conditionValue = "mcfsys"
    opensearch_index = "metrics-baselines"
    metric_config = None
    data_group = ["HSSCF10", "HSSCF10"]
    for item in gc["metrics"]:
        if item["name"] == metric_name:
            for key, val in item["conditions"].items():
                if key == conditionKey and val == conditionValue:
                    metric_config = item
    if metric_config is None:
        return flask.Response(f"Not a valid queryParam : {metric_name}", status=400)
    query = {
        "size": 1,
        "_source": True,
        "query": {
            "bool": {
                "filter": [
                    {"match_phrase": {"metric.name": metric_name}},
                    {"range": {"last_update": {"gte": "2025-04-23T00:00:00", "lte": "2025-04-23T23:59:59"}}},
                ]
            }
        },
    }
    if "group_by" in metric_config:
        query["query"]["bool"]["filter"].append(
            {"match_phrase": {f"resource.{metric_config['group_by']}.keyword": data_group[1]}}
        )
    elif "group_bys" in metric_config:
        for idx, group_by in enumerate(metric_config["group_bys"]):
            query["query"]["bool"]["filter"].append(
                {"match_phrase": {f"resource.{group_by}.keyword": data_group[idx + 1]}}
            )
    result = opensearch.doc_search(opensearch_index, query)
    if len(result["hits"]["hits"]) == 0:
        return flask.Response(f"No data in opensearch for {metric_name}", status=500)
    else:
        print(type(result["hits"]["hits"][0]["_source"]["baseline"]["time_window"]))
        df = pd.DataFrame(result["hits"]["hits"][0]["_source"]["baseline"]["time_window"])
        df.to_csv(f"baseline_{data_group[0]}_{metric_name}.csv")
        return flask.Response(f"Sucess for {metric_name}", status=200)


if __name__ == "__main__":
    app.run()