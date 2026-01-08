from typing import Any

from ate_api.domain.capital_schemes.bid_statuses import CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview


class CapitalSchemeReference:
    def __init__(self, reference: str):
        self._reference = reference

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, CapitalSchemeReference) and self._reference == other._reference

    def __hash__(self) -> int:
        return hash(self._reference)

    def __str__(self) -> str:
        return self._reference

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self._reference)})"


class CapitalScheme:
    def __init__(
        self,
        reference: CapitalSchemeReference,
        overview: CapitalSchemeOverview,
        bid_status_details: CapitalSchemeBidStatusDetails,
    ):
        self._reference = reference
        self._overview = overview
        self._bid_status_details = bid_status_details
        self._outputs: list[CapitalSchemeOutput] = []

    @property
    def reference(self) -> CapitalSchemeReference:
        return self._reference

    @property
    def overview(self) -> CapitalSchemeOverview:
        return self._overview

    @property
    def bid_status_details(self) -> CapitalSchemeBidStatusDetails:
        return self._bid_status_details

    @property
    def outputs(self) -> list[CapitalSchemeOutput]:
        return list(self._outputs)

    def change_output(self, output: CapitalSchemeOutput) -> None:
        self._outputs.append(output)
