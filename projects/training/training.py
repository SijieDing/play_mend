"""
Training by collecting moving average
"""

import io
import logging

import flask
from aiops_training import training


def main():
    """
    Fission function stub main
    """
    queryParam = flask.request.args.get("download")
    metricConfig = flask.request.get_json(silent=True)

    if metricConfig is None:
        logging.error("Failed to parse JSON data. Check Content-Type header.", exc_info=True)
        return flask.Response("Invalid or missing JSON data", status=400)

    if queryParam is not None:
        valid_queryParams = ["baseline", "raw_data"]
        if queryParam not in valid_queryParams:
            logging.debug(f"Not a valid query Parameter: {queryParam}", exc_info=True)
            return flask.Response("Not a valid query Parameter", status=400)
        try:
            df = training.training(metricConfig, queryParam)
            if df is None or not isinstance(df, dict):
                return flask.Response(f"Error generating CSV for {queryParam}", status=500)
            csv_output = io.StringIO()
            for key, it in df.items():
                csv_output.write(f"{key[2:6]}")
                it.to_csv(csv_output)
                csv_output.write("\n")
            csv_output.seek(0)
            response = flask.Response(csv_output.getvalue(), mimetype="text/csv")
            response.headers["Content-Disposition"] = f"attachment; filename={queryParam}_data.csv"
            return response
        except Exception as err:
            return flask.Response(f"Error generating CSV for {queryParam}: {err}", status=500)
    else:
        try:
            training.training(metricConfig, None)
            logging.debug(f"Training done successfully for : {metricConfig.get('name')}", exc_info=True)
            resp = flask.Response("Training done successfully")
            resp.status_code = 200
        except Exception as err:
            logging.debug(f"Training failed because of : {err}", exc_info=True)
            resp = flask.Response("Training failed")
            resp.status_code = 500

        return resp


if __name__ == "__main__":
    metric = {
        "name": "attributes.com.ibm.zou.metrics.DLY_AT_MAXSOCKETS",
        "timestamp": "@timestamp",
        "uuid": "resource.uuid",
        "group_bys": ["resource.cics.region.name"],
        "conditions": {
            "resource.com.ibm.zou.cdp.source.type": "ZOU_SMF110_2_COMM",
            "resource.com.ibm.zou.resource_type": "CICSRegion",
        },
        "const": 0,
        "threshold": 1,
    }
    df = training.training(metric, None)
