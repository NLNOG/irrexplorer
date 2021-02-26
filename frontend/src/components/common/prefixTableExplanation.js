import React from 'react';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle, faTimesCircle} from "@fortawesome/free-regular-svg-icons";

function PrefixTableExplanation() {
    function renderPrefixTableBody() {
        return (
            <>
                <p className="lead">
                    The table with prefixes shows prefixes relating to your query. In some cases, there
                    might be two tables: one with direct overlaps of your query, and a second with all
                    overlaps of the least specific query found in the first table.
                </p>

                <p>The table has a number of columns:</p>
                <dl className="row">
                    <dt className="col-sm-2">Prefix</dt>
                    <dd className="col-sm-10">The prefix found in either BGP, RPKI or IRR.</dd>
                    <dt className="col-sm-2">RIR</dt>
                    <dd className="col-sm-10">The RIR that allocated/assigned this prefix.</dd>
                    <dt className="col-sm-2">BGP</dt>
                    <dd className="col-sm-10">The originating AS number(s) seen in the DFZ for this prefix.</dd>
                    <dt className="col-sm-2">RPKI</dt>
                    <dd className="col-sm-10">
                        ASNs seen in RPKI ROAs for this prefix, along with the maximum prefix length in the ROA.
                    </dd>
                    <dt className="col-sm-2">Columns for each IRR</dt>
                    <dd className="col-sm-10">
                        The originating AS number(s) seen in route(6) objects in various IRR databases.
                        For each origin,
                        {' '}<FontAwesomeIcon icon={faCheckCircle} title="Route object is RPKI valid"/>{' '}
                        means the object is valid according to RPKI origin validation,
                        {' '}<FontAwesomeIcon icon={faTimesCircle} title="Route object is RPKI invalid"/>{' '}
                        means it is invalid, and no icon means that no relevant ROA was found.
                    </dd>
                    <dt className="col-sm-2">Advice</dt>
                    <dd className="col-sm-10">
                        Information, warnings, and alerts about this prefix and its BGP, IRR and RPKI
                        status. IRR explorer makes a best effort at identifying possible misconfigurations,
                        but do note that there are unusual setups that may raise false alarms.
                    </dd>
                </dl>
                <p>
                    Note that an origin may have an RPKI status, even when there is no RPKI origin, i.e. no ROA,
                    for that exact prefix. For example, let's say there is a ROA for 192.0.2.0/22 AS65540 with a
                    max length of 24, and a route object for 192.0.2.0/24 AS65540. You will see two prefix rows:
                    one for the /22, and one for the /24. The /24 row will not show an RPKI origin, because there
                    is no ROA for 192.0.2.0/24. However, because there is a covering ROA for the /22, the IRR origin
                    will be shown as RPKI valid.
                </p>
            </>
        );
    }

    function renderAdviceExplanationBody() {
        return (
            <>
                <dl className="row">
                    <dt className="col-sm-3">Route objects exist, but prefix not seen in DFZ</dt>
                    <dd className="col-sm-9">
                        There are route objects for this prefix, but the prefix is not seen in the DFZ.
                        If the prefix is no longer in use, you should clean up these route objects.
                        If you plan to announce this prefix in the future, this is harmless.
                    </dd>
                    <dt className="col-sm-3">No route objects match DFZ origin</dt>
                    <dd className="col-sm-9">
                        None of the route objects (if there are any) match the origin(s) seen
                        in the DFZ. This can have a significant on reachability, and you
                        should create route objects for this prefix.
                    </dd>
                    <dt className="col-sm-3">RPKI origin does not match BGP origin</dt>
                    <dd className="col-sm-9">
                        The origin(s) in the ROA(s) for this prefix do not match the
                        origin in the DFZ. This means your prefix is not reachable by
                        anyone dropping RPKI invalid routes, which is increasingly common.
                        You should create the appropriate ROA(s) for this prefix.
                    </dd>
                    <dt className="col-sm-3">RPKI invalid route objects found</dt>
                    <dd className="col-sm-9">
                        Some or all of the IRR route objects for this prefix are invalid according
                        to RPKI origin validation. This means they are misconfigured or outdated.
                        You should look into whether your ROAs or route objects are wrong
                        or outdated, and update them.
                    </dd>
                    <dt className="col-sm-3">No (covering) RPKI ROA found for route objects</dt>
                    <dd className="col-sm-9">
                        IRR route objects were found, that are not covered by any ROA. Note that
                        to be covered, there does not need to be a ROA for this exact prefix -
                        a less specific ROA with appropriate max length will also suffice.
                    </dd>
                </dl>
                <p>
                    For more guidance on RPKI, <a href="https://rpki.readthedocs.io/en/latest/rpki/securing-bgp.html">
                    see this very extensive guide</a>.
                </p>
                <p>
                    IRR explorer makes a best effort at identifying possible misconfigurations,
                    but do note that there are unusual setups that may raise false alarms.
                </p>
            </>
        );
    }

    return (
        <div className="accordion" id="prefixTableExplanationAccordion">
            <div className="accordion-item">
                <h2 className="accordion-header" id="headingOne">
                    <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
                        What does the prefix table show?
                    </button>
                </h2>
                <div id="collapseOne" className="accordion-collapse collapse" aria-labelledby="headingOne"
                     data-bs-parent="#prefixTableExplanationAccordion">
                    <div className="accordion-body">
                        {renderPrefixTableBody()}
                    </div>
                </div>
            </div>
            <div className="accordion-item">
                <h2 className="accordion-header" id="headingTwo">
                    <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                            data-bs-target="#collapseTwo" aria-expanded="true" aria-controls="collapseTwo">
                        Explanation of different messages
                    </button>
                </h2>
                <div id="collapseTwo" className="accordion-collapse collapse" aria-labelledby="headingTwo"
                     data-bs-parent="#prefixTableExplanationAccordion">
                    <div className="accordion-body">
                        {renderAdviceExplanationBody()}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default PrefixTableExplanation;
