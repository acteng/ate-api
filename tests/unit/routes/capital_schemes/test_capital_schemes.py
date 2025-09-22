from datetime import date, datetime

from fastapi import Request
from pydantic import AnyUrl

from ate_api.domain.authorities import AuthorityAbbreviation
from ate_api.domain.capital_schemes.authority_reviews import CapitalSchemeAuthorityReview
from ate_api.domain.capital_schemes.bid_statuses import BidStatus, CapitalSchemeBidStatusDetails
from ate_api.domain.capital_schemes.capital_schemes import CapitalScheme, CapitalSchemeReference
from ate_api.domain.capital_schemes.financials import CapitalSchemeFinancial
from ate_api.domain.capital_schemes.milestones import CapitalSchemeMilestone, Milestone
from ate_api.domain.capital_schemes.overviews import CapitalSchemeOverview, CapitalSchemeType
from ate_api.domain.dates import DateTimeRange
from ate_api.domain.financial_types import FinancialType
from ate_api.domain.funding_programmes import FundingProgrammeCode
from ate_api.domain.moneys import Money
from ate_api.domain.observation_types import ObservationType
from ate_api.routes.capital_schemes.authority_reviews import CapitalSchemeAuthorityReviewModel
from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel, CapitalSchemeBidStatusDetailsModel
from ate_api.routes.capital_schemes.capital_schemes import CapitalSchemeModel
from ate_api.routes.capital_schemes.financials import CapitalSchemeFinancialModel
from ate_api.routes.capital_schemes.milestones import (
    CapitalSchemeMilestoneModel,
    CapitalSchemeMilestonesModel,
    MilestoneModel,
)
from ate_api.routes.capital_schemes.overviews import CapitalSchemeOverviewModel, CapitalSchemeTypeModel
from ate_api.routes.collections import CollectionModel
from ate_api.routes.financial_types import FinancialTypeModel
from ate_api.routes.observation_types import ObservationTypeModel
from tests.unit.domain.dummies import dummy_bid_status_details, dummy_overview
from tests.unit.routes.dummies import dummy_bid_status_details_model, dummy_overview_model


class TestCapitalSchemeModel:
    def test_from_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 2, 1)),
                bid_status=BidStatus.FUNDED,
            ),
        )

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, http_request)

        assert capital_scheme_model == CapitalSchemeModel(
            id=AnyUrl(f"{base_url}/capital-schemes/ATE00001"),
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                name="Wirral Package",
                bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
                funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
                type_=CapitalSchemeTypeModel.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CapitalSchemeMilestonesModel(current_milestone=None, items=[]),
            authority_review=None,
        )

    def test_from_domain_sets_financials(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(2_000_000),
            )
        )
        capital_scheme.change_financial(
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                type=FinancialType.SPEND_TO_DATE,
                amount=Money(1_000_000),
            )
        )

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, http_request)

        assert capital_scheme_model.financials.items == [
            CapitalSchemeFinancialModel(type=FinancialTypeModel.FUNDING_ALLOCATION, amount=2_000_000),
            CapitalSchemeFinancialModel(type=FinancialTypeModel.SPEND_TO_DATE, amount=1_000_000),
        ]

    def test_from_domain_sets_current_milestone(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            )
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            )
        )

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, http_request)

        assert capital_scheme_model.milestones.current_milestone == MilestoneModel.CONSTRUCTION_STARTED

    def test_from_domain_sets_milestones(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            )
        )
        capital_scheme.change_milestone(
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            )
        )

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, http_request)

        assert capital_scheme_model.milestones.items == [
            CapitalSchemeMilestoneModel(
                milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationTypeModel.ACTUAL,
                status_date=date(2020, 2, 1),
            ),
            CapitalSchemeMilestoneModel(
                milestone=MilestoneModel.CONSTRUCTION_STARTED,
                observation_type=ObservationTypeModel.ACTUAL,
                status_date=date(2020, 3, 1),
            ),
        ]

    def test_from_domain_sets_authority_review(self, http_request: Request) -> None:
        capital_scheme = CapitalScheme(
            reference=CapitalSchemeReference("ATE00001"),
            overview=dummy_overview(),
            bid_status_details=dummy_bid_status_details(),
        )
        capital_scheme.perform_authority_review(CapitalSchemeAuthorityReview(review_date=datetime(2020, 1, 1)))

        capital_scheme_model = CapitalSchemeModel.from_domain(capital_scheme, http_request)

        assert capital_scheme_model.authority_review == CapitalSchemeAuthorityReviewModel(
            review_date=datetime(2020, 1, 1)
        )

    def test_to_domain(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=CapitalSchemeOverviewModel(
                name="Wirral Package",
                bid_submitting_authority=AnyUrl(f"{base_url}/authorities/LIV"),
                funding_programme=AnyUrl(f"{base_url}/funding-programmes/ATF3"),
                type_=CapitalSchemeTypeModel.CONSTRUCTION,
            ),
            bid_status_details=CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.FUNDED),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CapitalSchemeMilestonesModel(items=[]),
            authority_review=None,
        )

        capital_scheme = capital_scheme_model.to_domain(datetime(2020, 1, 1), http_request)

        assert (
            capital_scheme.reference == CapitalSchemeReference("ATE00001")
            and capital_scheme.overview
            == CapitalSchemeOverview(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                name="Wirral Package",
                bid_submitting_authority=AuthorityAbbreviation("LIV"),
                funding_programme=FundingProgrammeCode("ATF3"),
                type=CapitalSchemeType.CONSTRUCTION,
            )
            and capital_scheme.bid_status_details
            == CapitalSchemeBidStatusDetails(
                effective_date=DateTimeRange(datetime(2020, 1, 1)), bid_status=BidStatus.FUNDED
            )
            and not capital_scheme.milestones
            and not capital_scheme.authority_review
        )

    def test_to_domain_sets_financials(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=dummy_overview_model(base_url),
            bid_status_details=dummy_bid_status_details_model(),
            financials=CollectionModel[CapitalSchemeFinancialModel](
                items=[
                    CapitalSchemeFinancialModel(type=FinancialTypeModel.FUNDING_ALLOCATION, amount=2_000_000),
                    CapitalSchemeFinancialModel(type=FinancialTypeModel.SPEND_TO_DATE, amount=1_000_000),
                ]
            ),
            milestones=CapitalSchemeMilestonesModel(items=[]),
        )

        capital_scheme = capital_scheme_model.to_domain(datetime(2020, 1, 1), http_request)

        assert capital_scheme.financials == [
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                type=FinancialType.FUNDING_ALLOCATION,
                amount=Money(2_000_000),
            ),
            CapitalSchemeFinancial(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                type=FinancialType.SPEND_TO_DATE,
                amount=Money(1_000_000),
            ),
        ]

    def test_to_domain_sets_milestones(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=dummy_overview_model(base_url),
            bid_status_details=dummy_bid_status_details_model(),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CapitalSchemeMilestonesModel(
                items=[
                    CapitalSchemeMilestoneModel(
                        milestone=MilestoneModel.DETAILED_DESIGN_COMPLETED,
                        observation_type=ObservationTypeModel.ACTUAL,
                        status_date=date(2020, 2, 1),
                    ),
                    CapitalSchemeMilestoneModel(
                        milestone=MilestoneModel.CONSTRUCTION_STARTED,
                        observation_type=ObservationTypeModel.ACTUAL,
                        status_date=date(2020, 3, 1),
                    ),
                ]
            ),
        )

        capital_scheme = capital_scheme_model.to_domain(datetime(2020, 1, 1), http_request)

        assert capital_scheme.milestones == [
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.DETAILED_DESIGN_COMPLETED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 2, 1),
            ),
            CapitalSchemeMilestone(
                effective_date=DateTimeRange(datetime(2020, 1, 1)),
                milestone=Milestone.CONSTRUCTION_STARTED,
                observation_type=ObservationType.ACTUAL,
                status_date=date(2020, 3, 1),
            ),
        ]

    def test_to_domain_sets_authority_review(self, http_request: Request, base_url: str) -> None:
        capital_scheme_model = CapitalSchemeModel(
            reference="ATE00001",
            overview=dummy_overview_model(base_url),
            bid_status_details=dummy_bid_status_details_model(),
            financials=CollectionModel[CapitalSchemeFinancialModel](items=[]),
            milestones=CapitalSchemeMilestonesModel(items=[]),
            authority_review=CapitalSchemeAuthorityReviewModel(review_date=datetime(2020, 2, 1)),
        )

        capital_scheme = capital_scheme_model.to_domain(datetime(2020, 1, 1), http_request)

        assert capital_scheme.authority_review == CapitalSchemeAuthorityReview(review_date=datetime(2020, 2, 1))
