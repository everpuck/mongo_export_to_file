#!.\.env\Scripts\python

"""
    main.py
    MONGO_EXPORT_TO_FILE

    Created by everpuck on 2018/01/22
    Copyright (c) 2018 everpuck. All rights reserved
"""


import os
import json
from pymongo import MongoClient
import config_local
from mylog import setup_logger


class FileWriter():
    """
    sample FileWriter for test
    """

    def __init__(self, path=None, prefix="", max_line_count=100, file_index=0):

        """ init

        Args:
            path: path for file to save
            prefix: file name prefix
            max_line_count: max line per file
            file_index: record file index

        Returns:
            None

        Raises:
            None
        """

        if not path:
            self.path = os.path.join(os.getcwd(), 'data')
        if not os.path.isdir(self.path):
            os.makedirs(self.path)

        self.max_line_count = max_line_count
        self.prefix = prefix
        self.line_index = 0
        self.file_index = file_index
        self.cur_file = None
        self.logger = setup_logger(logger_name='FileWriter', logger_path='log')
    
    def init_file(self,):
        is_new = False
        if self.line_index > self.max_line_count-1:
            self.file_index += 1
            self.line_index = 0
            is_new = True

        full_file_name = os.path.join(
            self.path, "{0}_{1}".format(self.prefix, self.file_index))

        if not self.cur_file:
            self.cur_file = open(full_file_name, 'a')
        else:
            if is_new:
                self.logger.info('new file index now:{0}'.format(self.file_index))
                self.cur_file.close()

                # remove if exist
                if os.path.isfile(full_file_name):
                    self.logger.info('file {} exists, remove!'.format(full_file_name))
                    os.remove(full_file_name)

                self.cur_file = open(full_file_name, 'a')
    
    def finish_file(self,):
        if self.cur_file:
            self.cur_file.close()
            self.cur_file = None

        self.logger.info('finish write file...')

    def run_write(self, line_str):
        if not line_str:
            return
        self.init_file()
        if self.cur_file:
            self.cur_file.write(line_str + '\n')
            self.line_index += 1


def main():
    fw = FileWriter(prefix="fb_people", max_line_count=10)
    client = MongoClient(config_local.DB_URI_LOCAL)
    db = client[config_local.DB_NAME_LOCAL]
    for doc in db[config_local.DB_PEOPLE_COL].find({},{
        'fb_type': 1, 'crawl_fbid': 1, 'result_json': 1, 'time': 1}):
        _id = doc.pop('_id')
        print(_id)
        fw.run_write(json.dumps(doc))

    fw.finish_file()


if __name__ == "__main__":
    main()