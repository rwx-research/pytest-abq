import pytest
import sys
import os
from typing import List, cast

from .abq.types import (
    InitMessage,
    InitSuccessMessage,
    Location,
    ManifestMember,
    ManifestSuccessMessage,
    ManifestData,
    SingleTestResultMessage,
    Test,
    TestCaseData,
    TestCaseMessage,
    TestResult,
    TestResultFailure,
    TestResultMessage,
    TestResultSkipped,
    TestResultStatus,
    TestResultSuccess,
)

from .abq.config import EnabledConfig, get_config
from .abq.net import protocol_read, protocol_write

_config = get_config()


def generate_manifest(items: List[pytest.Item]) -> ManifestSuccessMessage:
    members: List[ManifestMember] = []
    for item in items:
        members.append(
            Test(
                type="test",
                id=item.nodeid,
                meta={},
                tags=list(map(lambda mark: mark.name, item.own_markers)),
            )
        )

    manifest = ManifestData(members=members, init_meta={})
    return ManifestSuccessMessage(
        type="manifest_success",
        manifest=manifest,
    )


if _config.enabled is True:
    abq_config = cast(EnabledConfig, _config)
    conn = abq_config.connect()

    queue: List[pytest.Item] = []
    index: int = -1
    current_test = None

    def pytest_configure(config: pytest.Config):
        if abq_config.should_generate_manifest:
            # Suppress any output during manifest generation.
            # Otherwise, pytest will print a summary of collected tests and that
            # no tests were run. This is not particularly useful to a user of
            # ABQ.
            config.option.verbose = -3
            config.option.no_summary = True
            config.option.no_header = True

    def pytest_collection_finish(session: pytest.Session):
        if abq_config.should_generate_manifest:
            manifest_message = generate_manifest(session.items)
            protocol_write(conn, manifest_message)

        global index, queue
        queue = session.items
        index = 0

    def pytest_runtestloop(session: pytest.Session):
        global index, current_test

        if abq_config.should_generate_manifest:
            return True

        _init_msg: InitMessage = protocol_read(conn)
        protocol_write(conn, InitSuccessMessage())

        while True:
            try:
                test_case_data: TestCaseData = protocol_read(conn)["test_case"]
            except EOFError:
                # Socket was closed; we've hit the end of all tests to run.
                return True

            # Fast-forward to the next test to run in the queue of items.
            current_test = test_case_data["id"]
            while queue[index].nodeid != test_case_data["id"]:
                index += 1

            item = queue[index]
            item.ihook.pytest_runtest_protocol(item=item, nextitem=item.nextitem)

    def pytest_runtest_logreport(report: pytest.TestReport):
        if report.when != "call":
            # We currently don't keep track of setup/teardown notifications.
            return
        assert (
            report.nodeid == current_test
        ), f"Got result for {report.nodeid} while {current_test} was expected to be running"

        exception_info = report.longrepr

        if report.outcome == "passed":
            status: TestResultStatus = TestResultSuccess(type="success")
        elif report.outcome == "failed":
            if isinstance(exception_info, pytest.ExceptionInfo):
                exception = exception_info.exconly()
                backtrace = str(exception_info.getrepr()).split("\n")
                status = TestResultFailure(
                    type="failure", exception=exception, backtrace=backtrace
                )
            elif isinstance(exception_info, str):
                status = TestResultFailure(type="failure", exception=exception_info)
            else:
                status = TestResultFailure(type="failure")
        else:
            assert report.outcome == "skipped"
            status = TestResultSkipped(type="skipped")

        file, line, _domain = report.location
        if line is not None:
            location = Location(file=file, line=line)
        else:
            location = Location(file=file)

        test_result = TestResult(
            status=status,
            id=report.nodeid,
            display_name=report.nodeid,
            location=location,
            runtime=int(report.duration * 1e9),  # seconds to nanos
            meta={},  # we can get this from report.user_properties, but it needs sanitization
            output=report.longreprtext,
        )
        test_result_message = SingleTestResultMessage(test_result=test_result)

        protocol_write(conn, test_result_message)
