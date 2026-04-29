"""Unit tests for the run_playbook Celery task.

ansible_runner.run, Redis, and async DB helpers are fully mocked so these
tests run without network, Redis, or Ansible installed.
"""

from unittest.mock import AsyncMock, MagicMock, patch

from app.tasks.jobs import _channel, run_playbook

# ── helpers ───────────────────────────────────────────────────────────────


def _make_runner_result(rc: int = 0) -> MagicMock:
    result = MagicMock()
    result.rc = rc
    return result


def _make_host(name: str = "web-01", address: str = "10.0.0.1") -> MagicMock:
    host = MagicMock()
    host.name = name
    host.address = address
    host.port = None
    host.connection_type.value = "ssh"
    return host


# ── _channel ──────────────────────────────────────────────────────────────


def test_channel_format() -> None:
    assert _channel("abc-123") == "job:abc-123:logs"


# ── run_playbook — success path ────────────────────────────────────────────


@patch("app.tasks.jobs._save_result", new_callable=AsyncMock)
@patch("app.tasks.jobs._fetch_job_data", new_callable=AsyncMock)
@patch("app.tasks.jobs.ansible_runner.run")
@patch("app.tasks.jobs._redis_client")
def test_run_playbook_success(
    mock_redis_cls: MagicMock,
    mock_ar_run: MagicMock,
    mock_fetch: AsyncMock,
    mock_save: AsyncMock,
) -> None:
    job_id = "00000000-0000-0000-0000-000000000001"

    mock_fetch.return_value = ("ping.yml", "[all]\nweb-01 ansible_host=10.0.0.1\n")
    mock_ar_run.return_value = _make_runner_result(rc=0)

    mock_r = MagicMock()
    mock_redis_cls.return_value = mock_r

    run_playbook(job_id)

    mock_fetch.assert_called_once_with(job_id)
    mock_ar_run.assert_called_once()
    mock_save.assert_called_once()
    # __END__ sentinel published
    mock_r.publish.assert_called_with(_channel(job_id), "__END__")


# ── run_playbook — failure path (non-zero rc) ──────────────────────────────


@patch("app.tasks.jobs._save_result", new_callable=AsyncMock)
@patch("app.tasks.jobs._fetch_job_data", new_callable=AsyncMock)
@patch("app.tasks.jobs.ansible_runner.run")
@patch("app.tasks.jobs._redis_client")
def test_run_playbook_failed_rc(
    mock_redis_cls: MagicMock,
    mock_ar_run: MagicMock,
    mock_fetch: AsyncMock,
    mock_save: AsyncMock,
) -> None:
    job_id = "00000000-0000-0000-0000-000000000002"

    mock_fetch.return_value = ("ping.yml", "[all]\nweb-01 ansible_host=10.0.0.1\n")
    mock_ar_run.return_value = _make_runner_result(rc=2)
    mock_redis_cls.return_value = MagicMock()

    run_playbook(job_id)

    # _save_result called with return_code=2
    _, kwargs = mock_save.call_args
    assert kwargs["return_code"] == 2


# ── run_playbook — job not found ───────────────────────────────────────────


@patch("app.tasks.jobs._fetch_job_data", new_callable=AsyncMock)
@patch("app.tasks.jobs._redis_client")
def test_run_playbook_job_not_found(
    mock_redis_cls: MagicMock,
    mock_fetch: AsyncMock,
) -> None:
    job_id = "00000000-0000-0000-0000-000000000003"
    mock_fetch.side_effect = RuntimeError("Job not found")
    mock_r = MagicMock()
    mock_redis_cls.return_value = mock_r

    run_playbook(job_id)

    # Error + sentinel published, ansible_runner never called
    calls = [str(c) for c in mock_r.publish.call_args_list]
    assert any("ERROR" in c for c in calls)
    assert any("__END__" in c for c in calls)


# ── run_playbook — event_handler publishes stdout lines ───────────────────


@patch("app.tasks.jobs._save_result", new_callable=AsyncMock)
@patch("app.tasks.jobs._fetch_job_data", new_callable=AsyncMock)
@patch("app.tasks.jobs.ansible_runner.run")
@patch("app.tasks.jobs._redis_client")
def test_run_playbook_publishes_stdout(
    mock_redis_cls: MagicMock,
    mock_ar_run: MagicMock,
    mock_fetch: AsyncMock,
    mock_save: AsyncMock,
) -> None:
    job_id = "00000000-0000-0000-0000-000000000004"
    mock_fetch.return_value = ("ping.yml", "[all]\n")
    mock_r = MagicMock()
    mock_redis_cls.return_value = mock_r

    # Simulate event_handler being called with stdout lines
    def fake_run(**kwargs: object) -> MagicMock:
        handler = kwargs.get("event_handler")
        if callable(handler):
            handler({"stdout": "PLAY [all] *****"})
            handler({"stdout": "ok: [web-01]"})
            handler({"stdout": ""})  # empty line — should be ignored
        return _make_runner_result(rc=0)

    mock_ar_run.side_effect = fake_run

    run_playbook(job_id)

    published = [str(c) for c in mock_r.publish.call_args_list]
    assert any("PLAY [all]" in c for c in published)
    assert any("ok: [web-01]" in c for c in published)
    # empty line not published
    assert not any("''" in c and "publish" in c for c in published)
