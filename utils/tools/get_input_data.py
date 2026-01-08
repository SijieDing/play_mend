import io

import flask
import pandas as pd

import aiops_unite.config as config
import aiops_unite.data_opensearch as data_opensearch

app = flask.Flask(__name__)


@app.route("/raw_value")
def get_data():
    gc = config.init()
    metric_name = "attributes.com.ibm.zou.metrics.asynchronous_requests_per_minute"
    conditionKey = "resource.com.ibm.zou.omegamon.table_name"
    conditionValue = "mcfsys"
    opensearch_index = "unite-metrics"
    date_from = "2025-02-06T08:12:40.480578+00:00"
    date_to = "2025-04-23T23:59:58.480578+00:00"
    metric_config = None
    data_group = ["HSSCF10", "HSSCF10"]
    for item in gc["metrics"]:
        if item["name"] == metric_name:
            for key, val in item["conditions"].items():
                if key == conditionKey and val == conditionValue:
                    metric_config = item
    if metric_config is None:
        return flask.Response(f"Not a valid queryParam : {metric_name}", status=400)

    raw_value = data_opensearch.load_metrics(
        opensearch_index,
        metric_config,
        date_from,
        date_to,
        data_group,
        **(
            {"global_training_exclusion": gc["training"]["global_training_exclusion"]}
            if "global_training_exclusion" in gc["training"]
            else {}
        ),
    )

    data = []
    for hit in raw_value:
        if metric_config["timestamp"] in hit["fields"] and metric_config["name"] in hit["fields"]:
            data.append(
                {
                    "timestamp": hit["fields"][metric_config["timestamp"]][0],
                    "metric_value": round(hit["fields"][metric_config["name"]][0], 2),
                }
            )
    csv_output = io.StringIO()
    df = pd.DataFrame(data)
    if df is None:
        return flask.Response(f"Error generating CSV for {metric_name}", status=500)

    df.to_csv(f"raw_value_{data_group[1]}_{metric_name}.csv")
    response = flask.Response(csv_output.getvalue(), mimetype="text/csv")
    filename = f"raw_value_{data_group[1]}_{metric_name}.csv"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


if __name__ == "__main__":
    app.run()
