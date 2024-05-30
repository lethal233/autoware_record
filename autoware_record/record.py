import glob
import os
import sqlite3

import yaml
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from yaml import SafeLoader

from autoware_record.record_exception import RecordException


class Record:
    _db3_fp: str
    _yml_fp: str

    _has_routing_msg: bool

    def __init__(self, bag_dir_path: str, interested_topics=None):
        # bag_dir_path is the directory path containing the db3 and yaml files
        self.bag_dir_path = bag_dir_path
        self.metadata = None
        self._version = None
        self._size = None

        self._start_time = None
        self._end_time = None

        self.__init_fp()
        self.interested_topics = interested_topics

    def __iter__(self):
        return self.read_messages()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __del__(self):
        self.close()

    def __init_fp(self):
        self._db3_fp = self.__get_file_path(self.bag_dir_path, 'db3')
        self._yml_fp = self.__get_file_path(self.bag_dir_path, 'yaml')

    def read_messages(self, topic_name=None, start_time=None, end_time=None):
        with sqlite3.connect(self._db3_fp) as conn:
            cursor = conn.cursor()

            query_sql = """
                            SELECT topics.name AS topic, data AS message, topics.type, timestamp AS t
                            FROM messages
                            JOIN topics ON messages.topic_id = topics.id
                            WHERE 1=1
                            """
            if topic_name:
                query_sql += f" AND topics.name = ?"
            if start_time != 0 and start_time is not None:
                query_sql += " AND t >= ?"
            if end_time != -1 and end_time is not None:
                query_sql += " AND t <= ?"
            query_sql += " ORDER BY t"
            params = []
            if topic_name:
                params.append(topic_name)
            if start_time != 0 and start_time is not None:
                params.append(start_time)
            if end_time != -1 and end_time is not None:
                params.append(end_time)
            rows = cursor.execute(query_sql, params).fetchall()
            for tpc, msg, ty, timestamp in rows:
                if self.interested_topics is None:
                    yield tpc, deserialize_message(msg, get_message(ty)), timestamp
                else:
                    if tpc in self.interested_topics:
                        yield tpc, deserialize_message(msg, get_message(ty)), timestamp

    def close(self):
        self.metadata = None

    def get_start_time(self):
        if not self.metadata:
            self.open_metafile()
        self._start_time = self.metadata['rosbag2_bagfile_information']['starting_time']['nanoseconds_since_epoch']
        return self._start_time

    def get_end_time(self):
        if not self.metadata:
            self.open_metafile()
        self._end_time = self.metadata['rosbag2_bagfile_information']['starting_time']['nanoseconds_since_epoch'] + \
                         self.metadata['rosbag2_bagfile_information']['duration']['nanoseconds']
        return self._end_time

    def get_message_count(self, topics=None):
        if not self.metadata:
            self.open_metafile()
        if topics is None:
            return self.metadata['rosbag2_bagfile_information']['message_count']
        else:
            tp_msgs = self.metadata['rosbag2_bagfile_information']['topics_with_message_count']
            for tm in tp_msgs:
                if tm['topic_metadata']['name'] == topics:
                    return tm['message_count']
        raise RecordException(f"Topic {topics} not found")

    def has_routing(self):
        if not self.metadata:
            self.open_metafile()
        try:
            return self.get_message_count('/planning/mission_planning/route') > 0
        except RecordException:
            return False

    def get_version(self):
        if not self.metadata:
            self.open_metafile()
        if self._version is None:
            return self.metadata['rosbag2_bagfile_information']['version']

    @property
    def size(self):
        if self._size is None:
            self._size = os.path.getsize(self._db3_fp)
        return self._size

    @property
    def filename(self):
        return self._db3_fp

    @property
    def version(self):
        if self._version is None:
            self._version = self.get_version()
        return self._version

    def get_channel_cache(self):
        if not self.metadata:
            self.open_metafile()
        return self.metadata['rosbag2_bagfile_information']['topics_with_message_count']

    def open_metafile(self):
        if self.metadata is None:
            self.metadata = yaml.load(open(self._yml_fp, 'r'), Loader=SafeLoader)

    def __get_file_path(self, f, extension: str) -> str:
        pattern = os.path.join(f, f'*.{extension}')
        files = glob.glob(pattern)
        if len(files) == 0:
            raise Exception(f"No {extension} files found in {f}")
        return files[0]


if __name__ == '__main__':
    file_name = "/home/lori/Downloads/sample-rosbag/"
    record = Record(file_name)
    for topic, message, t in record.read_messages('/vehicle/status/gear_status',
                                                  start_time=1614315746865701308, end_time=1614315776212543503):
        print("{}, {}, {}".format(topic, type(message), t))
