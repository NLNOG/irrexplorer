import React from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle, faTimesCircle} from "@fortawesome/free-regular-svg-icons";


function AsnWithRPKIStatus({rpkiStatus, asn}) {
    let rpkiIcon = undefined;
    let text = '';
    let asnClass = '';
    if (rpkiStatus === "VALID") {
        rpkiIcon = faCheckCircle;
        text = "Route object is RPKI-valid"
    } else if (rpkiStatus === "INVALID") {
        rpkiIcon = faTimesCircle;
        text = "Route object is RPKI-invalid"
        asnClass = "text-decoration-line-through";
    }

    return (
        <>
            <span className="nowrap">
                <span className={asnClass}>{asn}</span>
                {rpkiIcon && <>
                    {' '}
                    <FontAwesomeIcon icon={rpkiIcon} aria-label={text}/>
                </>}
            </span>
        </>
    );
}

AsnWithRPKIStatus.propTypes = {
    rpkiStatus: PropTypes.string,
    asn: PropTypes.number.isRequired,
};


export default AsnWithRPKIStatus;
