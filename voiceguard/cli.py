from __future__ import annotations

import click


@click.group()
def main() -> None:
    """VoiceGuard — multi-step voice verification SDK."""


@main.command("serve")
@click.option("--host", default="0.0.0.0", help="Bind address")
@click.option("--port", default=8000, type=int, help="Port number")
@click.option("--reload", is_flag=True, help="Auto-reload on code changes")
def serve(host: str, port: int, reload: bool) -> None:
    """Start VoiceGuard API + WebSocket server."""
    import uvicorn

    click.echo(f"Starting VoiceGuard server on {host}:{port}")
    uvicorn.run(
        "voiceguard.server.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


@main.command("demo")
@click.option("--host", default="0.0.0.0")
@click.option("--port", default=8000, type=int)
@click.option("--scenario", default="happy_path", help="Scenario: happy_path, wrong_voice, brute_force")
def demo(host: str, port: int, scenario: str) -> None:
    """Run VoiceGuard in demo mode with simulated scenarios."""
    import uvicorn

    click.echo(f"Starting VoiceGuard DEMO mode (scenario: {scenario})")
    click.echo(f"Server on {host}:{port} — open browser to see live verification")

    # Store chosen scenario so the demo runner can pick it up
    import os
    os.environ["VOICEGUARD_DEMO_MODE"] = "1"
    os.environ["VOICEGUARD_DEMO_SCENARIO"] = scenario

    uvicorn.run(
        "voiceguard.server.app:app",
        host=host,
        port=port,
        log_level="info",
    )


@main.group("audit")
def audit() -> None:
    """Audit-chain commands."""


@audit.command("verify")
@click.argument("session_id")
@click.option("--db", default="hospital_agent.db", help="Database path")
def audit_verify(session_id: str, db: str) -> None:
    """Verify integrity of the hash-linked audit chain for a session."""
    from voiceguard.crypto.audit_chain import verify_chain

    report = verify_chain(session_id, db_path=db)
    if report.valid:
        click.echo(f"Chain intact — {report.checked_events} events, no tampering detected.")
    else:
        click.echo(f"CHAIN BROKEN at event {report.broken_at_sequence}:")
        if report.expected_prev_hash:
            click.echo(f"  Expected prev_hash: {report.expected_prev_hash[:16]}...")
            click.echo(f"  Found prev_hash:    {report.found_prev_hash[:16]}...")
        if report.expected_event_hash:
            click.echo(f"  Expected event_hash: {report.expected_event_hash[:16]}...")
            click.echo(f"  Found event_hash:    {report.found_event_hash[:16]}...")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
