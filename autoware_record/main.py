import argparse
import sys
import logging

from datetime import datetime

from autoware_record.record import Record

kGB = 1 << 30
kMB = 1 << 20
kKB = 1 << 10


def cyber_record_info(record_file):
    if record_file is None:
        print("Usage: autoware_record info -f file")
        return

    record = Record(record_file)
    print("record_file:         {}".format(record.filename))
    print("ROS bag version:     {}".format(record.version))
    print("begin_time:          {}".format(
        datetime.fromtimestamp(record.get_start_time() / 1e9)))
    print("end_time:            {}".format(
        datetime.fromtimestamp(record.get_end_time() / 1e9)))
    print("duration:            {:.2f} s".format(
        (record.get_end_time() - record.get_start_time()) / 1e9))

    # size
    if record.size > kGB:
        print("size:                {:.2f} GByte".format(record.size / kGB))
    elif record.size > kMB:
        print("size:                {:.2f} MByte".format(record.size / kMB))
    elif record.size > kKB:
        print("size:                {:.2f} KByte".format(record.size / kKB))
    else:
        print("size:                {:.2f} Byte".format(record.size))

    print("message_number:      {}".format(record.get_message_count()))
    print("channel_number:      {}".format(len(record.get_channel_cache())))

    # Empty line
    print()
    for channel in record.get_channel_cache():
        print("{:<38}, {:<38}, {}".format(
            channel['topic_metadata']['name'],
            channel['topic_metadata']['type'],
            channel['message_count']))


def cyber_record_echo(record_file, message_topic):
    if record_file is None or message_topic is None:
        print("Usage: autoware_record echo -f file -t topic")
        return

    record = Record(record_file)
    for topic, message, t in record.read_messages(topic_name=message_topic):
        print("{}".format(message))


def display_usage():
    print("Usage: autoware_record <command> [<args>]")
    print("The cyber_record commands are:")
    print("\tinfo\tShow information of an exist record.")
    print("\techo\tPrint message to console.")


def main(args=sys.argv):
    if len(args) <= 2:
        display_usage()
        return

    parser = argparse.ArgumentParser(
        description="autoware_record is a cyber record file offline parse tool.",
        prog="main.py")

    parser.add_argument(
        "-f", "--file", action="store", type=str, required=False,
        nargs='?', const="", help="cyber record file")
    parser.add_argument(
        "-t", "--topic", action="store", type=str, required=False,
        nargs='?', const="", help="cyber message topic")
    parser.add_argument(
        "-m", "--msg_type", action="store", type=str, required=False,
        nargs='?', const="", help="record message type")

    func = args[1]
    args = parser.parse_args(args[2:])
    if func == "info":
        cyber_record_info(args.file)
    elif func == "echo":
        cyber_record_echo(args.file, args.topic)
    else:
        logging.error("Unrecognized parameter type!")
