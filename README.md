# pytest-abq

An [ABQ](rwx.com/abq) integration for [pytest](https://docs.pytest.org/en/7.2.x/).

To install:

```
pip install pytest-abq
```

That's it! Then, run your test suite with ABQ:

```
abq test -- pytest
```

## Compatibility

`pytest-abq` is actively tested against

- Python 3.8, 3.9, 3.10
- Pytest 7.0, 7.2

`pytest-abq` may support Python and pytest versions beyond these.

`pytest-abq` implements version 0.2 of the ABQ native runner protocol and
requires ABQ 1.3.0 or greater.

## Development

First, install the development dependencies.

```
pip install -r requirements.txt
```

To run unit tests, install the pytest plugin and then run `pytest`:

```
pip install -e .
pytest tests
```

To run the integration tests with ABQ, you'll need to first have
`abq_tester_harness` available in your path. Then, run `tox`:

```
tox
```

If you need to update the goldens, pass `-- update`:

```
tox -- update
```
