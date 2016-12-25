# Ctxt - Semantic Python Call Stack Context Manager

Provides unified method to keep call semantics when exception occures. It
devotes to textual description of call stack with actual values passed throw it
at each stack level. Contains  wrappers and context managers to trace semantic
flow. All of them are implemented as methods of Tracer class. Both static and
non-static methods present.

# Supported Python version
This code was tested against following Python versions:
- 2.7
- 3.3
- 3.4
- 3.5

# Why you shall use ctxt

Imagine some buggy code called from multiple places with completely different
params. Most of these calls normaly pass any tests while only a small subset of
parameter combinations probably cause failure.

Let it be something like this:

```python
import ctxt

@ctxt.Tracer.traced('Get value from {some_list} at {a} * {b} place')
def buggy(some_list, a, b):
    return some_list[a * b]


@ctxt.Tracer.traced('Sum values of {some_list}, indexes provided by {idx_1}, {idx_2}')
def sum_list_entries(some_list, idx_1, idx_2):
    res = 0
    for i in idx_1:
        for j in idx_2:
            res += buggy(some_list, i, j)
    return res


@ctxt.Tracer.traced('Some sample function call')
def do_some_staff():
    idx_1 = [0, 1, 3, 2]
    idx_2 = [1, 0, 2, 1, 1]
    some_list = [1, 2, 3, 4, 5]
    with ctxt.Tracer.scope('Sum list entries by indexes'):
        return sum_list_entries(some_list, idx_1, idx_2)

try:
    do_some_staff()
except ctxt.StackTracerException as e:
    print(e.format('dict'))
```

This will result in th following output. Seems to be much more readable.
For more readability result was dumped as JSON and passed to json
pretty printer.

```json
{
    "sub_exc": {
        "sub_exc": {
            "sub_exc": {
                "sub_exc": {
                    "text": "Traceback (most recent call last):\n  File \"/home/drozdov/dev/ctxt/ctxt/ctxt.py\", line 260, in wrapped_f\n    return f(*args, **kwargs)\n  File \"<stdin>\", line 3, in buggy\nIndexError: list index out of range\n"
                },
                "text": "Get value from [1, 2, 3, 4, 5] at 3 * 2 place"
            },
            "text": "Sum values of [1, 2, 3, 4, 5], indexes provided by [0, 1, 3, 2], [1, 0, 2, 1, 1]"
        },
        "text": "Sum list entries by indexes"
    },
    "text": "Some sample function call"
}
```
