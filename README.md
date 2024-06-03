# autoware_record

**autoware_record** is an Autoware ROS bag record file (in sqlite)
offline parse tool. You can use `autoware_record` to read messages from record file.

| os      | support            | remark |
|---------|--------------------|--------|
| ubuntu  | :heavy_check_mark: |        |
| mac     |                    |        |
| windows |                    |        |

## Quick start

### Dependencies

- ROS2 humble
- Python 3.10.12 or later
- [Reduced installation of Autoware](https://github.com/lethal233/autoware)

### How to use
First clone "autoware_record" to your project:

```sh
git clone https://github.com/lethal233/autoware_record.git
```

#### Demo record

You can download a Autoware demo record
from [sample-rosbag.zip](https://docs.google.com/uc?export=download&id=1VnwJx9tI3kI_cTLzP61ktuAJ1ChgygpG)

## Command line mode

**_NOTE: NOT Supported for now_**

[//]: # (You can easily get the information in the record file by the following command.)

[//]: # ()
[//]: # (#### Info)

[//]: # ()
[//]: # (`autoware_record info` will output the statistics of the record file.)

[//]: # ()
[//]: # (```shell)

[//]: # ($ autoware_record info -f example.db3)

[//]: # ()
[//]: # (record_file:         ario_0_0.db3)

[//]: # (ROS bag version:     5)

[//]: # (begin_time:          2024-01-27 18:02:22.660205)

[//]: # (end_time:            2024-01-27 18:03:20.926608)

[//]: # (duration:            58.27 s)

[//]: # (size:                113.91 MByte)

[//]: # (message_number:      91825)

[//]: # (channel_number:      572)

[//]: # ()
[//]: # (/apollo/planning                      , apollo.planning.ADCTrajectory         , 1)

[//]: # (/apollo/routing_request               , apollo.routing.RoutingRequest         , 0)

[//]: # (/apollo/monitor                       , apollo.common.monitor.MonitorMessage  , 0)

[//]: # (/apollo/routing_response              , apollo.routing.RoutingResponse        , 0)

[//]: # (/apollo/routing_response_history      , apollo.routing.RoutingResponse        , 1)

[//]: # (/apollo/localization/pose             , apollo.localization.LocalizationEstimate, 15)

[//]: # (/apollo/canbus/chassis                , apollo.canbus.Chassis                 , 15)

[//]: # (/apollo/prediction                    , apollo.prediction.PredictionObstacles , 2)

[//]: # (```)

[//]: # ()
[//]: # (#### Echo)

[//]: # ()
[//]: # (`cyber_record echo` will print the message of the specified topic to the terminal.)

[//]: # ()
[//]: # (```shell)

[//]: # ($ cyber_record echo -f example.record.00000 -t /apollo/canbus/chassis)

[//]: # ()
[//]: # (engine_started: true)

[//]: # (speed_mps: 0.0)

[//]: # (throttle_percentage: 0.0)

[//]: # (brake_percentage: 0.0)

[//]: # (driving_mode: COMPLETE_AUTO_DRIVE)

[//]: # (gear_location: GEAR_DRIVE)

[//]: # (header {)

[//]: # (  timestamp_sec: 1627031535.112813)

[//]: # (  module_name: "SimControl")

[//]: # (  sequence_num: 76636)

[//]: # (})

[//]: # (```)


## Python API

You can use `autoware_record` in the python file by importing

```python
from autoware_record.record import Record
```

## Examples

Below are some examples to help you read and write messages from record files.

## 1. Read messages

You can read messages directly from the record file in the following ways.

```python
from autoware_record.record import Record
record_file_path = "~/Downloads/sample-rosbag/"
record = Record(record_file_path)
for topic, message, t in record.read_messages():
    print("{}, {}, {}".format(topic, type(message), t))
```

The following is the output log of the program

```
/clock, <class 'rosgraph_msgs.msg._clock.Clock'>, 1614315746338218272
/sensing/imu/tamagawa/imu_raw, <class 'sensor_msgs.msg._imu.Imu'>, 1614315746340263903
/clock, <class 'rosgraph_msgs.msg._clock.Clock'>, 1614315746347214625
/vehicle/status/control_mode, <class 'autoware_auto_vehicle_msgs.msg._control_mode_report.ControlModeReport'>, 1614315746348259492
/vehicle/status/gear_status, <class 'autoware_auto_vehicle_msgs.msg._gear_report.GearReport'>, 1614315746348361304
/vehicle/status/steering_status, <class 'autoware_auto_vehicle_msgs.msg._steering_report.SteeringReport'>, 1614315746348408503
/vehicle/status/velocity_status, <class 'autoware_auto_vehicle_msgs.msg._velocity_report.VelocityReport'>, 1614315746348462066
/clock, <class 'rosgraph_msgs.msg._clock.Clock'>, 1614315746357520034
```

#### Filter Read

You can also read messages filtered by topics and time. This will improve the speed of parsing messages.

```python
from autoware_record.record import Record
file_name = "~/Downloads/sample-rosbag/"
def read_filter():
    record = Record(file_name)
    for topic, message, t in record.read_messages('/vehicle/status/gear_status',
                                                  start_time=1614315746865701308, end_time=1614315776212543503):
        print("{}, {}, {}".format(topic, type(message), t))
```

#### Speed up Read (Recommended)

Since deserialization is a time-consuming operation, you can speed up the reading process by setting the `interested_topics` parameter.

If the topic is not in the `interested_topics`, the message will not be deserialized.

https://github.com/lethal233/autoware_record/blob/4a1d722a8daf616330194fe63a1faaedb62602d7/autoware_record/record.py#L77

```python
from autoware_record.record import Record

file_name = "~/Downloads/sample-rosbag/"
interested_topics = ['/vehicle/status/gear_status', '/clock']
record = Record(file_name, interested_topics=interested_topics)
for topic, message, t in record.read_messages():
    print("{}, {}, {}".format(topic, type(message), t))
```
