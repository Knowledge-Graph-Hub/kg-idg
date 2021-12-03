from koza.cli_runner import koza_app

source_name = "drugcentral-reference-map"

row = koza_app.get_row(source_name)

map = koza_app.get_map(source_name)

entry = dict()

map[row["db_id"]] = row["uri"]