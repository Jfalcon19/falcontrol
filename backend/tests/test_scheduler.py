"""Unit tests for the RedBeat scheduler helpers.

RedBeat and the DB are fully mocked — no Redis or Postgres required.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from app.tasks.scheduler import _key, register_schedule, sync_all_schedules, unregister_schedule

# ── helpers ───────────────────────────────────────────────────────────────


def _make_schedule(
    schedule_id: str = "aaaaaaaa-0000-0000-0000-000000000001",
    cron: str = "0 2 * * *",
    enabled: bool = True,
) -> MagicMock:
    s = MagicMock()
    s.id = schedule_id
    s.cron_expression = cron
    s.enabled = enabled
    return s


# ── _key ──────────────────────────────────────────────────────────────────


def test_key_format() -> None:
    assert _key("abc-123") == "falcontrol:schedule:abc-123"


# ── register_schedule ─────────────────────────────────────────────────────


@patch("app.tasks.scheduler.RedBeatSchedulerEntry")
def test_register_schedule_saves_entry(mock_entry_cls: MagicMock) -> None:
    mock_entry = MagicMock()
    mock_entry_cls.return_value = mock_entry

    schedule = _make_schedule(cron="30 6 * * 1", enabled=True)
    register_schedule(schedule)

    mock_entry_cls.assert_called_once()
    _, kwargs = mock_entry_cls.call_args
    assert kwargs["task"] == "run_scheduled_job"
    assert kwargs["args"] == [str(schedule.id)]
    assert kwargs["enabled"] is True
    mock_entry.save.assert_called_once()


@patch("app.tasks.scheduler.RedBeatSchedulerEntry")
def test_register_schedule_disabled(mock_entry_cls: MagicMock) -> None:
    mock_entry = MagicMock()
    mock_entry_cls.return_value = mock_entry

    schedule = _make_schedule(enabled=False)
    register_schedule(schedule)

    _, kwargs = mock_entry_cls.call_args
    assert kwargs["enabled"] is False
    mock_entry.save.assert_called_once()


# ── unregister_schedule ───────────────────────────────────────────────────


@patch("app.tasks.scheduler.RedBeatSchedulerEntry")
def test_unregister_schedule_deletes_entry(mock_entry_cls: MagicMock) -> None:
    mock_entry = MagicMock()
    mock_entry_cls.from_key.return_value = mock_entry

    unregister_schedule("abc-123")

    args, _ = mock_entry_cls.from_key.call_args
    assert args[0] == "falcontrol:schedule:abc-123"
    mock_entry.delete.assert_called_once()


@patch("app.tasks.scheduler.RedBeatSchedulerEntry")
def test_unregister_schedule_ignores_missing(mock_entry_cls: MagicMock) -> None:
    mock_entry_cls.from_key.side_effect = KeyError("not found")

    # Should not raise
    unregister_schedule("missing-id")


# ── sync_all_schedules ────────────────────────────────────────────────────


@patch("app.tasks.scheduler.unregister_schedule")
@patch("app.tasks.scheduler.register_schedule")
@patch("app.tasks.scheduler._load_all_schedules", new_callable=AsyncMock)
def test_sync_all_schedules_registers_enabled(
    mock_load: AsyncMock,
    mock_register: MagicMock,
    mock_unregister: MagicMock,
) -> None:
    enabled = _make_schedule(schedule_id="aaa", enabled=True)
    disabled = _make_schedule(schedule_id="bbb", enabled=False)
    mock_load.return_value = [enabled, disabled]

    sync_all_schedules()

    mock_register.assert_called_once_with(enabled)
    mock_unregister.assert_called_once_with("bbb")


@patch("app.tasks.scheduler.unregister_schedule")
@patch("app.tasks.scheduler.register_schedule")
@patch("app.tasks.scheduler._load_all_schedules", new_callable=AsyncMock)
def test_sync_all_schedules_empty(
    mock_load: AsyncMock,
    mock_register: MagicMock,
    mock_unregister: MagicMock,
) -> None:
    mock_load.return_value = []

    sync_all_schedules()

    mock_register.assert_not_called()
    mock_unregister.assert_not_called()


# ── run_scheduled_job task ────────────────────────────────────────────────


@patch("app.tasks.jobs._save_result", new_callable=AsyncMock)
@patch("app.tasks.jobs._fetch_job_data", new_callable=AsyncMock)
@patch("app.tasks.jobs.ansible_runner.run")
@patch("app.tasks.jobs._redis_client")
@patch("app.tasks.jobs._create_job_from_schedule", new_callable=AsyncMock)
def test_run_scheduled_job_creates_job_and_runs(
    mock_create: AsyncMock,
    mock_redis_cls: MagicMock,
    mock_ar_run: MagicMock,
    mock_fetch: AsyncMock,
    mock_save: AsyncMock,
) -> None:
    from app.tasks.jobs import run_scheduled_job

    job_id = "00000000-0000-0000-0000-000000000099"
    mock_create.return_value = job_id
    mock_fetch.return_value = ("ping.yml", "[all]\nweb-01 ansible_host=10.0.0.1\n")

    result_mock = MagicMock()
    result_mock.rc = 0
    mock_ar_run.return_value = result_mock
    mock_redis_cls.return_value = MagicMock()

    run_scheduled_job("schedule-id-123")

    mock_create.assert_called_once_with("schedule-id-123")
    mock_fetch.assert_called_once_with(job_id)


@patch("app.tasks.jobs._create_job_from_schedule", new_callable=AsyncMock)
@patch("app.tasks.jobs._redis_client")
def test_run_scheduled_job_schedule_not_found(
    mock_redis_cls: MagicMock,
    mock_create: AsyncMock,
) -> None:
    from app.tasks.jobs import run_scheduled_job

    mock_create.side_effect = RuntimeError("Schedule not found")
    mock_redis_cls.return_value = MagicMock()

    # Should not raise — just log the error
    run_scheduled_job("nonexistent-schedule")
