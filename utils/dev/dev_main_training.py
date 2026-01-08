"""
Training by collecting moving average
"""

import os

from markupsafe import escape

os.environ["AP_ANOMALY_DETECTION_FUNCTION_CONFIG"] = os.path.join(
    os.path.dirname(__file__),
    # "../../libs/aiops_unite_pkg/",
    # "aiops_unite/sample-config_ODP.yaml",
    "../metric_config_yaml_history/",
    "sample-config_v4.yaml",
)

import io
import logging
import os
import traceback

import flask
from aiops_training import training


def main():
    """
    Fission function stub main
    """
    metric = flask.request.headers.get("X-Fission-Params-Metric")
    queryParam = flask.request.args.get("download")

    if queryParam is not None:
        valid_queryParams = ["baseline", "raw_data"]
        if queryParam not in valid_queryParams:
            return flask.Response(f"Not a valid query Parameter: {escape(queryParam)}", status=400,content_type="text/plain")
        try:
            df = training.training(metric, queryParam)
            if df is None or not isinstance(df, dict):
                return flask.Response(
                    f"Error generating CSV for {escape(queryParam)}", status=500 , content_type="text/plain"
                )
            csv_output = io.StringIO()
            for key, it in df.items():
                csv_output.write(f"{key[2:6]}")
                it.to_csv(csv_output)
                csv_output.write("\n")
            csv_output.seek(0)
            response = flask.Response(csv_output.getvalue(), mimetype="text/csv")
            response.headers["Content-Disposition"] = (
                f"attachment; filename={queryParam}_data.csv"
            )
            return response
        except Exception as err:
            return flask.Response(
                f"Error generating CSV for {queryParam}: {err}", status=500
            )
    else:
        try:
            training.training(metric, None)
            logging.debug(f"Training done successfully for : {metric}", exc_info=True)
            resp = flask.Response(f"Training done successfully for : {escape(metric)}")
            resp.status_code = 200
        except Exception as err:
            logging.debug(f"Training failed because of : {err}", exc_info=True)
            resp = flask.Response(f"Training failed because of : {escape(err)}")
            resp.status_code = 500

        return resp


if __name__ == "__main__":
    # metric = "attributes.com.ibm.zou.metrics.hwm_common_subspace_users"
    # df = training.training(metric, None)

    cics_metric_array = [
        # "attributes.com.ibm.zou.metrics.maximum_tasks_percent",
        "attributes.com.ibm.zou.metrics.dbds_pct",
        # "attributes.com.ibm.zou.metrics.maximum_receive_sessions_in_use",
        # "attributes.com.ibm.zou.metrics.maximum_send_sessions_in_use",
        # "attributes.com.ibm.zou.metrics.sos",
        # "attributes.com.ibm.zou.metrics.storage_in_use_8",
        # "attributes.com.ibm.zou.metrics.total_receive_sessions_in_use",
        # "attributes.com.ibm.zou.metrics.total_send_sessions_in_use",
        # "attributes.com.ibm.zou.metrics.total_times_sos",
        # "attributes.com.ibm.zou.metrics.transaction_rate",
    ]

    # db2_metric_array = [
    #     "attributes.com.ibm.zou.metrics.dist_receive_rate",
    #     "attributes.com.ibm.zou.metrics.current_open_dataset",
    #     "attributes.com.ibm.zou.metrics.edm_utilization",
    # ]
    for metric in cics_metric_array:
        df = training.training(metric, None)
