## Development

Get yourself a virtualenv for the project:

```
python -m venv venv
source venv/bin/activate
```

Then, install the development dependencies.

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

## Release

Inside the virtualenv, build and check the release. We build tarballs and
wheels. Please do not dist eggs!

```
python -m build
python -m twine check dist/*
```

When you're ready, upload the dists to PyPi.

```
python -m twine upload dist/*
```
