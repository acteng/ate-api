from datetime import UTC, date, datetime
from decimal import Decimal

from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_scheme_financials import CapitalSchemeFinancial, CapitalSchemeFinancials
from ate_api.domain.capital_scheme_milestones import CapitalSchemeMilestone, CapitalSchemeMilestones, Milestone
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.outputs import CapitalSchemeOutput, OutputMeasure, OutputType
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.data_sources import DataSource
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money
from ate_api.domain.observation_types import ObservationType
from ate_api.routes.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewModel
from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel, CapitalSchemeBidStatusDetailsModel
from ate_api.routes.capital_schemes.capital_schemes import CapitalSchemeModel
from ate_api.routes.capital_schemes.financials import CapitalSchemeFinancialModel, CapitalSchemeFinancialsModel
from ate_api.routes.capital_schemes.milestones import (
    CapitalSchemeMilestoneModel,
    CapitalSchemeMilestonesModel,
    MilestoneModel,
)
from ate_api.routes.capital_schemes.outputs import CapitalSchemeOutputModel, OutputMeasureModel, OutputTypeModel
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel
from ate_api.routes.collections import CollectionModel
from ate_api.routes.data_sources import DataSourceModel
from ate_api.routes.financial_types import FinancialTypeModel
from ate_api.routes.observation_types import ObservationTypeModel
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview
from tests.unit.routes.dummies import dummy_bid_status_details_model, dummy_overview_model


class TestCapitalSchemeModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
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
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, financials, milestones, http_request)

        assert capital_scheme_model == CapitalSchemeModel(
            id=AnyUrl(f"{base_url}/capital-schemes/ATE00001"),
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                name="Wirral Package",
                bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
                funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
                type=CapitalSchemeTypeModel.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED),
            financials=CapitalSchemeFinancialsModel(items=[]),
            milestones=CapitalSchemeMilestonesModel(current_milestone=None, items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](items=[]),
            authority_review=None,
        )

    def test_from_domain_sets_financials(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        financials.adjust_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(2_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )
        financials.adjust_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                type=FinancialType.SPEND_TO_DATE,
                amount=Money(1_000_000),
                data_source=DataSource.ATF4_BID,
            )
        )
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, financials, milestones, http_request)

        assert capital_scheme_model.financials == CapitalSchemeFinancialsModel(
            items=[
                CapitalSchemeFinancialModel(
                    type=FinancialTypeModel.FUNDING_ALLOCATION, amount=2_000_000, source=DataSourceModel.ATF4_BID
                ),
                CapitalSchemeFinancialModel(
                    type=FinancialTypeModel.SPEND_TO_DATE, amount=1_000_000, source=DataSourceModel.ATF4_BID
                ),
            ]
        )

    def test_from_domain_sets_milestones(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestones.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
                data_source=DataSource.ATF4_BID,
            )
        )
        milestones.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
                data_source=DataSource.ATF4_BID,
            )
        )

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, financials, milestones, http_request)

        assert capital_scheme_model.milestones == CapitalSchemeMilestonesModel(
            current_milestone=MilestoneModel.CONSTRUCTION_STARTED,
            items=[
                CapitalSchemeMilestoneModel(
                    milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
                    observation_type=ObservationTypeModel.ACTUAL,
                    status_date=date(2020, 2, 1),
                    source=DataSourceModel.ATF4_BID,
                ),
                CapitalSchemeMilestoneModel(
                    milestone=MilestoneModel.CONSTRUCTION_STARTED,
                    observation_type=ObservationTypeModel.ACTUAL,
                    status_date=date(2020, 3, 1),
                    source=DataSourceModel.ATF4_BID,
                ),
            ],
        )

    def test_from_domain_sets_outputs(self, http_request: Request) -> None:
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
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, financials, milestones, http_request)

        assert capital_scheme_model.outputs == CollectionModel[CapitalSchemeOutputModel](
            items=[
                CapitalSchemeOutputModel(
                    type=OutputTypeModel.WIDENING_EXISTING_FOOTWAY,
                    measure=OutputMeasureModel.MILES,
                    observation_type=ObservationTypeModel.ACTUAL,
                    value=Decimal(1.5),
                ),
                CapitalSchemeOutputModel(
                    type=OutputTypeModel.NEW_SEGREGATED_CYCLING_FACILITY,
                    measure=OutputMeasureModel.MILES,
                    observation_type=ObservationTypeModel.ACTUAL,
                    value=Decimal(2),
                ),
            ]
        )

    def test_from_domain_sets_authority_review(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.perform_authority_review(
            CapitalSchemeAuthorityReview(
                review_date=datetime(2020, 1, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
            )
        )
        financials = CapitalSchemeFinancials(capital_scheme=CapitalSchemeReference("ATE00001"))
        milestones = CapitalSchemeMilestones(capital_scheme=CapitalSchemeReference("ATE00001"))

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, financials, milestones, http_request)

        assert capital_scheme_model.authority_review == CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 1, 1, tzinfo=UTC), source=DataSourceModel.AUTHORITY_UPDATE
        )

    def test_to_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                name="Wirral Package",
                bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
                funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
                type=CapitalSchemeTypeModel.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED),
            financials=CapitalSchemeFinancialsModel(items=[]),
            milestones=CapitalSchemeMilestonesModel(items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](items=[]),
            authority_review=None,
        )

        capital_scheme = capital_scheme_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC), http_request)

        assert (
            capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview
            == CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            )
            and capital_scheme.bid_status_details
            == CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 1, 1, tzinfo=UTC)), bid_status=BidStatus.FUNDED
            )
            and not capital_scheme.authority_review
        )

    def test_to_domain_sets_outputs(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=dummy_overview_model(base_url),
            bid_status_details=dummy_bid_status_details_model(),
            financials=CapitalSchemeFinancialsModel(items=[]),
            milestones=CapitalSchemeMilestonesModel(items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](
                items=[
                    CapitalSchemeOutputModel(
                        type=OutputTypeModel.WIDENING_EXISTING_FOOTWAY,
                        measure=OutputMeasureModel.MILES,
                        observation_type=ObservationTypeModel.ACTUAL,
                        value=Decimal(1.5),
                    ),
                    CapitalSchemeOutputModel(
                        type=OutputTypeModel.NEW_SEGREGATED_CYCLING_FACILITY,
                        measure=OutputMeasureModel.MILES,
                        observation_type=ObservationTypeModel.ACTUAL,
                        value=Decimal(2),
                    ),
                ]
            ),
        )

        capital_scheme = capital_scheme_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC), http_request)

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

    def test_to_domain_sets_authority_review(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=dummy_overview_model(base_url),
            bid_status_details=dummy_bid_status_details_model(),
            financials=CapitalSchemeFinancialsModel(items=[]),
            milestones=CapitalSchemeMilestonesModel(items=[]),
            outputs=CollectionModel[CapitalSchemeOutputModel](items=[]),
            authority_review=CapitalSchemeAuthorityReviewModel(
                review_date=datetime(2020, 2, 1, tzinfo=UTC), source=DataSourceModel.AUTHORITY_UPDATE
            ),
        )

        capital_scheme = capital_scheme_model.to_domain(datetime(2020, 1, 1, tzinfo=UTC), http_request)

        assert capital_scheme.authority_review == CapitalSchemeAuthorityReview(
            review_date=datetime(2020, 2, 1, tzinfo=UTC), data_source=DataSource.AUTHORITY_UPDATE
        )
