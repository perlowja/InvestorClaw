# SPDX-License-Identifier: Apache-2.0
"""
Multi-device test matrix for InvestorClaw harness.

Defines device configurations and constraints for:
- mac-dev-host (Mac, local, unconstrained)
- pi-large (Raspberry Pi 8GB, baseline Pi testing)
- pi-small (Raspberry Pi 2GB, memory constraint validation)
"""

from dataclasses import dataclass


@dataclass
class DeviceConfig:
    """Configuration for a test device."""

    name: str  # Device identifier
    host: str  # Hostname or IP address
    ssh_enabled: bool  # Whether SSH is required
    ssh_port: int  # SSH port (default 22)
    memory_mb: int  # Available RAM
    gpu_available: bool  # GPU support
    max_concurrent_commands: int  # Command parallelism limit
    timeout_multiplier: float  # Latency multiplier vs. baseline
    description: str  # Human-readable description


# Device definitions
DEVICE_MATRIX = {
    "mac-dev-host": DeviceConfig(
        name="mac-dev-host",
        host="127.0.0.1",
        ssh_enabled=False,
        ssh_port=22,
        memory_mb=16000,
        gpu_available=False,
        max_concurrent_commands=8,
        timeout_multiplier=1.0,
        description="Local macOS workstation (16GB RAM, unconstrained)",
    ),
    "pi-large": DeviceConfig(
        name="pi-large",
        host="192.0.2.56",  # IP fallback: pi-large.local may not resolve via mDNS
        ssh_enabled=True,
        ssh_port=22,
        memory_mb=8000,
        gpu_available=False,
        max_concurrent_commands=4,
        timeout_multiplier=1.5,
        description="Nemoclaw+ZeroClaw (nclawzero) — Raspberry Pi 8GB orchestrator testing",
    ),
    "pi-small": DeviceConfig(
        name="pi-small",
        host="192.0.2.54",  # IP fallback: pi-small.local may not resolve via mDNS
        ssh_enabled=True,
        ssh_port=22,
        memory_mb=2000,
        gpu_available=False,
        max_concurrent_commands=1,
        timeout_multiplier=2.5,
        description="Pure ZeroClaw — Raspberry Pi 2GB orchestrator testing (memory constrained)",
    ),
}


def get_device(device_name: str) -> DeviceConfig:
    """Get device configuration by name."""
    if device_name not in DEVICE_MATRIX:
        raise ValueError(
            f"Unknown device: {device_name}. Available: {', '.join(DEVICE_MATRIX.keys())}"
        )
    return DEVICE_MATRIX[device_name]


def get_timeout_seconds(base_seconds: int, device_name: str) -> int:
    """Calculate adjusted timeout for device."""
    device = get_device(device_name)
    adjusted = int(base_seconds * device.timeout_multiplier)
    return max(adjusted, base_seconds)  # Never reduce timeout below base


def is_local_device(device_name: str) -> bool:
    """Check if device is local (no SSH required)."""
    device = get_device(device_name)
    return not device.ssh_enabled
