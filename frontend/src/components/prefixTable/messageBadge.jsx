import React from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle, faExclamationCircle, faQuestionCircle, faTimesCircle} from "@fortawesome/free-solid-svg-icons";

function MessageBadge({category, text, reducedColour}) {
    let classes = '';
    if(!reducedColour) {
        classes = `badge bg-${category} `
        if (category === 'warning' || category === 'info')
            classes += 'text-dark '
    }

    const icons = {
        danger: faTimesCircle,
        warning: faExclamationCircle,
        info: faQuestionCircle,
        success: faCheckCircle,
    };
    return (
        <>
            <span className={classes}><FontAwesomeIcon icon={icons[category]} title={category}/> {text}</span>
            <br/>
        </>
    );
}

MessageBadge.propTypes = {
    category: PropTypes.string.isRequired,
    text: PropTypes.string.isRequired,
    reducedColour: PropTypes.bool,
};


export default MessageBadge;
