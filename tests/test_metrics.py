from fastmile_api.metrics import render_metrics
from fastmile_parser.scraper import parse_snapshot


HTML = """
<html>
  <div id="model-value">ODU - Multiband - 4G05-B</div>
  <div id="software-version-val">FASTMILE2_D020110B83T0101M01E0153S</div>
  <div id="sn-value">FSH22010081D</div>
  <div id="imei-value">356088101152952</div>
  <div id="imsi-name-value">260032773115333</div>
  <div id="eth-mac-value">AA:BB:CC:DD:EE:FF</div>
  <div id="lockStatus-name-value">Normal</div>

  <div id="attached-cell-val">eNBID: <span>291067</span> Cell ID: <span>53</span> Band: <span>3</span></div>
  <div id="bandDL-val">B1</div>
  <div id="bandUL-val">CA Not Available</div>

  <!-- Primary Cell information card -->
  <div class="card-sevencol-grid">
    <div class="name-of-value-in-card-bold">131</div>
    <div class="name-of-value-in-card-bold">1725</div>
    <div class="name-of-value-in-card-bold">CellPrimary</div>
    <div class="name-of-value-in-card-bold">-106</div>
    <div class="name-of-value-in-card-bold">-13</div>
    <div class="name-of-value-in-card-bold">-74</div>
    <div class="name-of-value-in-card-bold">6</div>
  </div>

  <!-- Secondary Cell information card -->
  <div class="card-sevencol-grid">
    <div class="name-of-value-in-card-bold">311</div>
    <div class="name-of-value-in-card-bold">75</div>
    <div class="name-of-value-in-card-bold">CellSecondary</div>
    <div class="name-of-value-in-card-bold">-110</div>
    <div class="name-of-value-in-card-bold">-14</div>
    <div class="name-of-value-in-card-bold">-77</div>
    <div class="name-of-value-in-card-bold">3</div>
  </div>

  <!-- LTE stats -->
  <div class="LTE"><div class="bytes">1.5 GB</div><div class="bytes">256 MB</div></div>
  <div class="Ethernet"><div class="bytes">256 MB</div><div class="bytes">1.5 GB</div></div>

  <!-- APNs card -->
  <div class="apns-section">
    <div></div><div></div>
    <div>internet</div><div>10.0.0.2</div><div>::</div>
  </div>

  <!-- Available cells grid (*x6) -->
  <div id="available-cell-id-0">470</div>
  <div id="available-earfcn-0">150</div>
  <div id="rsrp-0">-56</div>
  <div id="rsrq-0">-14</div>
  <div id="rssi-0">-31</div>
  <div id="sinr-0">30</div>
</html>
"""


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
