import pandas as pd
from flask import Flask, jsonify, request, abort
import datetime

EXCEL_PATH = "FS_Aptia_IVR_Mapping_v3 2 (1).xlsx"
SHEET_NAME = "Mapping"

# Load the Mapping sheet and convert NaNs to "N/A"
mapping_df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)
mapping_df.fillna("N/A", inplace=True)

app = Flask(__name__)

def apply_filters(df: pd.DataFrame, args: dict) -> pd.DataFrame:
    """
    Optional lightweight filtering: attach any column=value pairs
    as query parameters, e.g. ?Team=Payroll MNOPF
    """
    for col, value in args.items():
        if col in df.columns:
            df = df[df[col].astype(str) == value]
    return df

def serialize(obj):
    """Convert datetime or time objects to ISO string format"""
    if isinstance(obj, (datetime.datetime, datetime.date, datetime.time)):
        return obj.isoformat()
    return obj

@app.route("/api/mapping", methods=["GET"])
def get_mapping():
    """
    GET /api/mapping
    Optional query-string filters: any column name = exact match.
    Example: /api/mapping?Team=Payroll%20MNOPF
    """
    filtered_df = apply_filters(mapping_df.copy(), request.args)
    if filtered_df.empty:
        abort(404, description="No rows match supplied filters.")

    data = filtered_df.to_dict(orient="records")
    serialized = [{k: serialize(v) for k, v in row.items()} for row in data]

    return jsonify(serialized)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
