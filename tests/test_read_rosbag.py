import unittest

from autoware_record.record import Record


class TestGradingMetrics(unittest.TestCase):

    def test_simple_read(self):
        file_name = "~/Downloads/sample-rosbag/"
        record = Record(file_name)
        for topic, message, t in record.read_messages():
            print("{}, {}, {}".format(topic, type(message), t))

    def test_read_with_filters(self):
        file_name = "~/Downloads/sample-rosbag/"
        record = Record(file_name)
        for topic, message, t in record.read_messages('/vehicle/status/gear_status',
                                                      start_time=1614315746865701308, end_time=1614315776212543503):
            print("{}, {}, {}".format(topic, type(message), t))

    def test_read_with_interested_topics(self):
        file_name = "~/Downloads/sample-rosbag/"
        interested_topics = ['/vehicle/status/gear_status', '/clock']
        record = Record(file_name, interested_topics=interested_topics)
        for topic, message, t in record.read_messages():
            print("{}, {}, {}".format(topic, type(message), t))
