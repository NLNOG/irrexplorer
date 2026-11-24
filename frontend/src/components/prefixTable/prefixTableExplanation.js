import React, {useEffect, useState} from 'react';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle, faTimesCircle} from "@fortawesome/free-regular-svg-icons";

import api from "../../services/api";
import MessageBadge from "./messageBadge";
import columnDescriptions from "./columnDescriptions";

function PrefixTableExplanation() {
    // The API lists every message the report can include
    const [catalogue, setCatalogue] = useState({});

    useEffect(() => {
        api.getMessageCatalogue().then(setCatalogue);
    }, []);

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
                    <dd className="col-sm-10">{columnDescriptions.prefix}</dd>
                    <dt className="col-sm-2">RIR</dt>
                    <dd className="col-sm-10">{columnDescriptions.rir}</dd>
                    <dt className="col-sm-2">BGP</dt>
                    <dd className="col-sm-10">{columnDescriptions.bgp}</dd>
                    <dt className="col-sm-2">RPKI</dt>
                    <dd className="col-sm-10">{columnDescriptions.rpki}</dd>
                    <dt className="col-sm-2">Columns for each IRR</dt>
                    <dd className="col-sm-10">
                        {columnDescriptions.irr}
                        {' '}For each origin,
                        {' '}<FontAwesomeIcon icon={faCheckCircle} title="Route object is RPKI-valid"/>{' '}
                        means the route object is RPKI-valid and
                        {' '}<FontAwesomeIcon icon={faTimesCircle} title="Route object is RPKI-invalid"/>{' '}
                        means it is RPKI-invalid. No icon means no ROA covers the prefix, so the RPKI
                        status of the route object is unknown.
                    </dd>
                    <dt className="col-sm-2">Advice</dt>
                    <dd className="col-sm-10">{columnDescriptions.advice}</dd>
                </dl>
                <p>
                    A route object can be RPKI-valid even when there is no ROA for its prefix, because a ROA
                    for a less specific prefix can also allow its origin. For example, say there is a ROA for
                    2001:db8::/32 AS65540 with a maximum length of 48, and a route object for 2001:db8:1::/48
                    AS65540. You will see two prefix rows: one for the /32, and one for the /48. The RPKI column
                    of the /48 row is empty, because there is no ROA for 2001:db8:1::/48. The route object is
                    still RPKI-valid, because the ROA for the /32 allows AS65540 to originate the /48.
                </p>
            </>
        );
    }

    function renderMessageExplanations() {
        const {data, error} = catalogue;
        if (error)
            return <p>{error}</p>;
        return data && <dl className="row">
            {data.map(({key, category, text, explanation}) => <React.Fragment key={key}>
                <dt className="col-sm-3"><MessageBadge category={category} text={text}/></dt>
                <dd className="col-sm-9">{explanation}</dd>
            </React.Fragment>)}
        </dl>;
    }

    function renderAdviceExplanationBody() {
        return (
            <>
                <p>
                    Below, &lt;IRR&gt; stands for the IRR of the RIR responsible for the prefix,
                    for example RIPE for RIPE NCC address space.
                </p>
                {renderMessageExplanations()}
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
