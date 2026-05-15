from fastmile_api.scraper import parse_snapshot


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


def test_parse_snapshot_extracts_full_status_payload():
    snapshot = parse_snapshot(HTML)

    assert snapshot.device.model == "ODU - Multiband - 4G05-B"
    assert snapshot.device.software_version == "FASTMILE2_D020110B83T0101M01E0153S"
    assert snapshot.device.serial_number == "FSH22010081D"
    assert snapshot.device.imei == "356088101152952"
    assert snapshot.device.imsi == "260032773115333"
    assert snapshot.device.mac == "AA:BB:CC:DD:EE:FF"
    assert snapshot.device.lock_status == "Normal"

    assert snapshot.lte.ca.enb == 291067
    assert snapshot.lte.ca.cid == 53
    assert snapshot.lte.ca.dl_bands == [3, 1]
    assert snapshot.lte.ca.ul_bands == [3]

    assert snapshot.lte.active[0].pci == 131
    assert snapshot.lte.active[0].earfcn == 1725
    assert snapshot.lte.active[0].cell_type == "CellPrimary"
    assert snapshot.lte.active[0].rsrp == -106
    assert snapshot.lte.active[0].rsrq == -13
    assert snapshot.lte.active[0].rssi == -74
    assert snapshot.lte.active[0].sinr == 6

    assert snapshot.lte.active[1].pci == 311
    assert snapshot.lte.active[1].cell_type == "CellSecondary"

    assert snapshot.lte.available[0].pci == 470
    assert snapshot.lte.available[0].earfcn == 150
    assert snapshot.lte.available[0].rsrp == -56
    assert snapshot.lte.available[0].rsrq == -14
    assert snapshot.lte.available[0].rssi == -31
    assert snapshot.lte.available[0].sinr == 30

    assert snapshot.apns[0].name == "internet"
    assert snapshot.apns[0].ipv4 == "10.0.0.2"
    assert snapshot.apns[0].ipv6 is None

    assert snapshot.data.eth.download.unit == "MB"
    assert snapshot.data.eth.download.val_gb == 0.256
    assert snapshot.data.lte.upload.unit == "MB"
