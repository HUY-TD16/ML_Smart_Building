"""Starting point for your own policy. Edit this file."""

from __future__ import annotations

from typing import Any

import numpy as np

from smart_buildings.baselines.pid_plus import PIDWaterResetPolicy


class TransferPolicy(PIDWaterResetPolicy):
    """Task 1 policy: PIDWaterResetPolicy with hot-water pump off during pure cooling."""

    name = "transfer"

    def get_action(self, obs: np.ndarray) -> dict[str, Any]:
        action = super().get_action(obs)
        cont = action["continuous_action"]
        disc = action["discrete_action"]

        is_heating = (
            self.water_temp_idx is not None
            and float(cont[self.water_temp_idx]) > -1.0
        )

        if not is_heating:
            # Pure cooling or idle: shut off hot-water pump to save pump electricity
            if self.water_pressure_idx is not None:
                cont[self.water_pressure_idx] = np.float32(-1.0)
            if 0 <= self.water_discrete_idx < self.n_discrete:
                disc[self.water_discrete_idx] = np.int32(0)
        # Note: When heating IS active, keep full differential pressure (+1.0 from super())
        # because coil water flow is proportional to sqrt(differential_pressure);
        # throttling pump pressure starves reheat coils in extreme cold (Fairbanks)!

        return {"continuous_action": cont, "discrete_action": disc}
