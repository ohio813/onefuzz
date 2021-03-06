#!/usr/bin/env python
#
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator

from .consts import ONE_HOUR, SEVEN_DAYS
from .enums import (
    OS,
    Architecture,
    Compare,
    ContainerPermission,
    ContainerType,
    ErrorCode,
    HeartbeatType,
    JobState,
    NodeState,
    NodeTaskState,
    PoolState,
    ScalesetState,
    StatsFormat,
    TaskFeature,
    TaskState,
    TaskType,
    VmState,
)
from .primitives import Container, PoolName, Region


class Error(BaseModel):
    code: ErrorCode
    errors: List[str]


class FileEntry(BaseModel):
    container: Container
    filename: str
    sas_url: Optional[str]


class Authentication(BaseModel):
    password: str
    public_key: str
    private_key: str


class JobConfig(BaseModel):
    project: str
    name: str
    build: str
    duration: int

    @validator("duration", allow_reuse=True)
    def check_duration(cls, value: int) -> int:
        if value < ONE_HOUR or value > SEVEN_DAYS:
            raise ValueError("invalid duration")
        return value


class ReproConfig(BaseModel):
    container: Container
    path: str
    duration: int

    @validator("duration", allow_reuse=True)
    def check_duration(cls, value: int) -> int:
        if value < ONE_HOUR or value > SEVEN_DAYS:
            raise ValueError("invalid duration")
        return value


class TaskDetails(BaseModel):
    type: TaskType
    duration: int
    target_exe: str
    target_env: Dict[str, str]
    target_options: List[str]
    target_workers: Optional[int]
    target_options_merge: Optional[bool]
    check_asan_log: Optional[bool]
    check_debugger: Optional[bool] = Field(default=True)
    check_retry_count: Optional[int]
    rename_output: Optional[bool]
    supervisor_exe: Optional[str]
    supervisor_env: Optional[Dict[str, str]]
    supervisor_options: Optional[List[str]]
    supervisor_input_marker: Optional[str]
    generator_exe: Optional[str]
    generator_env: Optional[Dict[str, str]]
    generator_options: Optional[List[str]]
    analyzer_exe: Optional[str]
    analyzer_env: Optional[Dict[str, str]]
    analyzer_options: Optional[List[str]]
    wait_for_files: Optional[ContainerType]
    stats_file: Optional[str]
    stats_format: Optional[StatsFormat]
    reboot_after_setup: Optional[bool]
    target_timeout: Optional[int]

    @validator("check_retry_count", allow_reuse=True)
    def validate_check_retry_count(cls, value: int) -> int:
        if value is not None:
            if value < 0:
                raise ValueError("invalid check_retry_count")
        return value

    @validator("target_timeout", allow_reuse=True)
    def check_target_timeout(cls, value: Optional[int]) -> Optional[int]:
        if value is not None:
            if value < 1:
                raise ValueError("invalid target_timeout")
        return value

    @validator("duration", allow_reuse=True)
    def check_duration(cls, value: int) -> int:
        if value < ONE_HOUR or value > SEVEN_DAYS:
            raise ValueError("invalid duration")
        return value


class TaskPool(BaseModel):
    count: int
    pool_name: PoolName


class TaskVm(BaseModel):
    region: Region
    sku: str
    image: str
    count: int = Field(default=1)
    spot_instances: bool = Field(default=False)
    reboot_after_setup: Optional[bool]

    @validator("count", allow_reuse=True)
    def check_count(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("invalid count")
        return value


class TaskContainers(BaseModel):
    type: ContainerType
    name: Container


class TaskConfig(BaseModel):
    job_id: UUID
    prereq_tasks: Optional[List[UUID]]
    task: TaskDetails
    vm: Optional[TaskVm]
    pool: Optional[TaskPool]
    containers: List[TaskContainers]
    tags: Dict[str, str]


class BlobRef(BaseModel):
    account: str
    container: Container
    name: str


class Report(BaseModel):
    input_url: Optional[str]
    input_blob: BlobRef
    executable: str
    crash_type: str
    crash_site: str
    call_stack: List[str]
    call_stack_sha256: str
    input_sha256: str
    asan_log: Optional[str]
    task_id: UUID
    job_id: UUID


class ADODuplicateTemplate(BaseModel):
    increment: List[str]
    comment: Optional[str]
    set_state: Dict[str, str]
    ado_fields: Dict[str, str]


class ADOTemplate(BaseModel):
    base_url: str
    auth_token: str
    project: str
    type: str
    unique_fields: List[str]
    comment: Optional[str]
    ado_fields: Dict[str, str]
    on_duplicate: ADODuplicateTemplate


class TeamsTemplate(BaseModel):
    url: str


class ContainerDefinition(BaseModel):
    type: ContainerType
    compare: Compare
    value: int
    permissions: List[ContainerPermission]


class VmDefinition(BaseModel):
    compare: Compare
    value: int


class TaskDefinition(BaseModel):
    features: List[TaskFeature]
    containers: List[ContainerDefinition]
    monitor_queue: Optional[ContainerType]
    vm: VmDefinition


class HeartbeatEntry(BaseModel):
    task_id: UUID
    machine_id: UUID
    data: List[Dict[str, HeartbeatType]]


class HeartbeatSummary(BaseModel):
    machine_id: UUID
    timestamp: Optional[datetime]
    type: HeartbeatType


# TODO: service shouldn't pass SyncedDir, but just the url and let the agent
# come up with paths
class SyncedDir(BaseModel):
    path: str
    url: str


CONTAINER_DEF = Optional[Union[SyncedDir, List[SyncedDir]]]


class ClientCredentials(BaseModel):
    client_id: UUID
    client_secret: str


class AgentConfig(BaseModel):
    client_credentials: Optional[ClientCredentials]
    onefuzz_url: str
    pool_name: str
    instrumentation_key: Optional[str]
    telemetry_key: Optional[str]


class TaskUnitConfig(BaseModel):
    job_id: UUID
    task_id: UUID
    task_type: TaskType
    instrumentation_key: Optional[str]
    telemetry_key: Optional[str]
    heartbeat_queue: str
    # command_queue: str
    back_channel_address: str
    input_queue: Optional[str]
    supervisor_exe: Optional[str]
    supervisor_env: Optional[Dict[str, str]]
    supervisor_options: Optional[List[str]]
    supervisor_input_marker: Optional[str]
    target_exe: Optional[str]
    target_env: Optional[Dict[str, str]]
    target_options: Optional[List[str]]
    target_timeout: Optional[int]
    target_options_merge: Optional[bool]
    check_asan_log: Optional[bool]
    check_debugger: Optional[bool]
    check_retry_count: Optional[int]
    rename_output: Optional[bool]
    generator_exe: Optional[str]
    generator_env: Optional[Dict[str, str]]
    generator_options: Optional[List[str]]
    wait_for_files: Optional[str]
    analyzer_exe: Optional[str]
    analyzer_env: Optional[Dict[str, str]]
    analyzer_options: Optional[List[str]]
    stats_file: Optional[str]
    stats_format: Optional[StatsFormat]

    # from here forwards are Container definitions.  These need to be inline
    # with TaskDefinitions and ContainerTypes
    analysis: CONTAINER_DEF
    coverage: CONTAINER_DEF
    crashes: CONTAINER_DEF
    inputs: CONTAINER_DEF
    no_repro: CONTAINER_DEF
    readonly_inputs: CONTAINER_DEF
    reports: CONTAINER_DEF
    tools: CONTAINER_DEF
    unique_inputs: CONTAINER_DEF
    unique_reports: CONTAINER_DEF


class Forward(BaseModel):
    src_port: int
    dst_ip: str
    dst_port: int


class ProxyConfig(BaseModel):
    url: str
    notification: str
    region: Region
    forwards: List[Forward]


class ProxyHeartbeat(BaseModel):
    region: Region
    forwards: List[Forward]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Files(BaseModel):
    files: List[str]


class WorkUnit(BaseModel):
    job_id: UUID
    task_id: UUID
    task_type: TaskType

    # JSON-serialized `TaskUnitConfig`.
    config: str


class WorkSet(BaseModel):
    reboot: bool
    setup_url: str
    script: bool
    work_units: List[WorkUnit]


class WorkUnitSummary(BaseModel):
    job_id: UUID
    task_id: UUID
    task_type: TaskType


class WorkSetSummary(BaseModel):
    work_units: List[WorkUnitSummary]


NotificationTemplate = Union[ADOTemplate, TeamsTemplate]


class Notification(BaseModel):
    container: Container
    notification_id: UUID = Field(default_factory=uuid4)
    config: NotificationTemplate


class JobTaskInfo(BaseModel):
    task_id: UUID
    type: TaskType
    state: TaskState


class Job(BaseModel):
    job_id: UUID = Field(default_factory=uuid4)
    state: JobState = Field(default=JobState.init)
    config: JobConfig
    error: Optional[str]
    end_time: Optional[datetime] = None
    task_info: Optional[List[JobTaskInfo]]


class Node(BaseModel):
    pool_name: PoolName
    machine_id: UUID
    state: NodeState = Field(default=NodeState.init)
    scaleset_id: Optional[UUID] = None
    tasks: Optional[List[Tuple[UUID, NodeTaskState]]] = None


class ScalesetSummary(BaseModel):
    scaleset_id: UUID
    state: ScalesetState


class NodeTasks(BaseModel):
    machine_id: UUID
    task_id: UUID
    state: NodeTaskState = Field(default=NodeTaskState.init)


class Pool(BaseModel):
    name: PoolName
    pool_id: UUID = Field(default_factory=uuid4)
    os: OS
    managed: bool
    arch: Architecture
    state: PoolState = Field(default=PoolState.init)
    client_id: Optional[UUID]
    nodes: Optional[List[Node]]
    config: Optional[AgentConfig]

    # work_queue is explicitly not saved to Tables (see save_exclude).  This is
    # intended to be used to pass the information to the CLI when the CLI asks
    # for information about what work is in the queue for the pool.
    work_queue: Optional[List[WorkSetSummary]]

    # explicitly excluded from Tables
    scaleset_summary: Optional[List[ScalesetSummary]]


class ScalesetNodeState(BaseModel):
    machine_id: UUID
    instance_id: str
    state: Optional[NodeState]


class Scaleset(BaseModel):
    pool_name: PoolName
    scaleset_id: UUID = Field(default_factory=uuid4)
    state: ScalesetState = Field(default=ScalesetState.init)
    auth: Optional[Authentication]
    vm_sku: str
    image: str
    region: Region
    size: int
    new_size: Optional[int]
    spot_instances: bool
    error: Optional[Error]
    nodes: Optional[List[ScalesetNodeState]]
    client_id: Optional[UUID]
    client_object_id: Optional[UUID]
    tags: Dict[str, str] = Field(default_factory=lambda: {})


class NotificationConfig(BaseModel):
    config: NotificationTemplate


class Heartbeat(BaseModel):
    task_id: UUID
    heartbeat_id: str
    machine_id: UUID
    heartbeat_type: HeartbeatType


class Repro(BaseModel):
    vm_id: UUID = Field(default_factory=uuid4)
    task_id: UUID
    config: ReproConfig
    state: VmState = Field(default=VmState.init)
    auth: Optional[Authentication]
    os: OS
    error: Optional[Error]
    ip: Optional[str]


class ExitStatus(BaseModel):
    code: Optional[int]
    signal: Optional[int]
    success: bool


class WorkerRunningEvent(BaseModel):
    task_id: UUID


class WorkerDoneEvent(BaseModel):
    task_id: UUID
    exit_status: ExitStatus
    stderr: str
    stdout: str


class WorkerEvent(BaseModel):
    event: Union[WorkerDoneEvent, WorkerRunningEvent]


class NodeStateUpdate(BaseModel):
    state: NodeState


NodeEvent = Union[WorkerEvent, NodeStateUpdate]


class NodeEventEnvelope(BaseModel):
    machine_id: UUID
    event: NodeEvent


class NodeCommandStopTask(BaseModel):
    task_id: UUID


NodeCommand = Union[NodeCommandStopTask]


class NodeCommandEnvelope(BaseModel):
    command: NodeCommand
    message_id: str


class TaskEvent(BaseModel):
    task_id: UUID
    machine_id: UUID
    event_data: WorkerEvent


class TaskEventSummary(BaseModel):
    timestamp: Optional[datetime]
    event_data: str
    event_type: str


class Task(BaseModel):
    job_id: UUID
    task_id: UUID = Field(default_factory=uuid4)
    state: TaskState = Field(default=TaskState.init)
    os: OS
    config: TaskConfig
    error: Optional[Error]
    auth: Optional[Authentication]
    heartbeats: Optional[List[HeartbeatSummary]]
    end_time: Optional[datetime]
    events: Optional[List[TaskEventSummary]]
