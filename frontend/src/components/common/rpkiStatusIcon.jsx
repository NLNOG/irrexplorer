import React from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle, faTimesCircle} from "@fortawesome/free-regular-svg-icons";

function RPKIStatusIcon({rpkiStatus}) {
    let rpkiIcon = undefined;
    let text = '';
    if (rpkiStatus === "VALID") {
        rpkiIcon = faCheckCircle;
        text = "Route object is RPKI valid"
    } else if (rpkiStatus === "INVALID") {
        rpkiIcon = faTimesCircle;
        text = "Route object is RPKI invalid"
    } else return null;

    return (
        <>
            &nbsp;
            <span className="d-inline-block" data-bs-toggle="tooltip" title={text}>
                <FontAwesomeIcon icon={rpkiIcon}/>
            </span>
        </>
    );
}

RPKIStatusIcon.propTypes = {
    rpkiStatus: PropTypes.string,
};


export default RPKIStatusIcon;
