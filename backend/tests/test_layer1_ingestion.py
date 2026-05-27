import pytest
from app.layers.ingestion import IngestionLayer

SAMPLE_CSV = """Flow Duration,Total Fwd Packets,Total Backward Packets,Total Length of Fwd Packets,Total Length of Bwd Packets,Flow Bytes/s,Flow Packets/s,Fwd Packet Length Mean,Bwd Packet Length Mean,Flow IAT Mean,Fwd IAT Mean,Bwd IAT Mean,Fwd PSH Flags,Bwd PSH Flags,Fwd URG Flags,Bwd URG Flags,Destination Port,Average Packet Size
120,10,5,300,150,100.5,25.3,30.0,30.0,5.0,3.0,4.0,0,0,0,0,80,20.0
"""

def test_ingestion_success():
    layer = IngestionLayer()
    result = layer.run(SAMPLE_CSV)
    assert result["status"] == "OK"
    assert result["row_count"] == 1
    assert "ips" in result
    assert "dataframe" in result

def test_ingestion_missing_columns():
    bad_csv = "col1,col2\n1,2\n"
    layer = IngestionLayer()
    result = layer.run(bad_csv)
    assert result["status"] == "ERROR"
    assert "Missing columns" in result["error"]

def test_ips_generated_if_absent():
    layer = IngestionLayer()
    result = layer.run(SAMPLE_CSV)
    assert len(result["ips"]) == result["row_count"]
