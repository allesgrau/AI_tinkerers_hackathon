from __future__ import annotations

import click


@click.group()
def main() -> None:
    """VoiceGuard command line interface."""


@main.command("serve")
def serve() -> None:
    click.echo("TODO: start VoiceGuard API and WebSocket server")


@main.command("demo")
def demo() -> None:
    click.echo("TODO: run VoiceGuard demo scenarios")


@main.group("audit")
def audit() -> None:
    """Audit-chain commands."""


@audit.command("verify")
def audit_verify() -> None:
    click.echo("TODO: verify hash-chain integrity")


if __name__ == "__main__":
    main()
