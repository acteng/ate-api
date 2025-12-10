from datetime import UTC, datetime
from decimal import Decimal

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.observation_types import ObservationType
from ate_api.infrastructure.database import (
    AuthorityEntity,
    BidStatusEntity,
    BidStatusName,
    CapitalSchemeAuthorityReviewEntity,
    CapitalSchemeBidStatusEntity,
    CapitalSchemeEntity,
    CapitalSchemeInterventionEntity,
    CapitalSchemeOverviewEntity,
    FundingProgrammeEntity,
    InterventionMeasureEntity,
    InterventionMeasureName,
    InterventionTypeEntity,
    InterventionTypeMeasureEntity,
    InterventionTypeName,
    ObservationTypeEntity,
    ObservationTypeName,
    SchemeTypeEntity,
    SchemeTypeName,
)
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview
from tests.unit.infrastructure.database.builders import (
    build_capital_scheme_bid_status_entity,
    build_capital_scheme_overview_entity,
)


class TestCapitalSchemeEntity:
    def test_from_domain(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
            ),
        )

        capital_scheme_entity = CapitalSchemeEntity.from_domain(
            capital_scheme,
            {AuthorityAbbreviation("LIV"): 1},
            {FundingProgrammeCode("ATF3"): 2},
            {CapitalSchemeType.CONSTRUCTION: 3},
            {BidStatus.FUNDED: 4},
            {},
            {},
        )

        assert capital_scheme_entity.scheme_reference == "ATE00001"
        (overview_entity,) = capital_scheme_entity.capital_scheme_overviews
        assert (
            overview_entity.scheme_name == "Wirral Package"
            and overview_entity.bid_submitting_authority_id == 1
            and overview_entity.funding_programme_id == 2
            and overview_entity.scheme_type_id == 3
            and overview_entity.effective_date_from == datetime(2020, 1, 1)
            and not overview_entity.effective_date_to
        )
        (bid_status_entity,) = capital_scheme_entity.capital_scheme_bid_statuses
        assert (
            bid_status_entity.bid_status_id == 4
            and bid_status_entity.effective_date_from == datetime(2020, 2, 1)
            and not bid_status_entity.effective_date_to
        )
        assert not capital_scheme_entity.capital_scheme_authority_reviews

    def test_from_domain_sets_outputs(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_output(
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=OutputType.WIDENING_EXISTING_FOOTWAY,
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(1.5),
            )
        )
        capital_scheme.change_output(
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(2),
            )
        )

        capital_scheme_entity = CapitalSchemeEntity.from_domain(
            capital_scheme,
            {AuthorityAbbreviation("dummy"): 0},
            {FundingProgrammeCode("dummy"): 0},
            {CapitalSchemeType.DEVELOPMENT: 0},
            {BidStatus.SUBMITTED: 0},
            {ObservationType.ACTUAL: 3},
            {
                (OutputType.WIDENING_EXISTING_FOOTWAY, OutputMeasure.MILES): 1,
                (OutputType.NEW_SEGREGATED_CYCLING_FACILITY, OutputMeasure.MILES): 2,
            },
        )

        intervention_entity1, intervention_entity2 = capital_scheme_entity.capital_scheme_interventions
        assert (
            intervention_entity1.intervention_type_measure_id == 1
            and intervention_entity1.intervention_value == Decimal(1.5)
            and intervention_entity1.observation_type_id == 3
            and intervention_entity1.effective_date_from == datetime(2020, 1, 1)
            and not intervention_entity1.effective_date_to
        )
        assert (
            intervention_entity2.intervention_type_measure_id == 2
            and intervention_entity2.intervention_value == Decimal(2)
            and intervention_entity2.observation_type_id == 3
            and intervention_entity2.effective_date_from == datetime(2020, 1, 1)
            and not intervention_entity2.effective_date_to
        )

    def test_from_domain_sets_authority_review(self) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.perform_authority_review(
            CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1, tzinfo=UTC))
        )

        capital_scheme_entity = CapitalSchemeEntity.from_domain(
            capital_scheme,
            {AuthorityAbbreviation("dummy"): 0},
            {FundingProgrammeCode("dummy"): 0},
            {CapitalSchemeType.DEVELOPMENT: 0},
            {BidStatus.SUBMITTED: 0},
            {},
            {},
        )

        (authority_review_entity,) = capital_scheme_entity.capital_scheme_authority_reviews
        assert authority_review_entity.review_date == datetime(2020, 2, 1)

    def test_to_domain(self) -> None:
        capital_scheme_entity = CapitalSchemeEntity(
            scheme_reference="ATE00001",
            capital_scheme_overviews=[
                CapitalSchemeOverviewEntity(
                    scheme_name="Wirral Package",
                    bid_submitting_authority=AuthorityEntity(authority_abbreviation="LIV"),
                    funding_programme=FundingProgrammeEntity(funding_programme_code="ATF3"),
                    scheme_type=SchemeTypeEntity(scheme_type_name=SchemeTypeName.CONSTRUCTION),
                    effective_date_from=datetime(2020, 1, 1),
                )
            ],
            capital_scheme_bid_statuses=[
                CapitalSchemeBidStatusEntity(
                    bid_status=BidStatusEntity(bid_status_name=BidStatusName.FUNDED),
                    effective_date_from=datetime(2020, 2, 1),
                )
            ],
        )

        capital_scheme = capital_scheme_entity.to_domain()

        assert capital_scheme.reference == CapitalSchemeReference("ATE00001")
        assert capital_scheme.overview == CapitalSchemeOverview(
            effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
            name="Wirral Package",
            bid_submitting_authority=AuthorityAbbreviation("LIV"),
            funding_programme=FundingProgrammeCode("ATF3"),
            type=CapitalSchemeType.CONSTRUCTION,
        )
        assert capital_scheme.bid_status_details == CapitalSchemeBidStatusDetails(
            effective_date=DateTimeRange(datetime(2020, 2, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
        )
        assert not capital_scheme.authority_review

    def test_to_domain_sets_outputs(self) -> None:
        capital_scheme_entity = CapitalSchemeEntity(
            scheme_reference="ATE00001",
            capital_scheme_overviews=[build_capital_scheme_overview_entity()],
            capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
            capital_scheme_interventions=[
                CapitalSchemeInterventionEntity(
                    intervention_type_measure=InterventionTypeMeasureEntity(
                        intervention_type=InterventionTypeEntity(
                            intervention_type_name=InterventionTypeName.WIDENING_EXISTING_FOOTWAY
                        ),
                        intervention_measure=InterventionMeasureEntity(
                            intervention_measure_name=InterventionMeasureName.MILES
                        ),
                    ),
                    intervention_value=Decimal("1.500000"),
                    observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    effective_date_from=datetime(2020, 1, 1),
                ),
                CapitalSchemeInterventionEntity(
                    intervention_type_measure=InterventionTypeMeasureEntity(
                        intervention_type=InterventionTypeEntity(
                            intervention_type_name=InterventionTypeName.NEW_SEGREGATED_CYCLING_FACILITY
                        ),
                        intervention_measure=InterventionMeasureEntity(
                            intervention_measure_name=InterventionMeasureName.MILES
                        ),
                    ),
                    intervention_value=Decimal("2.000000"),
                    observation_type=ObservationTypeEntity(observation_type_name=ObservationTypeName.ACTUAL),
                    effective_date_from=datetime(2020, 1, 1),
                ),
            ],
        )

        capital_scheme = capital_scheme_entity.to_domain()

        assert capital_scheme.outputs == [
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=OutputType.WIDENING_EXISTING_FOOTWAY,
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(1.5),
            ),
            CapitalSchemeOutput(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=OutputType.NEW_SEGREGATED_CYCLING_FACILITY,
                measure=OutputMeasure.MILES,
                observation_type=ObservationType.ACTUAL,
                value=Decimal(2),
            ),
        ]

    def test_to_domain_sets_authority_review(self) -> None:
        capital_scheme_entity = CapitalSchemeEntity(
            scheme_reference="ATE00001",
            capital_scheme_overviews=[build_capital_scheme_overview_entity()],
            capital_scheme_bid_statuses=[build_capital_scheme_bid_status_entity()],
            capital_scheme_authority_reviews=[CapitalSchemeAuthorityReviewEntity(review_date=datetime(2020, 1, 1))],
        )

        capital_scheme = capital_scheme_entity.to_domain()

        assert capital_scheme.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 1, 1, tzinfo=UTC)
        )
