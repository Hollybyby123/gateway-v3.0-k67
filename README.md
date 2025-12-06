<!-- Improved compatibility of back to top link -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/cyborgkid0110/gateway-v2.0">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">Gateway v2.0 - Smart Building IoT Gateway</h3>

  <p align="center">
    A multi-protocol IoT gateway bridging BLE Mesh and WiFi devices to cloud services
    <br />
    <a href="#documentation"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/cyborgkid0110/gateway-v2.0/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/cyborgkid0110/gateway-v2.0/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#configuration">Configuration</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#documentation">Documentation</a>
      <ul>
        <li><a href="#software-architecture">Software Architecture</a></li>
        <li><a href="#code-execution-flow">Code Execution Flow</a></li>
        <li><a href="#main-modules">Main Modules</a></li>
        <li><a href="#development-guide">Development Guide</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

Gateway v2.0 is an IoT gateway system designed for smart building applications. It runs on Raspberry Pi and acts as a bridge between IoT devices (sensors, actuators, controllers) and cloud servers, supporting multiple communication protocols including BLE Mesh and WiFi.

The gateway implements a layered architecture with two main components:
- **Things-Gateway Layer**: Manages communication with IoT devices via BLE Mesh and WiFi protocols
- **Gateway-Server Layer**: Handles MQTT communication with cloud services and local data persistence

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python-badge]][Python-url]
* [![MQTT][MQTT-badge]][MQTT-url]
* [![Bluetooth][Bluetooth-badge]][Bluetooth-url]
* [![Raspberry Pi][RaspberryPi-badge]][RaspberryPi-url]
* [![SQLite][SQLite-badge]][SQLite-url]

### Key Features

- ✅ **BLE Mesh Support**: Full Bluetooth Mesh protocol implementation with ESP32
- ✅ **MQTT Integration**: Real-time communication with cloud services
- ✅ **D-Bus IPC**: Efficient inter-process communication between layers
- ✅ **Local Database**: SQLite storage for sensor data and device management
- ✅ **Device Provisioning**: Automated device discovery and configuration
- ✅ **Remote Provisioning**: Support for BLE Mesh remote provisioning
- ✅ **Multi-Room Support**: Room-based message filtering for multi-gateway deployments
- 🚧 **WiFi Device Support**: Architecture ready for WiFi device integration

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

To get the gateway up and running on your Raspberry Pi, follow these steps.

### Prerequisites

**Hardware Requirements:**
- Raspberry Pi 3/4 (recommended: Raspberry Pi 4B with 2GB+ RAM)
- ESP32 development board with BLE Mesh firmware
- USB cable for ESP32 connection
- MicroSD card (16GB+)
- Power supply for Raspberry Pi

**Software Requirements:**
- Raspberry Pi OS (Raspbian Buster or later)
- Python 3.7+
- MQTT Broker (Mosquitto or cloud service like Thingsboard)

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/cyborgkid0110/gateway-v2.0.git
   cd gateway-v2.0
   ```

2. Install D-Bus configuration files
   ```bash
   sudo cp cfg/*.conf /etc/dbus-1/system.d/
   sudo systemctl reload dbus
   ```

3. Create data directory
   ```bash
   mkdir -p data
   ```

4. Connect ESP32 to Raspberry Pi via USB
   ```bash
   # Verify connection
   ls /dev/ttyUSB*
   # You should see /dev/ttyUSB0 or similar
   ```

5. Configure the gateway (see [Configuration](#configuration) section)

6. Run the gateway
   ```bash
   sudo python main.py
   ```

   If want to automatic setup every time start the Raspberry Pi:
   ```base
   sudo tee /etc/systemd/system/ipac_gateway.service > /dev/null <<EOF
   [Unit]
   Description=IPAC Gateway Background Service
   After=network.target
 
   [Service]
   WorkingDirectory=/path/to/workspace                          # modify /path/to/workspace
   ExecStart=sudo /path/to/python /path/to/workspace/main.py    # and /path/to/python by `which python`
   Restart=always
   RestartSec=5
   Environment=PYTHONUNBUFFERED=1
 
   [Install]
   WantedBy=multi-user.target
   EOF
 
   sudo systemctl daemon-reload
   sudo systemctl enable ipac_gateway.service
   sudo systemctl start ipac_gateway.service
   ```

### Configuration

Edit the configuration parameters in the source files:

**MQTT Settings** (`src/gateway_server/gw2sv.py`):
```python
BROKER_SERVER = '192.168.88.192'    # Server MQTT broker IP
PORT = 1883                         # MQTT port (1883 or 8883 for TLS)
```

**Serial Settings** (`src/things_gateway/btmesh_app.py`):
```python
USB_PORT = '/dev/ttyUSB0'  # ESP32 serial port
USB_BAUDRATE = 19200       # Serial baud rate
```

**Room ID** (`src/gateway_server/gw2sv.py`):
```python
room_id = 407  # Unique identifier for this gateway
```

**Database Path** (`src/shared/database.py`):
```python
location = "./data/data.db"  # SQLite database file
```

For detailed configuration options, see [Configuration Parameters](#configuration-parameters).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### Basic Operations

**Starting the Gateway:**
```bash
sudo python main.py
```

The gateway will:
1. Initialize the SQLite database
2. Start the Gateway-Server layer (MQTT communication)
3. Start the Things-Gateway layer (BLE Mesh communication)
4. Connect to the MQTT broker
5. Begin listening for device messages

**Testing with CLI Tool:**
```bash
cd tools/btmesh
python test.py

# Available commands:
> scan_device    # Scan for BLE Mesh devices
> add_node       # Add a new device
> ac_control     # Control air conditioner
> relay_set      # Configure relay
> subscribe      # Subscribe to MQTT topics
> exit           # Exit the tool
```

### MQTT Topics

The gateway subscribes to and publishes on the following topics:

| Topic | Direction | Description |
|-------|-----------|-------------|
| `farm/node/scan` | Subscribe | Device scanning commands |
| `farm/node/add` | Subscribe | Device provisioning requests |
| `farm/node/delete` | Subscribe | Device removal requests |
| `farm/node/config` | Subscribe | Device configuration |
| `farm/control` | Subscribe | Actuator control commands |
| `farm/monitor/sensor` | Publish | Sensor data |
| `farm/monitor/actuator` | Publish | Actuator status |
| `v1/gateway/telemetry` | Publish | Thingsboard telemetry |

### Example: Adding a BLE Mesh Device

1. **Scan for devices:**
   ```bash
   # Via MQTT
   mosquitto_pub -h <broker_ip> -t "farm/node/scan" -m '{
     "operator": "scan_device",
     "status": 1,
     "info": {
       "protocol": "ble_mesh",
       "room_id": 407
     }
   }'
   ```

2. **Provision discovered device:**
   ```bash
   mosquitto_pub -h <broker_ip> -t "farm/node/add" -m '{
     "operator": "add_node",
     "status": 1,
     "info": {
       "room_id": 407,
       "protocol": "ble_mesh",
       "remote_prov": {"enable": 0, "unicast": 0},
       "dev_info": {
         "uuid": "70cf7f4757af4f038cb0ef624a632bf0",
         "device_name": "IPAC_LAB_SMART_FARM",
         "mac": "24:DC:C3:46:A1:8E",
         "address_type": 0,
         "oob_info": 0,
         "adv_type": 3,
         "bearer_type": "PB-ADV"
       }
     }
   }'
   ```

3. **Monitor sensor data:**
   ```bash
   mosquitto_sub -h <broker_ip> -t "farm/monitor/sensor"
   ```

_For more examples, please refer to the [Documentation](#documentation) section below._

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- DOCUMENTATION -->
<a id="documentation"></a>
## Documentation

### Software Architecture

The Gateway v2.0 system follows a layered architecture designed to facilitate communication between IoT devices (Things layer) and cloud servers through a Raspberry Pi gateway. The architecture consists of two main layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                          SERVER                                 │
│                    (Cloud/Thingsboard)                          │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ MQTT Protocol
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GATEWAY (Raspberry Pi)                       │
│  ┌───────────────────────┐    ┌───────────────────────────────┐ │
│  │   Gateway-Server      │◄──►│     Things-Gateway            │ │
│  │   Layer (gw2sv.py)    │    │     Layer (btmesh_app.py,     │ │
│  │                       │    │            wifi_app.py)       │ │
│  │   - MQTT Handler      │    │     - UART/Serial Handler     │ │
│  │   - D-Bus Service     │    │     - D-Bus Service           │ │
│  │   - Database Access   │    │     - BLE Mesh Protocol       │ │
│  └───────────────────────┘    └───────────────────────────────┘ │
│                    ▲   D-Bus IPC  ▲                             │
│                    └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ BLE Mesh / WiFi
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     THINGS (IoT Devices)                        |
│        Sensors, Actuators, Universal IR Controllers             │
└─────────────────────────────────────────────────────────────────┘
```

#### Things-Gateway Layer

**Location:** `src/things_gateway/`

This layer handles events and communication between IoT devices at the Things layer and the Raspberry Pi Gateway.

**Key Responsibilities:**
- **BLE Mesh Protocol Handling** (`btmesh_app.py`): Device scanning, provisioning, node configuration, sensor data reception, actuator control
- **WiFi Device Handling** (`wifi_app.py`): Reserved for WiFi-based IoT device communication

**Key Components:**
- `BluetoothMeshService`: D-Bus service exposing BLE Mesh operations
- `MeshGateway`: Core class handling serial communication with ESP32
- `UART`: Serial port management for ESP32 communication

#### Gateway-Server Layer

**Location:** `src/gateway_server/`

This layer handles events and communication between the Raspberry Pi Gateway and the Server (Cloud).

**Key Responsibilities:**
- **MQTT Communication**: Subscribe/publish on various topics for sensors, actuators, device management
- **Database Operations**: Manages local SQLite database for node registration and sensor data
- **D-Bus Client/Service**: Communicates with Things-Gateway layer via IPC

**Key Components:**
- `GatewayClient`: MQTT client for server communication
- `GatewayService`: D-Bus service exposing gateway operations

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Code Execution Flow

#### Application Entry Point

The application starts from `main.py`:

```python
# main.py flow
1. Create database (database.createDatabase())
2. Initialize tasks list with:
   - gw2sv.main (Gateway-Server handler)
   - btmesh_app.main (Things-Gateway handler)
3. Start MultiTasks (parallel processes)
4. Monthly database rotation loop
```

**Process Architecture:**
```
main.py
    │
    ├── Process 1: gw2sv.main()
    │       ├── Thread: mqtt_handler() - MQTT client loop
    │       └── Thread: dbus_handler() - D-Bus service loop
    │
    └── Process 2: btmesh_app.main()
            ├── Thread: btmesh_app() - Serial/UART communication
            └── Thread: dbus_handler() - D-Bus service loop
```

#### Inter-Process Communication (IPC) via D-Bus

The two layers communicate using the D-Bus system bus. Each layer exposes a D-Bus service and acts as a client to the other layer's service.

**D-Bus Services:**

| Service Name | Object Path | Interface | Layer |
|--------------|-------------|-----------|-------|
| `org.ipac.gateway` | `/org/ipac/gateway` | `org.ipac.gateway` | Gateway-Server |
| `org.ipac.btmesh` | `/org/ipac/btmesh` | `org.ipac.btmesh` | Things-Gateway |

**D-Bus Methods - GatewayService (`org.ipac.gateway`):**

| Method | Signature | Description |
|--------|-----------|-------------|
| `BtmeshScanDeviceAck` | `in: b` | Acknowledge scan device status |
| `BtmeshRemoteScanDeviceAck` | `in: bq` | Acknowledge remote scan status |
| `BtmeshScanResult` | `in: a{sv}` | Report scan results |
| `BtmeshNewNodeInfo` | `in: a{sv}` | Report new node information |
| `BtmeshAddNodeAck` | `in: a{sv}` | Acknowledge node addition |
| `BtmeshDeleteNodeAck` | `in: a{sv}` | Acknowledge node deletion |
| `SaveSensorData` | `in: a{sv}` | Save sensor data to database |
| `SaveSensorDataToThingsboard` | `in: a{sv}` | Send sensor data to Thingsboard |

**D-Bus Methods - BluetoothMeshService (`org.ipac.btmesh`):**

| Method | Signature | Description |
|--------|-----------|-------------|
| `BtmeshScanDevice` | `in: none` | Start device scanning |
| `BtmeshRemoteScanStartAll` | `in: aq` | Start remote scan on all nodes |
| `BtmeshAddDevice` | `in: a{sv}` | Add unprovisioned device |
| `BtmeshRemoteAddDevice` | `in: qa{sv}` | Add device via remote provisioning |
| `BtmeshDeleteNode` | `in: a{sv}` | Delete a provisioned node |
| `BtmeshRelaySet` | `in: a{sv}` | Configure relay state |
| `BtmeshUniversalIRController` | `in: a{sa{sv}}` | Control IR actuator |

#### Operation Flow Diagrams

**Overview Architecture:**

```
+-------------------------+                 +--------------------------------------+
|        Wifi App         |                 |           GatewayService             |
|-------------------------|                 |--------------------------------------|
| requirements:           |                 | requirements:                        |
| - Handle MQTT events    |  GatewayService | - Handle packets Things↔GW layer     |
|                         | ---- flow ----> | - Send packets with correct protocol |
+-----------+-------------+                 +--------------------------------------+
            |                               |                                      |
            v                               |                                      |
+-------------------------+                 |                                      |
|      WifiService        |                 |                                      |
|-------------------------|   WifiService   |                                      |
| requirements:           | <---- flow ---- |                                      |
| - Provide Wifi services |                 |                                      |
+-----------+-------------+                 |                                      |
            |                               |                                      |
            v                               |                                      |
+-------------------------+                 |                                      |
|       BTMeshApp         |                 |                                      |
|-------------------------|                 |                                      |
| requirements:           |                 |                                      |
| - Mapped ESP32 app      |  GatewayService |                                      |
|   layer                 | ---- flow ----> |                                      |
+-----------+-------------+                 |                                      |
            |                               |                                      |
            v                               |                                      |
+-------------------------+                 |                                      |
|     BTMeshService       |                 |                                      |
|-------------------------|                 |                                      |
| requirements:           |  BtmeshService  |                                      |
| - Provide BTMesh SV     | <---- flow ---- |                                      |
+-----------+-------------+                 +--------------------------------------+
                                                             |
                                                             v
                                           +---------------------------------------+
                                           |             GatewayClient             |
                                           |---------------------------------------|
                                           | requirements:                         |
                                           | - Handle packets from Server          |
                                           +---------------------------------------+


Interfaces:
+------------------+     +------------------+     +------------------+
| <<interface>>    |     | <<interface>>    |     | <<interface>>    |
| BTMeshService    |     | GatewayService   |     | WifiService      |
|------------------|     |------------------|     |------------------|
| requirements:    |     | requirements:    |     | requirements:    |
| - all APIs in    |     | - all APIs in    |     | - all APIs in    |
|   class          |     |   class          |     |   class          |
+------------------+     +------------------+     +------------------+

```

**Device Scanning Flow:**
```
Server                 gw2sv.py              btmesh_app.py           ESP32
  │                       │                        │                    │
  │─── MQTT: scan_device ─►│                       │                    │
  │                       │── D-Bus: BtmeshScan ──►│                    │
  │                       │      Device()          │── UART: scan_cmd ─►│
  │                       │                        │                    │
  │                       │                        │◄── scan_result ────│
  │                       │◄─ D-Bus: BtmeshScan ───│                    │
  │                       │      Result()          │                    │
  │◄── MQTT: scan_result ─│                        │                    │
```

**Device Provisioning Flow:**
```
Server                 gw2sv.py              btmesh_app.py           ESP32
  │                       │                        │                    │
  │─── MQTT: add_node ────►│                       │                    │
  │                       │── D-Bus: BtmeshAdd ───►│                    │
  │                       │      Device()          │── UART: add_cmd ──►│
  │                       │                        │                    │
  │                       │                        │◄── add_result ─────│
  │                       │                        │                    │
  │                       │                        │◄── new_node_info ──│
  │                       │◄─ D-Bus: BtmeshNew ────│                    │
  │                       │      NodeInfo()        │── UART: appkey ───►│
  │                       │                        │                    │
  │◄── MQTT: new_node ────│                        │◄── config_status ──│
```

**Sensor Data Flow:**
```
ESP32                btmesh_app.py              gw2sv.py               Server
  │                        │                        │                    │
  │── sensor_data_status ─►│                        │                    │
  │                        │── D-Bus: SaveSensor ──►│                    │
  │                        │      DataToThingsboard │                    │
  │                        │                        │── MQTT: telemetry ►│
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Main Modules

#### Gateway-Server Handler (gw2sv.py)

**Location:** `src/gateway_server/gw2sv.py`

Manages communication between Gateway and Server layers.

**Key Classes:**
- `GatewayClient(mqtt.Client)`: MQTT client handling server communication
- `GatewayService(dbus.service.Object)`: D-Bus service for Things-Gateway layer communication

**MQTT Topic Handlers:**

| Function | Topic | Description |
|----------|-------|-------------|
| `mqtt_recv_scan_device()` | `farm/node/scan` | Handle scan device requests |
| `mqtt_recv_add_device()` | `farm/node/add` | Handle add node requests |
| `mqtt_recv_delete_node()` | `farm/node/delete` | Handle delete node requests |
| `mqtt_recv_actuator_control()` | `farm/control` | Handle actuator control commands |
| `mqtt_recv_config_node()` | `farm/node/config` | Handle node configuration |

#### Things-Gateway Handler (btmesh_app.py)

**Location:** `src/things_gateway/btmesh_app.py`

Manages BLE Mesh network operations via serial communication with ESP32.

**Key Classes:**
- `UART`: Manages serial port connection to ESP32 (Properties: `port`, `baudrate`, `ser`; Methods: `setup_uart()`, `restart_uart()`, `close_uart()`)
- `MeshGateway`: Core class processing BLE Mesh protocol messages (`read_opcode()`: Routes incoming opcodes to appropriate handlers; Receive methods for all mesh operations)
- `BluetoothMeshService(dbus.service.Object)`: D-Bus service exposing BLE Mesh operations to other layers (Methods for scanning, provisioning, node management, actuator control)

**UART Command Functions:**

| Function | Opcode | Description |
|----------|--------|-------------|
| `scan_device_cmd()` | `0x03` | Start scanning for unprovisioned devices |
| `stop_scan_cmd()` | `0x04` | Stop scanning |
| `add_device_cmd()` | `0x05` | Start provisioning |
| `delete_node_cmd()` | `0x06` | Delete a node |
| `get_composition_data_cmd()` | `0x07` | Get node composition data |
| `add_appkey_cmd()` | `0x08` | Add application key |
| `model_app_bind_cmd()` | `0x09` | Bind model to app key |
| `model_pub_set_cmd()` | `0x0A` | Set model publication |
| `model_sub_set_cmd()` | `0x0B` | Set model subscription |
| `rpr_scan_start_cmd()` | `0x0D` | Start remote provisioning scan |
| `relay_set_cmd()` | `0x14` | Configure relay |
| `ac_control_state_set_cmd()` | `0x53` | Control air conditioner |

**State Machine:**

```
INITIAL_STATE (0) ─────► IDLE_STATE (1) ◄────► RESTART_STATE (3)
         │                     │
         └─── get_local_keys ──┘
                              │
                   ┌──────────┴──────────┐
                   │  Process opcodes    │
                   │  from serial port   │
                   └─────────────────────┘
```

Currently, get local NetKey and AppKey are unnecessary as keys are locked to ESP32. 

**wifi_app.py:**

**Location:** `src/things_gateway/wifi_app.py`

Currently empty. Reserved for future WiFi device communication implementation.

#### D-Bus Configuration Files

**Location:** `cfg/`

These configuration files allow D-Bus services to run on the system bus.

**org.ipac.gateway.conf:**

```xml
<busconfig>
  <policy user="root">
    <allow own="org.ipac.gateway"/>
    <allow send_destination="org.ipac.gateway"/>
    <allow receive_sender="org.ipac.gateway"/>
  </policy>
  <policy context="default">
    <allow send_destination="org.ipac.gateway"/>
    <allow receive_sender="org.ipac.gateway"/>
  </policy>
</busconfig>
```

**org.ipac.btmesh.conf:**

```xml
<busconfig>
  <policy user="root">
    <allow own="org.ipac.btmesh"/>
    <allow send_destination="org.ipac.btmesh"/>
    <allow receive_sender="org.ipac.btmesh"/>
  </policy>
  <policy context="default">
    <allow send_destination="org.ipac.btmesh"/>
    <allow receive_sender="org.ipac.btmesh"/>
  </policy>
</busconfig>
```

**Installation:**
```bash
sudo cp cfg/*.conf /etc/dbus-1/system.d/
sudo systemctl reload dbus
```

#### Shared Libraries

**Location:** `src/shared/`

**database.py:**

Database management module using SQLite.

**Tables:**

| Table | Description |
|-------|-------------|
| `RoomInfo` | Room identification |
| `Registration` | Node registration records |
| `NodeHealth` | Battery and health status |
| `BTMeshNodes` | BLE Mesh node details (UUID, unicast, MAC) |
| `SensorMonitor` | Sensor readings (temp, humidity, CO2, light, etc.) |
| `EnergyMonitor` | Energy consumption data |
| `ActuatorMonitor` | Actuator status monitoring |
| `ActuatorControl` | Actuator control commands |

**Key Functions:**
- `createDatabase()`: Initialize all database tables
- `createDatabaseSchedule()`: Monthly database rotation
- `RecordMaker(dict_data)`: Convert dictionary to database record format

**mesh_model.py:**

BLE Mesh model definitions based on Bluetooth SIG specifications.

**Model Categories:**
- Foundation Models (Configuration, Health, Remote Provisioning)
- Generic Models (OnOff, Level, Power, Battery, Location)
- Sensor Models
- Time and Scene Models
- Lighting Models
- Firmware Update Models

**Custom Models (Company ID: 0x02E5):**

| Model | ID | Description |
|-------|-----|-------------|
| `CUSTOM_DEVICE_INFO_SERVER_MODEL` | `0x1400` | Device info server |
| `CUSTOM_DEVICE_INFO_CLIENT_MODEL` | `0x1401` | Device info client |
| `CUSTOM_SENSOR_SERVER_MODEL` | `0x1414` | Custom sensor server |
| `CUSTOM_SENSOR_CLIENT_MODEL` | `0x1415` | Custom sensor client |
| `CUSTOM_AC_SERVER_MODEL` | `0x1416` | Air conditioner server |
| `CUSTOM_AC_CLIENT_MODEL` | `0x1417` | Air conditioner client |

**Helper Functions:**
- `read_sig_models(model_list)`: Parse SIG model IDs
- `read_vendor_models(model_list)`: Parse vendor model IDs

**mesh_codes.py:**

BLE Mesh protocol constants and status codes.

**Key Constants:**
- Bearer types: `PB_ADV`, `PB_GATT`, `PB_BEARER`
- Relay states: `RELAY_DISABLE`, `RELAY_ENABLE`, `RELAY_NOT_SUPPORTED`
- Remote provisioning status codes
- Remote provisioning link states
- Air conditioner control states

#### Functional Testing Tools

**Location:** `tools/`

**tools/btmesh/test.py:**

Interactive CLI tool for testing BLE Mesh operations via MQTT.

**Available Commands:**

| Command | Description |
|---------|-------------|
| `scan_device` | Send scan device request |
| `add_node` | Add a new node (prompts for UUID and MAC) |
| `ac_control` | Send air conditioner control command |
| `relay_set` | Configure relay state |
| `subscribe` | Subscribe to a topic |
| `exit` | Exit the program |

**Usage:**
```bash
python tools/btmesh/test.py
> scan_device
> add_node
Enter UUID: <uuid>
Enter MAC: <mac>
> exit
```

**tools/btmesh/thingsboard.py:**

Simple MQTT publisher for Thingsboard integration testing.

**Usage:**
```bash
python tools/btmesh/thingsboard.py
```

This script publishes sample telemetry data to Thingsboard server.

#### Library Modules

**Location:** `lib/`

**dao.py (SqliteDAO):**

SQLite Data Access Object providing database API.

**Methods:**

| Method | Description |
|--------|-------------|
| `createTable()` | Create a new table |
| `insertOneRecord()` | Insert a single record |
| `listAllTables()` | List all tables in database |
| `listAllColumns()` | List columns in a table |
| `listAllValuesInColumn()` | Get all values from a column |
| `updateOneRecord()` | Update a record |
| `__do__()` | Execute raw SQL query |

**logs.py (Log):**

Logging utility class.

**Log Levels:**
- `debug()`: Debug messages
- `info()`: Information flow
- `error()`: Non-tracing errors
- `exception()`: Exceptions with traceback

**Output:** `gateway.log` file

**mqtt.py:**

Base MQTT client class (abstract implementation).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Development Guide

#### Adding a New BLE Mesh Command

1. **Define opcode** in `btmesh_app.py`:
```python
OPCODE_NEW_COMMAND = 0xXX
```

> **Important:** Make sure the opcode is **unique** and does not conflict with existing opcodes. Currently, the opcode is only 1 byte (0x00-0xFF), which limits the number of commands and makes message processing more error-prone due to potential collisions. **It is recommended to upgrade the opcode to 2 bytes** in future versions to allow for a larger command space and better error detection.

2. **Create send function**:
```python
def new_command_cmd(param1, param2):
    checksum = ~(OPCODE_NEW_COMMAND + param1 + param2) & 0xFF
    msg = [OPCODE_NEW_COMMAND, param1, param2, checksum]
    send_message_to_esp32(msg, '<BBBB')
```

> **Note:** The message structure can be self-built for custom commands or follow the standard BLE Mesh message format depending on your use case. For standard mesh operations, refer to the [Bluetooth Mesh Protocol Specification](https://www.bluetooth.com/specifications/specs/mesh-protocol/) for detailed message formats. **Ensure the message structure is consistent with the ESP32 firmware implementation** to avoid communication errors.

3. **Add receive handler** in `MeshGateway` class:
```python
def recv_new_command(self):
    msg = self.ser.ser.read(X)
    # Parse message
    # Call D-Bus method if needed
```

4. **Register in `read_opcode()`**:
```python
elif (opcode == OPCODE_NEW_COMMAND):
    self.recv_new_command()
```

5. **Expose via D-Bus** (if needed):
```python
@dbus.service.method('org.ipac.btmesh', in_signature='...', out_signature='')
def BtmeshNewCommand(self, params):
    new_command_cmd(params)
```

> **D-Bus Method Definition:** For detailed information on D-Bus method signatures and parameter types, refer to the [dbus-python tutorial](https://dbus.freedesktop.org/doc/dbus-python/tutorial.html). Key signature types include:
> - `s`: string
> - `i`: 32-bit signed integer
> - `q`: 16-bit unsigned integer (uint16)
> - `b`: boolean
> - `a`: array (e.g., `as` = array of strings, `aq` = array of uint16)
> - `{sv}`: dictionary with string keys and variant values
> - `a{sv}`: array of dictionaries (commonly used for structured data)

#### Adding a New MQTT Topic Handler

1. **Define topic** in `gw2sv.py`:
```python
NEW_TOPIC = "farm/new/topic"
```

2. **Create handler function**:
```python
def mqtt_recv_new_topic(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return
    
    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'new_operator':
            btmesh_interface.BtmeshNewMethod(msg['info'])
```

3. **Add to message router** in `GatewayClient.on_message()`:
```python
elif (msg.topic == NEW_TOPIC):
    mqtt_recv_new_topic(self.__msg)
```

4. **Subscribe to topic** in `mqtt_handler()`:
```python
topic = [
    # ... existing topics
    NEW_TOPIC,
]
```

#### Adding a New Database Table

1. **Define table** in `database.py`:
```python
db.createTable("NewTable", """  id INTEGER PRIMARY KEY AUTOINCREMENT,
                                field1 TEXT,
                                field2 INTEGER,
                                time INTEGER""")
```

2. **Use in handlers**:
```python
db = SqliteDAO(database.location)
record = {
    'fields': ['field1', 'field2', 'time'],
    'values': (value1, value2, timestamp)
}
db.insertOneRecord("NewTable", record['fields'], record['values'])
```

#### Adding WiFi Device Support

To add WiFi device support, you need to create a new module similar to `btmesh_app.py` that handles WiFi-based IoT device communication. This involves setting up a D-Bus service for inter-process communication and implementing the WiFi protocol handler.

1. **Implement `wifi_app.py`**:

Create the WiFi handler module following the same architecture as `btmesh_app.py`:

```python
import threading
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

# Global variables for D-Bus communication
bus = None
gw_service = None
gw_service_interface = None

class WiFiService(dbus.service.Object):
    """D-Bus service for WiFi device operations"""
    
    def __init__(self, bus_name, object_path='/org/ipac/wifi'):
        bus_name = dbus.service.BusName('org.ipac.wifi', bus=bus)
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.method('org.ipac.wifi', in_signature='', out_signature='')
    def WiFiScanDevice(self):
        """Scan for WiFi devices on the network"""
        # Implement WiFi device discovery
        # Example: Use mDNS/Bonjour or custom UDP broadcast
        pass

    @dbus.service.method('org.ipac.wifi', in_signature='a{sv}', out_signature='')
    def WiFiAddDevice(self, device_info):
        """Add a WiFi device to the network"""
        # device_info contains: ip, mac, device_name, etc.
        pass

    @dbus.service.method('org.ipac.wifi', in_signature='a{sv}', out_signature='')
    def WiFiDeleteDevice(self, device_info):
        """Remove a WiFi device from the network"""
        pass

    @dbus.service.method('org.ipac.wifi', in_signature='a{sv}', out_signature='')
    def WiFiSendCommand(self, command_data):
        """Send command to WiFi device"""
        # Implement HTTP/MQTT/CoAP communication with device
        pass

def dbus_call_proxy_object():
    """Connect to Gateway Service D-Bus"""
    global gw_service
    global gw_service_interface
    
    try:
        gw_service = bus.get_object('org.ipac.gateway', '/org/ipac/gateway')
        gw_service_interface = dbus.Interface(gw_service, 'org.ipac.gateway')
    except dbus.exceptions.DBusException:
        print('Cannot connect to GatewayService')

def dbus_handler():
    """Initialize and run D-Bus service"""
    DBusGMainLoop(set_as_default=True)
    global bus

    bus = dbus.SystemBus()
    bus_name = dbus.service.BusName('org.ipac.wifi', bus=bus)
    wifi_service = WiFiService(bus_name)
    print("WiFiService is running.")
    GLib.MainLoop().run()

def wifi_app():
    """Main WiFi application loop"""
    # Implement WiFi device communication
    # Example: HTTP server, MQTT client, or socket server
    while True:
        # Handle incoming WiFi device data
        # Forward to Gateway Service via D-Bus
        pass

def main():
    """Entry point for WiFi module"""
    app_thread = threading.Thread(target=wifi_app)
    dbus_handler_thread = threading.Thread(target=dbus_handler)

    app_thread.start()
    dbus_handler_thread.start()

if __name__ == '__main__':
    main()
```

2. **Create D-Bus config** `cfg/org.ipac.wifi.conf`:

```xml
<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
  <policy user="root">
    <allow own="org.ipac.wifi"/>
    <allow send_destination="org.ipac.wifi"/>
    <allow receive_sender="org.ipac.wifi"/>
  </policy>
  <policy context="default">
    <allow send_destination="org.ipac.wifi"/>
    <allow receive_sender="org.ipac.wifi"/>
  </policy>
</busconfig>
```

Install the configuration:
```bash
sudo cp cfg/org.ipac.wifi.conf /etc/dbus-1/system.d/
sudo systemctl reload dbus
```

3. **Add to `main.py`**:
```python
from src.things_gateway import wifi_app
tasks.append(wifi_app.main)
```

4. **Update `gw2sv.py`** to handle WiFi protocol:

Add WiFi service proxy:
```python
wifi_service = None
wifi_interface = None

def dbus_call_wifi_proxy_object():
    global wifi_service
    global wifi_interface
    
    try:
        wifi_service = bus.get_object('org.ipac.wifi', '/org/ipac/wifi')
        wifi_interface = dbus.Interface(wifi_service, 'org.ipac.wifi')
    except dbus.exceptions.DBusException:
        print('Cannot connect to WiFiService')
        return False
    return True
```

Update MQTT handlers to support WiFi:
```python
elif (msg['info']['protocol'] == 'wifi'):
    if wifi_service is None or wifi_interface is None:
        status = dbus_call_wifi_proxy_object()
        if status == False:
            return
    wifi_interface.WiFiScanDevice()
```

#### Best Practices

1. **D-Bus Communication**:
   - Always check if service/interface is available before calling
   - Use `dbus_call_proxy_object()` to establish connection
   - Handle `DBusException` gracefully

2. **Serial Communication**:
   - Use checksums for data integrity
   - Implement retry mechanism for failed reads
   - Handle serial port disconnection gracefully

3. **MQTT Messages**:
   - Always check `room_id` to filter relevant messages
   - Use JSON format for message payloads
   - Log publication failures

4. **Database Operations**:
   - Create new `SqliteDAO` instance for each operation
   - Use parameterized queries to prevent SQL injection
   - Handle foreign key constraints properly

5. **Error Handling**:
   - Log all exceptions using the `Log` class
   - Provide meaningful error messages
   - Implement graceful degradation

6. **Testing**:
   - Use `tools/btmesh/test.py` for functional testing
   - Test D-Bus methods using `dbus-send` or `busctl`
   - Verify MQTT messages using `mosquitto_sub`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### File Structure

```
gateway-v2.0/
├── main.py                     # Application entry point
├── README.md                   # This documentation
├── cfg/
│   ├── org.ipac.btmesh.conf    # D-Bus config for BLE Mesh service
│   └── org.ipac.gateway.conf   # D-Bus config for Gateway service
├── data/
│   └── data.db                 # SQLite database (generated)
├── lib/
│   ├── dao.py                  # Database access object
│   ├── logs.py                 # Logging utility
│   └── mqtt.py                 # MQTT client base class
├── src/
│   ├── gateway_server/
│   │   └── gw2sv.py            # Gateway-Server handler
│   ├── shared/
│   │   ├── database.py         # Database management
│   │   ├── mesh_codes.py       # BLE Mesh constants
│   │   └── mesh_model.py       # BLE Mesh model definitions
│   └── things_gateway/
│       ├── btmesh_app.py       # BLE Mesh handler
│       └── wifi_app.py         # WiFi handler (reserved)
└── tools/
    └── btmesh/
        ├── test.py             # CLI testing tool
        └── thingsboard.py      # Thingsboard test publisher
```

### Configuration Parameters

| Parameter | Location | Default Value | Description |
|-----------|----------|---------------|-------------|
| **MQTT Broker** | `gw2sv.py` | `192.168.88.192` | IP address or hostname of MQTT broker server. Change to match your broker (Thingsboard, Mosquitto, etc.) |
| **MQTT Port** | `gw2sv.py` | `1883` | TCP port for MQTT (1883 unencrypted, 8883 for TLS/SSL) |
| **Serial Port** | `btmesh_app.py` | `/dev/ttyUSB0` | USB-to-Serial device path for ESP32. Use `ls /dev/tty*` to find correct port |
| **Baud Rate** | `btmesh_app.py` | `19200` | Serial communication speed (bps). Both devices must match. Higher rates (115200) possible if stable |
| **Database Path** | `database.py` | `./data/data.db` | SQLite database file path. Auto-created on first run. Ensure `data/` directory exists with write permissions |
| **Room ID** | `gw2sv.py` | `407` | Unique identifier for gateway location. Used to filter MQTT messages. Each gateway needs unique ID |

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- ROADMAP -->
## Roadmap

- [x] BLE Mesh device provisioning and configuration
- [x] MQTT integration with cloud services
- [x] D-Bus IPC for modular architecture
- [x] Local SQLite database for data persistence
- [x] Remote provisioning support
- [ ] WiFi device support implementation
- [ ] Enhanced security (MQTT TLS, device authentication)
- [ ] Web-based configuration interface
- [ ] Multi-gateway coordination
- [ ] OTA firmware updates for devices

See the [open issues](https://github.com/cyborgkid0110/gateway-v2.0/issues) for a full list of proposed features and known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top Contributors

<a href="https://github.com/cyborgkid0110/gateway-v2.0/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=cyborgkid0110/gateway-v2.0" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Project Link: [https://github.com/cyborgkid0110/gateway-v2.0](https://github.com/cyborgkid0110/gateway-v2.0)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Bluetooth SIG - Mesh Protocol Specification](https://www.bluetooth.com/specifications/specs/mesh-protocol/)
* [paho-mqtt - Python MQTT Client](https://pypi.org/project/paho-mqtt/)
* [dbus-python - D-Bus Python Bindings](https://dbus.freedesktop.org/doc/dbus-python/)
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/cyborgkid0110/gateway-v2.0.svg?style=for-the-badge
[contributors-url]: https://github.com/cyborgkid0110/gateway-v2.0/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/cyborgkid0110/gateway-v2.0.svg?style=for-the-badge
[forks-url]: https://github.com/cyborgkid0110/gateway-v2.0/network/members
[stars-shield]: https://img.shields.io/github/stars/cyborgkid0110/gateway-v2.0.svg?style=for-the-badge
[stars-url]: https://github.com/cyborgkid0110/gateway-v2.0/stargazers
[issues-shield]: https://img.shields.io/github/issues/cyborgkid0110/gateway-v2.0.svg?style=for-the-badge
[issues-url]: https://github.com/cyborgkid0110/gateway-v2.0/issues
[license-shield]: https://img.shields.io/github/license/cyborgkid0110/gateway-v2.0.svg?style=for-the-badge
[license-url]: https://github.com/cyborgkid0110/gateway-v2.0/blob/main/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png

<!-- Technology Badges -->
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[MQTT-badge]: https://img.shields.io/badge/MQTT-660066?style=for-the-badge&logo=mqtt&logoColor=white
[MQTT-url]: https://mqtt.org/
[Bluetooth-badge]: https://img.shields.io/badge/Bluetooth-0082FC?style=for-the-badge&logo=bluetooth&logoColor=white
[Bluetooth-url]: https://www.bluetooth.com/
[RaspberryPi-badge]: https://img.shields.io/badge/Raspberry%20Pi-A22846?style=for-the-badge&logo=raspberrypi&logoColor=white
[RaspberryPi-url]: https://www.raspberrypi.org/
[SQLite-badge]: https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white
[SQLite-url]: https://www.sqlite.org/ 