"""Task 1 Example Policy: V1SmartPIDPolicy."""

from smart_buildings.baselines.transfer_policy import TransferPolicy


class V1SmartPIDPolicy(TransferPolicy):
    name = "v1_smart_pid"
