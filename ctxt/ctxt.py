import re
import inspect
import traceback
import functools
import collections
from contextlib import contextmanager


try:
    from future_builtins import zip
except ImportError:
    try:
        from itertools import izip as zip
    except ImportError:
        pass


class StackTracerException(Exception):
    def __init__(self, sub_exc=None, text=None, params_map=None):
        self.__sub_exc = sub_exc
        self.__text = text
        self.__params_map = {} if params_map is None else params_map

    def params(self):
        return self.__params_map

    def format(self, fmt):
        assert fmt in ['dict', 'dict-short']
        s = {}
        if self.__text:
            if self.__params_map:
                s['text'] = self.__text.format(**self.__params_map)
            else:
                s['text'] = self.__text
        if self.__sub_exc:
            s['sub_exc'] = self.__sub_exc.format('dict')
        return s

    def __str__(self):
        return str(self.format('dict'))


class Tracer(object):
    """Tracer  - provides context managers and decorators to trace semantics
    of method call stack.

    Tracer methods can be used to provide more details on exceptions occured
    during some data processing. Context managers and method decorators store
    some textual inforamtion about each particular method call aside with
    variables and method arguments values. In case of exception occures they
    format call stack with texts and variable values.
    This provides additional semantics on the context when exception occured.

    Class methods can be used either as static class methods or method of normal
    class instance.

    Attributes:
        throws (tuple of Exceptions, optional): optional tuple with exception to
            ignore. When exception occures its tested to be in tuple and is
            reraised without additional processing. If `throws` attribute is
            decided to be used, its better to subclass Tracer and define this
            attribute in subclass only

    Note:
        `throws` attribute is expected to be used for static class methods only.
        When normal Tracer instance may be provided it will be better to list
        expected exceptions while constructing it
    """

    def __init__(self, throws=None):
        """Construct new Tracer instance.

        Args:
            throws (tuple of Exceptions, optional): optional tuple with
                exceptions to ignore. When exception from this tuple occures its
                ignored and reraised for further caller processing
        """

        self.__throws = () if throws is None else tuple(throws)
        self.traced = self.__traced_inst
        self.scope = self.__scope_inst

    @classmethod
    def traced(cls, text_spec):
        """traced - Decorates function or method with some semantic details

        Handles decorated function call context and formats exception details
        if function fails

        Args:
            text_spec (str): text prototype describing action. May contain key
            based formatting placeholders with variable names to substitute.
            When exception occures this variables will be substituted with
            called method arguments first, if missing - borrowed from underlying
            StackTracerException. If variable values are unfound - None will be
            forced as value.

        Raises:
            StackTracerException: is raised or reraised when unexpected

        Note:
            For normal program flow decorator adds just one stack frame each
            time called. Additional processing takes place only on expected
            exception condition

        Examples:
            >> @Tracer.traced('Adding {v1} and {v2}')
            >> def sum(self, v1, v2):
            >>     a = {1: 2, 3: 4}
            >>     b = a[10]           # Here is KeyError exception raised
            >>     return v1 + v2
            >>
            >> sum(1, 2)

            This will throw StackTracerException with message `Adding 1 and 2`.
            Values for message format will be extracted from sum function
            arguments.


            >> @Tracer.traced('Adding {param1}, {param2}')
            >> def sum(self, v1, v2):
            >>     with Tracer.scope({'param1': v1 + 2, 'param2': v2 + 2}
            >>         a = {1: 2, 2: 4}
            >>         b = a[10]       # Here is KeyError exception raised
            >>         return v1 + v2
            >>
            >> sum(1, 2)

            This will throw StackTracerException with message `Adding 3 and 4`.
            Values for message format will be extracted from internal scope
            exception values map

        """
        def wrap(f):
            @functools.wraps(f)
            def wrapped_f(*args, **kwargs):

                def throws(exc):
                    if hasattr(cls, 'throws') and isinstance(exc, cls.throws):
                        return True
                    return False

                try:
                    return f(*args, **kwargs)
                except StackTracerException as e:
                    Tracer.mk_traced_exc(e, text_spec, f, args, kwargs)
                except Exception as e:
                    if throws(e):
                        raise
                    e = StackTracerException(text=traceback.format_exc())
                    Tracer.mk_traced_exc(e, text_spec, f, args, kwargs)
            return wrapped_f
        return wrap

    def __traced_inst(self, text_spec):
        def wrap(f):
            @functools.wraps(f)
            def wrapped_f(*args, **kwargs):

                def throws(exc):
                    if isinstance(exc, self.__throws) or (
                        hasattr(self, 'throws') and isinstance(exc, self.throws)
                    ):
                        return True
                    return False

                try:
                    return f(*args, **kwargs)
                except StackTracerException as e:
                    Tracer.mk_traced_exc(e, text_spec, f, args, kwargs)
                except Exception as e:
                    if throws(e):
                        raise
                    e = StackTracerException(text=traceback.format_exc())
                    Tracer.mk_traced_exc(e, text_spec, f, args, kwargs)
            return wrapped_f
        return wrap

    @classmethod
    @contextmanager
    def scope(cls, *args):
        """scope - semantic flow context manager

        Handles particular action context and formats exception details
        if action fails

        Args:
            text_spec (str): text prototype describing action. May contain key
                based formatting placeholders with variable names to substitute.
                When exception occures this variables will be substituted with
                params_map values first, if missing - borrowed from underlying
                StackTracerException, if also missing - looked up throw call
                stack local. If variable values are unfound - None will be
                forced as value.
            param_map (dict, optional): dictinary, maps handled values to their
                names for format string
            throws (tuple of Exceptions, optional): tuple of exception to pass
                without formating

        Raises:
            StackTracerException: is raised or reraised when unexpected

        Note:
            Arguments may be passed in any order, matching is based on their
            types, not names. Argument presence influences StackTracerException
            construction.

            For normal program flow decorator adds just one stack frame each
            time called. Additional processing takes place only on expected
            exception condition

        Example:
            >> with Tracer.scope(
            >>     'Do some staff with {v1} and {v2}',
            >>     {'v1': v1, 'v2': v2},
            >>     [ExpectedException, AnotherExpectedException]
            >> ):
            >>     a = {1: 2, 3: 4}
            >>     b = a[10]         # Here is KeyError raised
        """

        def throws(exc):
            if hasattr(cls, 'throws') and isinstance(exc, cls.throws):
                return True
            for a in args:
                if isinstance(a, (list, tuple)):
                    return isinstance(exc, tuple(a))
            return False

        try:
            yield
        except StackTracerException as e:
            Tracer.mk_scope_exc(e, args)
        except Exception as e:
            if throws(e):
                raise
            exc_wrapper = StackTracerException(text=traceback.format_exc())
            Tracer.mk_scope_exc(exc_wrapper, args)

    @contextmanager
    def __scope_inst(self, *args):
        def throws(exc):
            if isinstance(exc, self.__throws) or (
                hasattr(self, 'throws') and isinstance(exc, self.throws)
            ):
                return True
            for a in args:
                if isinstance(a, (list, tuple)):
                    return isinstance(exc, tuple(a))
            return False

        try:
            yield
        except StackTracerException as e:
            Tracer.mk_scope_exc(e, args)
        except Exception as e:
            if throws(e):
                raise
            exc_wrapper = StackTracerException(text=traceback.format_exc())
            Tracer.mk_scope_exc(exc_wrapper, args)

    @staticmethod
    def parse_args(args):
        params_map = {}
        text_spec = None
        for a in args:
            if isinstance(a, dict):
                params_map = a
            elif isinstance(a, str):
                text_spec = a
        return text_spec, params_map

    @staticmethod
    def lookup_stack_value(name):
        trace = inspect.trace()
        for i in reversed(range(0, len(trace))):
            if name in trace[-i][0].f_locals:
                return trace[-i][0].f_locals[name]
        return None

    @staticmethod
    def lookup_args_value(name, f, args, kwargs):
        args_name = inspect.getargspec(f)[0]
        args_dict = collections.OrderedDict(
            list(zip(args_name, args)) + list(kwargs.items())
        )
        return args_dict.get(name, None)

    @staticmethod
    def gather_params(text_spec, params_map, lookup_cb):
        if text_spec is None or '{' not in text_spec:
            return params_map
        fmt_params = {
            k.groups()[0]: None for k in re.finditer(
                '\{([a-zA-Z_][a-zA-Z0-9_]*)\}',
                text_spec
            )
        }
        fmt_params.update(params_map)
        for k in fmt_params:
            if k in params_map:
                continue
            fmt_params[k] = lookup_cb(k)
        return fmt_params

    @staticmethod
    def mk_traced_exc(exc, text_spec, f, args, kwargs):
        params_map = exc.params()
        fmt_params = Tracer.gather_params(
            text_spec, params_map,
            lambda name:
                Tracer.lookup_args_value(name, f, args, kwargs)
        )
        if fmt_params:
            text = text_spec.format(**fmt_params)
            raise StackTracerException(
                sub_exc=exc,
                text=text,
                params_map={}
            )
        raise StackTracerException(sub_exc=exc, text=text_spec)

    @staticmethod
    def mk_scope_exc(exc, args):
        text_spec, params_map = Tracer.parse_args(args)
        if text_spec is None:
            raise StackTracerException(sub_exc=exc, params_map=params_map)

        fmt_params = Tracer.gather_params(
            text_spec, params_map,
            lambda name: Tracer.lookup_stack_value(name)
        )
        text_spec = text_spec.format(**fmt_params)
        raise StackTracerException(
            sub_exc=exc,
            text=text_spec,
            params_map=fmt_params
        )
