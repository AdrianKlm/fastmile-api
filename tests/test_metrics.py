from fastmile_api.metrics import render_metrics
from fastmile_api.scraper import parse_snapshot
from tests.test_scraper import HTML


def test_render_metrics_includes_core_router_state():
    snapshot = parse_snapshot(HTML)
    output = render_metrics(snapshot)

    assert 'fastmile_router_device_info{model="ODU - Multiband - 4G05-B",software_version="FASTMILE2_D020110B83T0101M01E0153S",lock_status="Normal"} 1' in output
    assert 'fastmile_router_online 1' in output
    assert 'fastmile_router_traffic_gb{interface="eth",direction="download"} 0.256' in output
    assert 'fastmile_router_traffic_gb{interface="lte",direction="upload"} 0.256' in output
    assert 'fastmile_router_ca_band{direction="dl",band="3"} 1' in output
    assert 'fastmile_router_ca_band{direction="dl",band="1"} 1' in output
    assert 'fastmile_router_primary_cell_rsrp -106' in output
    assert 'fastmile_router_secondary_cell_rsrp{index="0"} -110' in output
    assert 'fastmile_router_available_cell_rsrp{index="0"} -56' in output
