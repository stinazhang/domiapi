#!/usr/bin/env python 
# -*- coding:utf-8 -*-


from base.runmethod import RunMethod
from base.get_Data import GetData
from base.common_util import CommonUtil
from base.operation_header import OperationHeader
import json, requests, unittest
import logging
from base.connect_db import OperationMysql
from base import globalvar
import re

class run_product_getById(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        '''获取新增厂商ID'''
        cls.header = OperationHeader().get_header()
        url_firm = globalvar.Base_Url + "/firm/add"
        data_firm = {"name": "测试厂商700", "code":700, "icon":" 测试厂商11", "address":"金绣国际测试地址"}
        cls.firmid = requests.post(url=url_firm, data=json.dumps(data_firm), headers=cls.header).json()['result']
        '''获取新增产品ID'''
        cls.header = OperationHeader().get_header()
        url_product = globalvar.Base_Url + "/product/add"
        data_product = {"firmId": cls.firmid, "name": "test product", "code": 800, "ability":512 }
        cls.productid = requests.post(url=url_product, data=json.dumps(data_product), headers=cls.header).json()['result']
        '''读测试用例sheet'''
        cls.data = GetData(fileName='/Users/stina/Desktop/apitest.xls', sheetName='product_getById')
        cls.run_method = RunMethod()
        cls.com_util = CommonUtil()

    def test_run_product_getById(self):
        res = None
        rows_count = self.data.get_case_lines()
        for i in range(1, rows_count):
            url = globalvar.Base_Url + self.data.get_request_url(i)
            method = self.data.get_request_method(i)
            request_data_old = self.data.get_request_data(i)
            request_data = re.sub('pid', self.productid, request_data_old)
            expect = self.data.get_expcet_data(i)
            header = self.data.is_header(i)
            if header == None:
                header = self.header
            else:
                header = json.loads(header)
            response = self.run_method.run_main(method, url, request_data.encode('utf-8'), header).json()

            # 表格里填入返回值
            write_json = str(response)
            self.data.write_response(i, write_json)

            # 与预期值做比较
            res = "state':"+ str(response['state'])
            if self.com_util.is_equal_str(expect, res) == 1:
                self.data.write_result(i, 'pass')
                logging.info("**********product_getById test success***********")
                globalvar.pass_count.append(i)
            else:
                self.data.write_result(i, 'fail')
                logging.info("**********product_getById test fail***********")
                globalvar.fail_count.append(i)

    @classmethod
    def tearDownClass(cls) -> None:
        '''删除测试产品'''
        sql_product = "SELECT id FROM product WHERE flag=0 AND (`code`<1 OR `code`>699)"
        sql_product_data = OperationMysql().search_all(sql_product)
        if sql_product_data != None:
            sql_count = sql_product_data[0]
            for i in range(sql_count):
                pid = sql_product_data[1][i]['id']
                data = json.dumps({"productId": pid})
                url = globalvar.Base_Url + '/product/del'
                requests.post(url=url, data=data, headers=cls.header)
        else:
            pass

        '''删除测试厂商'''
        sql_firm = "SELECT id FROM firm WHERE flag=0 AND (`code`<1 OR `code`>699)"
        sql_firm_data = OperationMysql().search_all(sql_firm)
        if sql_firm_data != None:
            sql_count = sql_firm_data[0]
            for i in range(sql_count):
                fid = sql_firm_data[1][i]['id']
                data = json.dumps({"firmId": fid})
                url = globalvar.Base_Url + '/firm/del'
                requests.post(url=url, data=data, headers=cls.header)
        else:
            pass



if __name__ == '__main__':
    unittest.main()