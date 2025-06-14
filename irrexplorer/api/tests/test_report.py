from ipaddress import ip_network

from irrexplorer.api.interfaces import (
    MessageCategory,
    PrefixIRRDetail,
    PrefixSummary,
    ReportMessage,
)
from irrexplorer.api.report import enrich_prefix_summaries_with_report
from irrexplorer.state import RIR, RPKIStatus


def test_report_good():
    summary = PrefixSummary(
        prefix=ip_network("2001:db8::/48"),
        rir=RIR.RIPENCC,
        bgp_origins={65540},
        rpki_routes=[
            PrefixIRRDetail(
                rpsl_pk="2001:db8::/48AS65540ML25",
                asn=65540,
                rpki_status=RPKIStatus.valid,
                rpsl_text="rpsl object text",
            )
        ],
        irr_routes={
            "RIPE": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540ML25",
                    asn=65540,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                )
            ],
        },
    )
    enrich_prefix_summaries_with_report([summary])
    assert summary.category_overall == MessageCategory.SUCCESS
    assert summary.goodness_overall == 3
    assert summary.messages == [
        ReportMessage(category=MessageCategory.SUCCESS, text="Everything looks good"),
    ]
    assert summary.prefix_sort_key == "42540766411282592856903984951653826560/48"


def test_report_no_origin():
    summary = PrefixSummary(
        prefix=ip_network("2001:db8::/48"),
        rir=RIR.RIPENCC,
        rpki_routes=[
            PrefixIRRDetail(
                rpsl_pk="2001:db8::/48AS65540ML25",
                asn=65540,
                rpki_status=RPKIStatus.valid,
                rpsl_text="rpsl object text",
            )
        ],
        irr_routes={
            "RIPE": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                )
            ],
        },
    )
    enrich_prefix_summaries_with_report([summary])
    assert summary.category_overall == MessageCategory.INFO
    assert summary.goodness_overall == 2
    assert summary.messages == [
        ReportMessage(
            category=MessageCategory.INFO,
            text="Route objects exist, but prefix not seen in DFZ",
        ),
        ReportMessage(
            category=MessageCategory.INFO, text="RPKI ROA exists, but prefix not seen in DFZ"
        ),
    ]


def test_report_no_origin_no_roa():
    summary = PrefixSummary(
        prefix=ip_network("2001:db8::/48"),
        rir=RIR.RIPENCC,
        irr_routes={
            "RADB": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.not_found,
                    rpsl_text="rpsl object text",
                )
            ],
        },
    )
    enrich_prefix_summaries_with_report([summary])
    assert summary.category_overall == MessageCategory.WARNING
    assert summary.goodness_overall == 1
    assert summary.messages == [
        ReportMessage(
            category=MessageCategory.WARNING,
            text="Expected route object in RIPE, but only found in other IRRs",
        ),
        ReportMessage(
            category=MessageCategory.INFO, text="Route objects exist, but prefix not seen in DFZ"
        ),
        ReportMessage(
            category=MessageCategory.INFO, text="No (covering) RPKI ROA found for route objects"
        ),
    ]


def test_report_rpki_invalid():
    summary = PrefixSummary(
        prefix=ip_network("2001:db8::/48"),
        rir=RIR.RIPENCC,
        bgp_origins={65540},
        rpki_routes=[
            PrefixIRRDetail(
                rpsl_pk="2001:db8::/48AS65541ML25",
                asn=65541,
                rpki_status=RPKIStatus.valid,
                rpsl_text="rpsl object text",
            )
        ],
        irr_routes={
            "RIPE": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.invalid,
                    rpsl_text="rpsl object text",
                )
            ],
            "RADB": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.invalid,
                    rpsl_text="rpsl object text",
                )
            ],
        },
    )
    enrich_prefix_summaries_with_report([summary])
    assert summary.category_overall == MessageCategory.DANGER
    assert summary.goodness_overall == 0
    assert summary.messages == [
        ReportMessage(
            category=MessageCategory.DANGER, text="RPKI origin does not match BGP origin"
        ),
        ReportMessage(category=MessageCategory.DANGER, text="RPKI-invalid route objects found"),
    ]


def test_report_invalid_origin_expected_irr():
    summary = PrefixSummary(
        prefix=ip_network("2001:db8::/48"),
        rir=RIR.RIPENCC,
        bgp_origins={65540},
        irr_routes={
            "RIPE": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65541",
                    asn=65541,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                )
            ],
            "RADB": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                )
            ],
        },
    )
    enrich_prefix_summaries_with_report([summary])
    assert summary.category_overall == MessageCategory.DANGER
    assert summary.goodness_overall == 0
    assert summary.messages == [
        ReportMessage(
            category=MessageCategory.DANGER,
            text="Expected route object in RIPE, but BGP origin does not match. Objects from other IRRs do match BGP origin",
        ),
    ]


def test_report_invalid_origin_other_irr():
    summary = PrefixSummary(
        prefix=ip_network("2001:db8::/48"),
        rir=RIR.RIPENCC,
        bgp_origins={65540},
        irr_routes={
            "RIPE": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                )
            ],
            "RADB": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65541",
                    asn=65541,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                )
            ],
        },
    )
    enrich_prefix_summaries_with_report([summary])
    assert summary.category_overall == MessageCategory.WARNING
    assert summary.goodness_overall == 1
    assert summary.messages == [
        ReportMessage(
            category=MessageCategory.WARNING,
            text="Expected route object in RIPE matches BGP origin, but non-matching objects exist in other IRRs",
        ),
    ]


def test_report_multiple_irr_origins():
    summary = PrefixSummary(
        prefix=ip_network("2001:db8::/48"),
        rir=RIR.RIPENCC,
        bgp_origins={65540},
        irr_routes={
            "RIPE": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                ),
            ],
            "RADB": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                ),
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65541",
                    asn=65541,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                ),
            ],
        },
    )
    enrich_prefix_summaries_with_report([summary])
    assert summary.category_overall == MessageCategory.WARNING
    assert summary.goodness_overall == 1
    assert summary.messages == [
        ReportMessage(
            category=MessageCategory.WARNING,
            text="Multiple route objects exist with different origins, but DFZ only has one",
        ),
    ]


def test_report_multiple_bgp_and_irr_origins():
    summary = PrefixSummary(
        prefix=ip_network("2001:db8::/48"),
        rir=RIR.RIPENCC,
        bgp_origins={65540, 65542},
        irr_routes={
            "RIPE": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                ),
            ],
            "RADB": [
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65540",
                    asn=65540,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                ),
                PrefixIRRDetail(
                    rpsl_pk="2001:db8::/48AS65541",
                    asn=65541,
                    rpki_status=RPKIStatus.valid,
                    rpsl_text="rpsl object text",
                ),
            ],
        },
    )
    enrich_prefix_summaries_with_report([summary])
    assert summary.category_overall == MessageCategory.DANGER
    assert summary.goodness_overall == 0
    assert summary.messages == [
        ReportMessage(
            category=MessageCategory.DANGER,
            text="No route objects for some DFZ origins",
        ),
    ]
