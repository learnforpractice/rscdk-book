import os
import sys
import json
import struct
import pytest

test_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(test_dir, '..'))

from ipyeos import log
from ipyeos import eos
from ipyeos import chaintester
from ipyeos.chaintester import ChainTester

chaintester.chain_config['contracts_console'] = True

logger = log.get_logger(__name__)

def update_auth(tester, account):
    a = {
        "account": account,
        "permission": "active",
        "parent": "owner",
        "auth": {
            "threshold": 1,
            "keys": [
                {
                    "key": 'EOS6AjF6hvF7GSuSd4sCgfPKq5uWaXvGM2aQtEUCwmEHygQaqxBSV',
                    "weight": 1
                }
            ],
            "accounts": [{"permission":{"actor":account,"permission": 'eosio.code'}, "weight":1}],
            "waits": []
        }
    }
    tester.push_action('eosio', 'updateauth', a, {account:'active'})

def init_tester():
    tester = chaintester.ChainTester()
    update_auth(tester, 'hello')
    return tester

def chain_test(fn):
    def call():
        tester = init_tester()
        ret = fn(tester)
        tester.free()
        return ret
    return call

class NewChainTester():
    def __init__(self):
        self.tester = None

    def __enter__(self):
        self.tester = init_tester()
        return self.tester

    def __exit__(self, type, value, traceback):
        self.tester.free()

test_dir = os.path.dirname(__file__)
def deploy_contract(tester, package_name):
    with open(f'{test_dir}/target/{package_name}.wasm', 'rb') as f:
        code = f.read()
    with open(f'{test_dir}/target/{package_name}.abi', 'rb') as f:
        abi = f.read()
    tester.deploy_contract('hello', code, abi)

@chain_test
def test_secondary(tester):
    deploy_contract(tester, 'secondaryindex')

    args = {}
    r = tester.push_action('hello', 'test1', args, {'hello': 'active'})
    tester.produce_block()
    r = tester.get_table_rows(True, 'hello', '', 'mydata', '', '', 10)
    logger.info("+++++++rows: %s", r)

    args = {
        'b': 222
    }
    r = tester.push_action('hello', 'test2', args, {'hello': 'active'})
    tester.produce_block()
    r = tester.get_table_rows(True, 'hello', '', 'mydata', '', '', 10)
    logger.info("+++++++rows: %s", r)

@chain_test
def test_remove(tester):
    deploy_contract(tester, 'secondaryindex')

    args = {}
    r = tester.push_action('hello', 'test1', args, {'hello': 'active'})
    tester.produce_block()
    r = tester.get_table_rows(True, 'hello', '', 'mydata', '', '', 10)
    logger.info("+++++++rows: %s", r)

    args = {
        'b': 222
    }
    r = tester.push_action('hello', 'test3', args, {'hello': 'active'})
    tester.produce_block()
    r = tester.get_table_rows(True, 'hello', '', 'mydata', '', '', 10)
    logger.info("+++++++rows: %s", r)

@chain_test
def test_offchain_find(tester: ChainTester):
    deploy_contract(tester, 'secondaryindex')

    args = {}
    r = tester.push_action('hello', 'test1', args, {'hello': 'active'})
    r = tester.get_table_rows(True, 'hello', '', 'mydata', '1', '', 10, key_type="i64", index_position="1")
    logger.info("+++++++rows: %s", r)

    r = tester.get_table_rows(True, 'hello', '', 'mydata', '22', '', 10, key_type="i64", index_position="2")
    logger.info("+++++++rows: %s", r)
    # 0x14d == 333
    r = tester.get_table_rows(True, 'hello', '', 'mydata', '0x14d', '', 10, key_type="i128", index_position="3")
    logger.info("+++++++rows: %s", r)
