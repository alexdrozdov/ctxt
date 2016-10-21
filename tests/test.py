import sys
import json
import unittest
import ctxt


class TracerKeyError(ctxt.Tracer):
    throws = (IndexError, )

    def __init__(self):
        super(TracerKeyError, self).__init__()


tracer = ctxt.Tracer()
tracer1 = ctxt.Tracer(throws=(KeyError, ))
tracer2 = TracerKeyError()


class DoSomeStuff1(object):
    @tracer.traced('Adding {v1} and {v2}')
    def process_1(self, v1, v2):
        a = {1: 2}
        str(a[3])

    @tracer.traced('Adding {v1} and {v2}')
    def process_1_1(self, v1, v2):
        with tracer.scope("v1={v1}, v2={v2}"):
            a = {1: 2}
            str(a[3])

    @tracer.traced('Adding {v1} and {v2}')
    def process_1_2(self, v1, v2):
        with tracer.scope("v1={v1}, v2={v2}", {'v1': v1, 'v2': v2}):
            a = {1: 2}
            str(a[3])

    @tracer.traced('Adding {v1} and {v2}')
    def process_2_1(self, v1, v2):
        with tracer.scope("v1={v1}, v2={v2}"):
            with tracer.scope("v1={v1}, v2={v2}"):
                a = {1: 2}
                str(a[3])

    @tracer.traced('Adding {v1} and {v2}')
    def process_2_2(self, v1, v2):
        with tracer.scope("v1={v1}, v2={v2}", {'v1': v1, 'v2': v2}):
            with tracer.scope("v1={v1}, v2={v2}"):
                a = {1: 2}
                str(a[3])

    @tracer.traced('Adding {v1} and {v2}')
    def process_3(self, v1, v2):
        self.process_1(v1, v2)

    @tracer.traced('Adding {v1} and {v2}')
    def process_3_1(self, v1, v2):
        self.process_1_1(v1, v2)

    @tracer.traced('Adding {v1} and {v2}')
    def process_3_2(self, v1, v2):
        self.process_1_2(v1, v2)

    @tracer.traced('Adding {v1} and {v2}')
    def process_3_3(self, v1, v2):
        self.process_2_1(v1, v2)

    @tracer.traced('Adding {v1} and {v2}')
    def process_3_4(self, v1, v2):
        self.process_2_2(v1, v2)

    @tracer.traced('Adding {v1} and {v2}')
    def process_4(self, v1, v2):
        with tracer.scope("v1={v1}, v2={v2}"):
            self.process_2_1(v1, v2)


class DoSomeStuff2(object):
    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_1(self, v1, v2):
        a = {1: 2}
        str(a[3])

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_1_1(self, v1, v2):
        with ctxt.Tracer.scope("v1={v1}, v2={v2}"):
            a = {1: 2}
            str(a[3])

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_1_2(self, v1, v2):
        with ctxt.Tracer.scope("v1={v1}, v2={v2}", {'v1': v1, 'v2': v2}):
            a = {1: 2}
            str(a[3])

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_2_1(self, v1, v2):
        with ctxt.Tracer.scope("v1={v1}, v2={v2}"):
            with ctxt.Tracer.scope("v1={v1}, v2={v2}"):
                a = {1: 2}
                str(a[3])

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_2_2(self, v1, v2):
        with ctxt.Tracer.scope("v1={v1}, v2={v2}", {'v1': v1, 'v2': v2}):
            with ctxt.Tracer.scope("v1={v1}, v2={v2}"):
                a = {1: 2}
                str(a[3])

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_3(self, v1, v2):
        self.process_1(v1, v2)

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_3_1(self, v1, v2):
        self.process_1_1(v1, v2)

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_3_2(self, v1, v2):
        self.process_1_2(v1, v2)

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_3_3(self, v1, v2):
        self.process_2_1(v1, v2)

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_3_4(self, v1, v2):
        self.process_2_2(v1, v2)

    @ctxt.Tracer.traced('Adding {v1} and {v2}')
    def process_4(self, v1, v2):
        with ctxt.Tracer.scope("v1={v1}, v2={v2}"):
            self.process_2_1(v1, v2)


d1 = DoSomeStuff1()
d2 = DoSomeStuff2()


class TestCase(unittest.TestCase):
    def __init__(self, method, args, kwargs, json_file):
        super(TestCase, self).__init__('test_case')
        self.maxDiff = None
        self.__method = method
        self.__args = args
        self.__kwargs = kwargs
        self.__json_file = json_file

    def setUp(self):
        print('')

    def test_case(self):
        exc = None
        with open(self.__json_file) as f:
            expected = json.load(f)
        try:
            self.__method(*self.__args, **self.__kwargs)
        except ctxt.StackTracerException as e:
            exc = e
        self.assertEqual(
            expected,
            sanitize_traceback(exc.format('dict'))
        )


def sanitize_traceback(d):
    for k, v in d.items():
        if isinstance(v, str):
            if 'Traceback' in v:
                d[k] = 'Exception Traceback goes here'
        elif isinstance(v, dict):
            sanitize_traceback(v)
    return d


def suite(test_list):
    return unittest.TestSuite([
        TestCase(
            item['method'],
            item.get('args', ()),
            item.get('kwargs', {}),
            item['file']
        )
        for item in test_list
    ])


def gen_files(test_list):
    for t in test_list:
        method = t['method']
        args = t.get('args', ())
        kwargs = t.get('kwargs', {})
        json_file = t['file']
        try:
            method(*args, **kwargs)
        except ctxt.StackTracerException as e:
            with open(json_file, 'w') as f:
                json.dump(
                    sanitize_traceback(e.format('dict')),
                    f
                )


test_list = [
    {'method': d1.process_1, 'args': (1, 2), 'file': 'tests/d1.process_1.js'},
    {'method': d1.process_1_1, 'args': (1, 2), 'file': 'tests/d1.process_1_1.js'},
    {'method': d1.process_1_2, 'args': (1, 2), 'file': 'tests/d1.process_1_2.js'},
    {'method': d1.process_2_1, 'args': (1, 2), 'file': 'tests/d1.process_2_1.js'},
    {'method': d1.process_2_2, 'args': (1, 2), 'file': 'tests/d1.process_2_2.js'},
    {'method': d1.process_3, 'args': (1, 2), 'file': 'tests/d1.process_3.js'},
    {'method': d1.process_3_1, 'args': (1, 2), 'file': 'tests/d1.process_3_1.js'},
    {'method': d1.process_3_2, 'args': (1, 2), 'file': 'tests/d1.process_3_2.js'},
    {'method': d1.process_3_3, 'args': (1, 2), 'file': 'tests/d1.process_3_3.js'},
    {'method': d1.process_3_4, 'args': (1, 2), 'file': 'tests/d1.process_3_4.js'},
    {'method': d1.process_4, 'args': (1, 2), 'file': 'tests/d1.process_4.js'},

    {'method': d2.process_1, 'args': (1, 2), 'file': 'tests/d2.process_1.js'},
    {'method': d2.process_1_1, 'args': (1, 2), 'file': 'tests/d2.process_1_1.js'},
    {'method': d2.process_1_2, 'args': (1, 2), 'file': 'tests/d2.process_1_2.js'},
    {'method': d2.process_2_1, 'args': (1, 2), 'file': 'tests/d2.process_2_1.js'},
    {'method': d2.process_2_2, 'args': (1, 2), 'file': 'tests/d2.process_2_2.js'},
    {'method': d2.process_3, 'args': (1, 2), 'file': 'tests/d2.process_3.js'},
    {'method': d2.process_3_1, 'args': (1, 2), 'file': 'tests/d2.process_3_1.js'},
    {'method': d2.process_3_2, 'args': (1, 2), 'file': 'tests/d2.process_3_2.js'},
    {'method': d2.process_3_3, 'args': (1, 2), 'file': 'tests/d2.process_3_3.js'},
    {'method': d2.process_3_4, 'args': (1, 2), 'file': 'tests/d2.process_3_4.js'},
    {'method': d2.process_4, 'args': (1, 2), 'file': 'tests/d2.process_4.js'},
]

if __name__ == '__main__':
    if len(sys.argv) == 1:
        unittest.TextTestRunner().run(suite(test_list))
    else:
        gen_files(test_list)
