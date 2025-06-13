import csv, io, json

def parse_sdn(raw_csv):
    reader = csv.reader(io.StringIO(raw_csv))
    return [
        {"uid": row[0], "name": row[1].strip(), "type": row[2], "program": row[3]}
        for row in reader
        if len(row) >= 4  # Ensure row has at least 4 columns
    ]

def to_json(cleaned):
    return json.dumps(cleaned)