import socket
from typing import Any, Dict, List, Optional, Union, Literal, TypedDict
from typing_extensions import NotRequired


Connection = socket.socket


class Test(TypedDict):
    type: Literal["test"]
    id: str
    tags: List[str]
    meta: Dict[str, Any]


class Group(TypedDict):
    type: Literal["group"]
    name: str
    tags: List[str]
    meta: Dict[str, Any]
    members: List["ManifestMember"]


ManifestMember = Union[Group, Test]


class ManifestData(TypedDict):
    members: List[ManifestMember]
    init_meta: Dict[str, Any]


class ManifestSuccessMessage(TypedDict):
    type: Literal["manifest_success"]
    manifest: ManifestData
    other_errors: NotRequired[List["OutOfBandError"]]


class ManifestFailureMessage(TypedDict):
    type: Literal["manifest_failure"]
    error: "OutOfBandError"
    other_errors: NotRequired[List["OutOfBandError"]]


class TestFocus(TypedDict):
    test_ids: List[str]


class TestCaseData(TypedDict):
    id: str
    meta: Dict[str, Any]
    focus: NotRequired[TestFocus]


class TestCaseMessage(TypedDict):
    test_case: TestCaseData


Nanoseconds = int


class TestResultFailure(TypedDict):
    type: Literal["failure"]
    exception: NotRequired[str]
    backtrace: NotRequired[List[str]]


class TestResultError(TypedDict):
    type: Literal["error"]
    exception: NotRequired[str]
    backtrace: NotRequired[List[str]]

class TestResultSuccess(TypedDict):
    type: Literal["success"]

class TestResultPending(TypedDict):
    type: Literal["pending"]

class TestResultSkipped(TypedDict):
    type: Literal["skipped"]

class TestResultTodo(TypedDict):
    type: Literal["todo"]

class TestResultTimedOut(TypedDict):
    type: Literal["timed_out"]

TestResultStatus = Union[
    TestResultFailure,
    TestResultError,
    TestResultSuccess,
    TestResultPending,
    TestResultSkipped,
    TestResultTodo,
    TestResultTimedOut,
]


class Location(TypedDict):
    file: str
    line: NotRequired[int]
    column: NotRequired[int]


class TestResult(TypedDict):
    status: TestResultStatus
    id: str
    display_name: str
    runtime: Nanoseconds
    meta: Dict[str, Any]
    output: NotRequired[str]
    location: NotRequired[Location]
    started_at: NotRequired[str]
    finished_at: NotRequired[str]
    lineage: NotRequired[List[str]]
    past_attempts: NotRequired[List["TestResult"]]
    other_errors: NotRequired[List["OutOfBandError"]]


class OutOfBandError(TypedDict):
    message: str
    backtrace: NotRequired[List[str]]
    exception: NotRequired[str]
    location: NotRequired[Location]
    meta: NotRequired[Dict[str, Any]]


TestResultMessage = Union[
    "SingleTestResultMessage",
    "MultipleTestResultsMessage",
    "IncrementalTestResultMessage",
]


class SingleTestResultMessage(TypedDict):
    test_result: TestResult


class MultipleTestResultsMessage(TypedDict):
    test_results: List[TestResult]


class IncrementalTestResultStep(TypedDict):
    type: Literal["incremental_result"]
    one_test_result: TestResult


class IncrementalTestResultDone(TypedDict):
    type: Literal["incremental_result_done"]
    last_test_result: NotRequired[TestResult]


IncrementalTestResultMessage = Union[
    IncrementalTestResultStep, IncrementalTestResultDone
]


class NativeRunnerSpecification(TypedDict):
    type: Literal["abq_native_runner_specification"]
    name: str
    version: str
    test_framework: str
    test_framework_version: str
    language: str
    language_version: str
    host: str


class ProtocolVersion(TypedDict):
    type: Literal["abq_protocol_version"]
    major: int
    minor: int


class AbqNativeRunnerSpawnedMessage(TypedDict):
    type: Literal["abq_native_runner_spawned"]
    protocol_version: ProtocolVersion
    runner_specification: NativeRunnerSpecification


class InitMessage(TypedDict):
    init_meta: Dict[str, Any]
    fast_exit: bool


class InitSuccessMessage(TypedDict):
    pass
