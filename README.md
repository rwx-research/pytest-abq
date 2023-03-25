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
