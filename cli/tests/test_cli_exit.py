from appsec_cli.main import severity_blocks


def test_severity_blocks_thresholds():
    assert severity_blocks("critical", "critical")
    assert severity_blocks("high", "high")
    assert not severity_blocks("medium", "high")
