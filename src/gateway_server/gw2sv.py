import sys
sys.path.append('/home/pi/.local/lib/python3.9/site-packages')
import paho.mqtt.client as mqtt
from lib.dao import SqliteDAO
from src.shared import database
import json
import time
import os
import threading
from lib.logs import Log
import dbus  # type: ignore
import dbus.service  # type: ignore
from dbus.mainloop.glib import DBusGMainLoop  # type: ignore
from gi.repository import GLib  # type: ignore

# serverTopics = {"data_request": "farm/monitor/sensor",        OK
#                   "energy_data" : "farm/monitor/sensor",      OK
#                   "actuator_data": "farm/monitor/actuator",   OK
#                   "send_setpoint": "farm/control",
#                   "send_setpoint_ack": "farm/control", 
#                   "server_delete": "farm/sync_node",
#                   "server_delete_ack": "farm/sync_node_ack",
#                   "server_add": "farm/sync_node",
#                   "server_add_ack": "farm/sync_node_ack",
#                   "keep_alive_ack": "farm/monitor/alive"}

# SERVER_DELETE_TOPIC = "farm/sync_node"          # deprecated
# SERVER_DELETE_ACK_TOPIC = "farm/sync_node_ack"  # deprecated
# "server_add": "farm/sync_node",                 # deprecated
# "server_add_ack": "farm/sync_node_ack",

SENSOR_DATA_TOPIC = "farm/monitor/sensor"
ACTUATOR_DATA_TOPIC = "farm/monitor/actuator"
ACTUATOR_CONTROL_TOPIC = "farm/control"

SCAN_DEVICE_TOPIC = "farm/node/scan"
ADD_NODE_TOPIC = "farm/node/add"
NEW_NODE_TOPIC = "farm/node/new"
DELETE_NODE_TOPIC = "farm/node/delete"
CONFIG_NODE_TOPIC = "farm/node/config"
KEEPALIVE_ACK_TOPIC = "farm/monitor/alive"

# # ── WiFi things topics (direct MQTT from hardware) ──────────────
# WIFI_REGISTER_TOPIC = "farm/register"   # register / register_ack
# WIFI_ALIVE_TOPIC    = "farm/alive"      # keep_alive / keep_alive_ack
# WIFI_SYNC_TOPIC     = "farm/sync_node"  # gateway_add / gateway_delete + acks
# WIFI_SENSOR_TOPIC   = "farm/sensor"     # sensor_data
# WIFI_ACTUATOR_TOPIC = "farm/actuator"   # actuator_data / setpoint / setpoint_ack

BROKER_SERVER = '192.168.2.32'     # test broker
# BROKER_SERVER = '192.168.88.153'     # test broker
# BROKER_SERVER = '192.168.2.81'     # test broker
# BROKER_SERVER = '192.168.1.217'     # ip nhà Bon
PORT = 1883
KEEPALIVE = 60

# Thingsboard test
access_token = "A7OnpaZFnln7WHnVl1sS"   
DEV_TOPIC = "v1/gateway/telemetry"      

room_id = 407         # this must be taken from database

client = None       # MQTT client

bus = None
btmesh_service = None
btmesh_interface = None

def dbus_call_proxy_object():
    global btmesh_service
    global btmesh_interface
    
    try:
        btmesh_service = bus.get_object('org.ipac.btmesh', '/org/ipac/btmesh')
        btmesh_interface = dbus.Interface(btmesh_service, 'org.ipac.btmesh')
    except dbus.exceptions.DBusException:
        print('Cannot connect to BtmeshService')
        return False
    
    return True

def mqtt_recv_scan_device(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return

    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'scan_device':
            if (msg['info']['protocol'] == 'ble_mesh'):
                btmesh_interface.BtmeshScanDevice()
                db = SqliteDAO(database.location)
                unicasts = db.__do__(f"SELECT unicast FROM BTMeshNodes WHERE remote = 1")
                # result of db.__do__ is [(record1,..), (record2,..)]
                unicast_list = []
                if unicasts is None:
                    return
                for addr in unicasts:
                    unicast_list.append(addr[0])
                btmesh_interface.BtmeshRemoteScanStartAll(unicast_list)
            elif (msg['info']['protocol'] == 'wifi'):
                pass

def mqtt_recv_add_device(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return

    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'add_node':
            if (msg['info']['protocol'] == 'ble_mesh'):
                if (msg['info']['remote_prov']['enable'] == True):
                    btmesh_interface.BtmeshRemoteAddDevice(msg['info']['remote_prov']['unicast'], msg['info']['dev_info'])
                else:
                    btmesh_interface.BtmeshAddDevice(msg['info']['dev_info'])
            elif (msg['info']['protocol'] == 'wifi'):
                pass

def mqtt_recv_new_node_info(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return

    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'new_node_info_ack':
            # add node info database
            if (msg['info']['protocol'] == 'ble_mesh'):
                db = SqliteDAO(database.location)
                node_info = db.__do__(f"SELECT uuid FROM BTMeshNodes WHERE unicast = {msg['info']['dev_info']['unicast']}")
                db = SqliteDAO(database.location)
                if len(node_info) != 0:
                    uuid = node_info[0][0]
                    if uuid != msg['info']['dev_info']['uuid']:
                        print("Conflict UUIDs with node unicast")
                else:
                    # record = database.RecordMaker(msg['info']['dev_info'])
                    record = {
                        'fields': ['node_id', 'function', 'sync_state', 'protocol', 'time'],
                        'values': (msg['info']['dev_info']['node_id'], msg['info']['dev_info']['function'], 1 , msg['info']['protocol'], time.time())
                    }
                    db.insertOneRecord("Registration", record['fields'], record['values'])
                    db = SqliteDAO(database.location)
                    remote = True if (msg['info']['remote_prov']['enable'] == 1) else False
                    record = {
                        'fields': ['node_id', 'uuid', 'unicast', 'remote'],
                        'values': (msg['info']['dev_info']['node_id'], msg['info']['dev_info']['uuid'], msg['info']['dev_info']['unicast'], remote)
                    }
                    db.insertOneRecord("BTMeshNodes", record['fields'], record['values'])
                    print(f"Add new node record: {record['fields']}, {record['values']}")
                        
            elif (msg['info']['protocol'] == 'wifi'):
                pass

def mqtt_recv_delete_node(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return
            
    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'delete_node':
            if (msg['info']['protocol'] == 'ble_mesh'):
                btmesh_interface.BtmeshDeleteNode(msg['info']['dev_info'])
            elif (msg['info']['protocol'] == 'wifi'):
                pass

def mqtt_recv_actuator_control(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return
    
    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'actuator_control':
            # get unicast from database
            unicast = 6                     # fixed for test only
            actuator_target = {
                'actuator_info': {
                    'unicast': unicast,
                    'function': msg['info']['function'],
                },
                'control_state': {
                    'setpoint': msg['info']['control_state']['setpoint'],
                    'mode': msg['info']['control_state']['mode'],
                    'start_time': msg['info']['control_state']['start_time'],
                    'end_time': msg['info']['control_state']['end_time'],
                    'status': msg['info']['control_state']['status'],
                }
            }

            if (msg['info']['protocol'] == 'ble_mesh'):
                btmesh_interface.BtmeshUniversalIRController(actuator_target)
            elif (msg['info']['protocol'] == 'wifi'):
                pass

def mqtt_recv_config_node(msg):
    if btmesh_service is None or btmesh_interface is None:
        status = dbus_call_proxy_object()
        if status == False:
            return
    
    unicast = 9
    if (msg['info']['room_id'] == room_id):
        if msg['operator'] == 'config_node':
            if (msg['info']['protocol'] == 'ble_mesh'):
                dbus_msg = {
                    'unicast': unicast,
                    'relay_state': msg['info']['config']['relay'],
                }
                btmesh_interface.BtmeshRelaySet(dbus_msg)
            elif (msg['info']['protocol'] == 'wifi'):
                pass

# ── WiFi things handlers ─────────────────────────────────────────
# These are called when a WiFi hardware device publishes to the broker directly.
# The gateway receives, processes, then forwards to the existing server pipeline.

def wifi_recv_register(msg):
    """
    WiFi device registration is handled entirely by the server (scan+add UX).
    Gateway only logs the announce — do NOT publish register_ack here.
    """
    mac = msg['info'].get('mac_address')
    print(f"[WiFi] register seen from mac={mac} — server will handle ack")

def wifi_recv_keepalive(msg):
    """Thing sent keep_alive. Send keep_alive_ack back on the same topic."""
    mac     = msg['info'].get('mac_address')
    node_id = msg['info'].get('node_id')
    ack = {
        'operator': 'keep_alive_ack',
        'status': 1,
        'info': {'mac_address': mac, 'node_id': node_id, 'time': int(time.time())}
    }
    client.publish(KEEPALIVE_ACK_TOPIC, json.dumps(ack))
    print(f"[WiFi] keep_alive_ack sent to node_id={node_id}")

def wifi_recv_sync_node(msg):
    """Receive gateway_add_ack or gateway_delete_ack from the thing."""
    print(f"[WiFi] sync_node ack: operator={msg['operator']} mac={msg['info'].get('mac_address')}")

def wifi_recv_sensor_data(msg):
    """
    Receive sensor_data from WiFi thing.
    Saves to local SQLite only — server already subscribed to the same topic
    and receives the message directly, so no re-publish needed.
    """
    info = msg['info']
    try:
        db = SqliteDAO(database.location)
        record = database.RecordMaker({
            'node_id': info.get('node_id'),
            'temp':    info.get('temp')  or info.get('temperature'),
            'hum':     info.get('hum')   or info.get('humidity'),
            'light':   info.get('light') or info.get('light_intensity'),
            'co2':     info.get('co2'),
            'motion':  info.get('motion'),
            'dust':    info.get('dust')  or info.get('dust_density'),
        })
        db.insertOneRecord("SensorMonitor", record['fields'], record['values'])
    except Exception as e:
        print(f"[WiFi] SQLite insert error: {e}")
    print(f"[WiFi] sensor_data saved node_id={info.get('node_id')}")

def wifi_recv_actuator_data(msg):
    """
    Receive actuator_data or setpoint_ack from WiFi thing.
    Server already subscribed to the same topic, so no re-publish needed.
    """
    info = msg['info']
    print(f"[WiFi] actuator_data received node_id={info.get('node_id')} state={info.get('state')}")

# ─────────────────────────────────────────────────────────────────

class GatewayClient(mqtt.Client):
    def __init__(self, topic):
        super().__init__()
        self.__logger = Log(__name__)
        self.__topic = topic

    def on_connect(self, client, userdata, flags, rc):
        """Called when the broker responds to our connection request"""
        # The connection result
        if rc == 0:
            self.__logger.info("Connected to broker")
            for topic in self.__topic:
                self.subscribe(topic)
    
    def on_connect_fail(self, client, userdata):
        """Called when the client failed to connect to the broker"""
        self.__logger.info("Unconnected to broker")

    def on_disconnect(self, client, userdata, rc):
        if rc == 0:
            self.__logger.info("Gateway disconnected to broker")

    def on_message(self, client, userdata, msg):
        """Called when a message has been received on a topic that the client subscribes to"""
        print(f'[GW MQTT] topic={msg.topic} payload={msg.payload.decode()[:120]}')
        try:
            self.__msg = json.loads(msg.payload.decode())
        except Exception as e:
            print(f"[MQTT] Bad payload on {msg.topic}: {e}")
            return

        if room_id is None:
            print("Room ID is unknown.")
            return

        op = self.__msg.get('operator', '')
        topic = msg.topic

        # ── BLE mesh routing (operator-specific) ─────────────────
        if topic == SCAN_DEVICE_TOPIC and op == 'scan_device':
            mqtt_recv_scan_device(self.__msg)

        elif topic == SCAN_DEVICE_TOPIC and op == 'register':
            # WiFi device announcing itself — server handles registration, gateway only logs
            wifi_recv_register(self.__msg)

        elif topic == ADD_NODE_TOPIC and op == 'add_node':
            mqtt_recv_add_device(self.__msg)

        elif topic == NEW_NODE_TOPIC and op == 'new_node_info_ack':
            mqtt_recv_new_node_info(self.__msg)

        elif topic == DELETE_NODE_TOPIC and op == 'delete_node':
            mqtt_recv_delete_node(self.__msg)

        elif topic == CONFIG_NODE_TOPIC and op == 'config_node':
            mqtt_recv_config_node(self.__msg)

        elif topic == ACTUATOR_CONTROL_TOPIC and op == 'actuator_control':
            mqtt_recv_actuator_control(self.__msg)

        # ── WiFi MQTT device routing ──────────────────────────────
        # Registration (register_ack) is sent by the server, not the gateway.
        # Gateway only caches local telemetry for WiFi nodes.

        elif topic == KEEPALIVE_ACK_TOPIC and op == 'keep_alive':
            wifi_recv_keepalive(self.__msg)

        elif topic == SENSOR_DATA_TOPIC and op == 'sensor_data':
            wifi_recv_sensor_data(self.__msg)

        elif topic == ACTUATOR_DATA_TOPIC and op in ('actuator_data', 'setpoint_ack'):
            wifi_recv_actuator_data(self.__msg)
        # ─────────────────────────────────────────────────────────

    def on_publish(self, client, userdata, mid):
        '''Called when publish() function has been used'''
        self.__logger.info("Published successfully")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        """Publish a message on a topic"""
        self.__logger.info(f"Subscribed to {self.__topic} successfully")

class GatewayService(dbus.service.Object):
    def __init__(self, bus_name, object_path='/org/ipac/gateway'):
        bus_name = dbus.service.BusName('org.ipac.gateway', bus=bus)
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.method('org.ipac.gateway', in_signature='b', out_signature='')
    def BtmeshScanDeviceAck(self, scan_status):
        if room_id is None:
            print("Room ID is unknown.")
            return

        msg = {
            'operator': 'scan_device_ack',
            'status': (1 if (scan_status == True) else 0),
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(SCAN_DEVICE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send new node info to server')

    @dbus.service.method('org.ipac.gateway', in_signature='bq', out_signature='')
    def BtmeshRemoteScanDeviceAck(self, scan_status, unicast):
        if room_id is None:
            print("Room ID is unknown.")
            return

        msg = {
            'operator': 'remote_scan_device_ack',
            'status': (1 if (scan_status == True) else 0),
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'remote_addr': unicast,
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(SCAN_DEVICE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send new node info to server')

    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def BtmeshScanResult(self, scan_result):
        if room_id is None:
            print("Room ID is unknown.")
            return

        msg = {
            'operator': 'scan_result',
            'status': 1,
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'remote_prov': {
                    'enable': scan_result['remote'],
                    'unicast': scan_result['remote_addr'],
                },
                'dev_info': {
                    'uuid': scan_result['uuid'],
                    'device_name': scan_result['device_name'],   # this name should be assigned from device
                    'mac': scan_result['mac'],
                    'address_type': scan_result['address_type'],
                    'oob_info': scan_result['oob_info'],
                    'adv_type': scan_result['adv_type'],
                    'bearer_type': scan_result['bearer_type'],
                    'rssi': scan_result['rssi']
                }
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(SCAN_DEVICE_TOPIC, pub_msg)

        if (res[0] != 0):
            print('Cannot send new node info to server')

    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def BtmeshNewNodeInfo(self, new_node_info):
        if room_id is None:
            print("Room ID is unknown.")
            return

        msg = {
            'operator': 'new_node_info',
            'status': 1,
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'dev_info': {
                    'function': new_node_info['function'],
                    'uuid': new_node_info['uuid'],
                    'device_name': new_node_info['device_name'],   # this name should be assigned from device
                    'unicast': new_node_info['unicast'],
                }
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(NEW_NODE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send scan device result to server')

    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def BtmeshAddNodeAck(self, add_node_ack):
        if room_id is None:
            print("Room ID is unknown.")
            return

        msg = {
            'operator': 'add_node_ack',
            'status': add_node_ack['status'],
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'remote_prov': {
                    'enable': add_node_ack['remote'],
                    'unicast': add_node_ack['remote_addr'],
                },
                'dev_info': {
                    'uuid': add_node_ack['uuid'],
                    'device_name': add_node_ack['device_name'],   # this name should be assigned from device
                    'mac': add_node_ack['mac'],
                    'address_type': add_node_ack['address_type'],
                    'oob_info': add_node_ack['oob_info'],
                    'adv_type': add_node_ack['adv_type'],
                    'bearer_type': add_node_ack['bearer_type'],
                }
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(ADD_NODE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send scan device result to server')
    
    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def BtmeshDeleteNodeAck(self, delete_node_ack):
        if room_id is None:
            print("Room ID is unknown.")
            return

        db = SqliteDAO(database.location)
        node_info = db.__do__(f"SELECT node_id, uuid FROM BTMeshNodes WHERE unicast = {delete_node_ack['unicast']}")
        if len(node_info) == 0:
            print("Cannot find node info from this unicast address")
            return
        node_id = node_info[0][0]
        uuid = node_info[0][1]
        # after taking data from database, delete node if status = 1
        msg = {
            'operator': 'delete_node_ack',
            'status': delete_node_ack['status'],
            'info': {
                'room_id': room_id,
                'protocol': 'ble_mesh',
                'dev_info': {
                    'node_id': node_id,
                    'unicast': delete_node_ack['unicast'],
                    'uuid': uuid,
                }
            }
        }
        pub_msg = json.dumps(msg)
        res = client.publish(DELETE_NODE_TOPIC, pub_msg)
        if (res[0] != 0):
            print('Cannot send delete node result to server')

    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def SaveSensorData(self, sensor_data):
        if room_id is None:
            print("Room ID is unknown.")
            return

        if (sensor_data['protocol'] == 'ble_mesh'):
            data = sensor_data.get('data')
            if data is None:
                data = {
                    'pid': sensor_data.get('pid'),
                    'temp': sensor_data.get('temp'),
                    'hum': sensor_data.get('hum'),
                    'light': sensor_data.get('light'),
                    'co2': sensor_data.get('co2'),
                    'motion': sensor_data.get('motion'),
                    'dust': sensor_data.get('dust'),
                }

            db = SqliteDAO(database.location)
            node_id_rows = db.__do__(f"SELECT node_id FROM BTMeshNodes WHERE unicast = {sensor_data['unicast']}")
            node_id = -1
            if node_id_rows and node_id_rows[0] and node_id_rows[0][0] is not None:
                node_id = node_id_rows[0][0]
                db_data = dict(data)
                db_data['node_id'] = node_id
                print("NODE ID:", node_id_rows)
                record = database.RecordMaker(db_data)
                db = SqliteDAO(database.location)
                db.insertOneRecord("SensorMonitor", record['fields'], record['values'])
                print(f"Inserted sensor data record: {record['fields']}, {record['values']}")
                db = SqliteDAO(database.location)
                db.insertOneRecord("NodeHealth", ['node_id', 'battery'], (node_id, sensor_data.get('battery', -1)))
                print(f"Inserted battery data record: {sensor_data.get('battery', -1)}")
            else:
                print(f"Cannot find node ID from unicast address {sensor_data['unicast']}")

            msg = {
                'operator': 'sensor_data',
                'status': 1,
                'info': {
                    'room_id': room_id,
                    'node_id': node_id,
                    'protocol': 'ble_mesh',
                    'unicast': sensor_data['unicast'],
                    'battery': sensor_data.get('battery', -1),
                    'pid': data['pid'],
                    'temp': data['temp'],
                    'hum': data['hum'],
                    'light': data['light'],
                    'co2': data['co2'],
                    'motion': data['motion'],
                    'dust': data['dust'],
                }
            }
            pub_msg = json.dumps(msg)
            res = client.publish(SENSOR_DATA_TOPIC, pub_msg, qos=1)
            rc = res.rc if hasattr(res, 'rc') else res[0]
            if (rc != mqtt.MQTT_ERR_SUCCESS):
                print('Cannot send sensor data result to server')
            else:
                print(f"[BLE] sensor_data published to {BROKER_SERVER}:{PORT} topic={SENSOR_DATA_TOPIC}")

    @dbus.service.method('org.ipac.gateway', in_signature='a{sv}', out_signature='')
    def SaveSensorDataToThingsboard(self, sensor_data):
        if room_id is None:
            print("Room ID is unknown.")
            return

        device = None
        if sensor_data['unicast'] == 7:
            device = "ipac_sensor_node_1"
        else:
            device = "ipac_sensor_node_2"

        msg = {
            device: [
                {
                "ts": int(time.time())*1000,
                "values": {
                    "temperature": round(sensor_data['temp'], 2),
                    "humidity": round(sensor_data['hum'], 2)
                }
                }
            ],
        }
        # print("Here")
        pub_msg = json.dumps(msg)
        res = client.publish(DEV_TOPIC, pub_msg, qos=1)
        if (res[0] != 0):
            print('Cannot send sensor data result to Thingsboard')

def update_node_id():
    global room_id

    db = SqliteDAO(database.location)
    room_info = db.__do__("SELECT room_id FROM RoomInfo")
    if len(room_info) != 0:
        room_id = room_info[0][0]

def dbus_handler():
    DBusGMainLoop(set_as_default=True)
    global bus

    bus = dbus.SystemBus()
    bus_name = dbus.service.BusName('org.ipac.gateway', bus=bus)
    gw_service = GatewayService(bus_name)
    print("GatewayService is running.")
    # Start the main loop to process incoming D-Bus messages
    GLib.MainLoop().run()

def mqtt_handler():
    global client
    topic = [
        SCAN_DEVICE_TOPIC,      # BLE: scan_device / scan_result  |  WiFi: register (log only)
        ADD_NODE_TOPIC,         # BLE: add_node  |  server sends register_ack here
        NEW_NODE_TOPIC,         # BLE: new_node_info_ack
        DELETE_NODE_TOPIC,      # BLE: delete_node
        CONFIG_NODE_TOPIC,      # BLE: config_node
        KEEPALIVE_ACK_TOPIC,    # BLE+WiFi: keep_alive / keep_alive_ack
        ACTUATOR_CONTROL_TOPIC, # BLE+WiFi: actuator_control
        SENSOR_DATA_TOPIC,      # WiFi: sensor_data (cache to SQLite)
        ACTUATOR_DATA_TOPIC,    # WiFi: actuator_data / setpoint_ack
    ]

    client = GatewayClient(topic)
    # client.username_pw_set(access_token)
    client.connect(BROKER_SERVER, PORT, KEEPALIVE)
    client.loop_forever()

def main():
    mqtt_handler_thread = threading.Thread(target=mqtt_handler)
    dbus_handler_thread = threading.Thread(target=dbus_handler)

    mqtt_handler_thread.start()
    dbus_handler_thread.start()

if __name__ == '__main__':
    main()
