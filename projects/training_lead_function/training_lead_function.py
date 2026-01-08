"""
Training by collecting moving average
"""

import flask
from aiops_lead_function import lead_function


def main():
    """
    Fission function stub main
    """

    try:
        url = "http://ap-anomaly-detection-training-function-service:8888"
        lead_function.lead_function(url)
        resp = flask.Response("Training Lead Function triggered successfully")
        resp.status_code = 200
    except Exception as err:
        resp = flask.Response(f"lead function for training failed with error {err}")
        resp.status_code = 500

    return resp


if __name__ == "__main__":
    url = "http://ap-anomaly-detection-training-function-service:8888"
    lead_function.lead_function(url)
