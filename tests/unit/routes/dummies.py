from ate_api.routes.capital_schemes.bid_statuses import BidStatusModel, CapitalSchemeBidStatusDetailsModel


def dummy_bid_status_details_model() -> CapitalSchemeBidStatusDetailsModel:
    return CapitalSchemeBidStatusDetailsModel(bid_status=BidStatusModel.NOT_FUNDED)
