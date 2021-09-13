import warnings
import torch
import time
import sqlite3
from collections import OrderedDict


class Log(object):
    name = "Log useful attr"

    def dict2attr(self, d, toNp=True):
        for k, v in d.items():
            setattr(self, k, v)
        if toNp:
            self.toNumpy()
        return self

    def toNumpy(self):
        for k, v in self.__dict__.items():
            if not k.startswith("_"):
                b = getattr(self, k)
                if isinstance(b, torch.Tensor):
                    setattr(self, k, b.detach().cpu().numpy())
                elif isinstance(b, int):
                    setattr(self, k, b)


class conf2sqlite():
    def __init__(self, database='experiment.db', table='TEST'):
        super(conf2sqlite, self).__init__()
        if not database.endswith('.db'):
            database = database + '.db'
        self.database = database
        self.table = table
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()
        self.config = None
        self.id = None

    def get_time(self):
        t = time.localtime()
        _time = f'{t.tm_mon}_{t.tm_mday}_{t.tm_hour}:{t.tm_min}:{t.tm_sec}'
        return _time

    def set_id(self, key=''):
        id = {'ID':self.get_time()+key}
        self.update_dict(id)
        self.id = self.dict['ID']


    def bind(self, config):
        self.config = config
        self.dict = OrderedDict()
        for k, v in config.items():
            if not k.startswith('_'):
                self.dict[k] = self.config[k]

    def clean_dict(self, white_list=[]):
        _white_list = [int] + white_list
        for key in self.dict.keys():
            if type(self.dict[key]) == str:
                if not self.dict[key].endswith('\''):
                    self.dict[key] = f'\'{self.dict[key]}\''.replace('/', '\\')
            elif type(self.dict[key]) == bool:
                self.dict[key] = f'\'{str(self.dict[key])}\''
            elif type(self.dict[key]) not in _white_list:
                self.dict[key] = f'\'{str(self.dict[key])}\''

    def update_dict(self, dic):
        for key, value in dic.items():
            self.dict[key] = value
        self.clean_dict()
        return

    def dict2type(self, dic):
        dict_type = {}
        for key, value in dic.items():
            T = 'char(50)'
            if type(value) == int:
                T = 'INTEGER'
            elif type(value) == str:
                T = 'TEXT'
            elif type(value) == float:
                T = 'REAL'
            elif type(value) == bool:
                T = 'char(50)'
            dict_type[key] = T
        #             string.append(f'{key} {T}')
        #         return ',\n'.join(string)
        return dict_type

    def dict2string(self, dic):
        dic_type = self.dict2type(dic)
        string = []
        for key, value in dic_type.items():
            if key == 'ID':
                continue
            string.append(f'{key} {value}')
        return ', \n'.join(string)

    def dict_eq_type(self, dic):
        dic_type = self.dict2type(dic)
        string = []
        for key, value in dic_type.items():
            string.append(f'{key}={value}')
        return ' '.join(string)

    def execute(self, string):
        if type(string) == list:
            for l in string:
                results = self.cursor.execute(l)
        else:
            results = self.cursor.execute(string)
        self.conn.commit()
        return results

    def check_cols(self):
        #         ans = self.cursor.execute(f'SELECT * FROM {self.table} limit 1')
        ans = self.cursor.execute(f'PRAGMA table_info({self.table})')
        a = [row[1] for row in ans]
        new_keys = set(self.dict.keys()) - set(a)
        new_dict = {}
        for key in new_keys:
            new_dict[key] = self.dict[key]

        if len(new_dict) == 0:
            return False
        else:
            return new_dict

    def alter_table(self):
        # ALTER TABLE database_name.table_name ADD COLUMN column_def...;
        string = []
        if self.check_cols() != False:
            for key, value in self.check_cols().items():
                string.append(f"""ALTER TABLE {self.table} ADD {self.dict2string({key:value})}""")
        return string

    def create_table(self):
        assert  self.config != None, "config hasn't bind to sqlite class"
        string = f"""CREATE TABLE IF NOT EXISTS {self.table}(\nID char(50) PRIMARY KEY NOT NULL, \n{self.dict2string(self.dict)})
        """
        return string

    def update_data(self):
        """UPDATE COMPANY set SALARY = 25000.00 where ID=1"""
        self.clean_dict()
        id = self.dict['ID']
        cols = []
        for key, value in self.dict.items():
            if key == 'ID':
                continue
            cols.append(f'{key} = {value}')
        col_string = ', '.join(cols)
        string = f"""UPDATE {self.table} set {col_string} where ID={id}"""
        return string

    def insert_data(self):
        """INSERT INTO TABLE_NAME (column1, column2, column3,...columnN)
            VALUES (value1, value2, value3,...valueN);"""
        self.clean_dict()
        keys = ', '.join([str(i) for i in self.dict.keys()])
        values = ', '.join([str(i) for i in self.dict.values()])
        string = f"""INSERT OR REPLACE INTO {self.table} ({keys})
        VALUES ({values})"""
        return string

    def __del__(self):
        self.conn.close()
        
sql = conf2sqlite()








