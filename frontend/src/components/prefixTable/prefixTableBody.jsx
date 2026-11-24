import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

import AsnWithRPKIStatus from "./asnWithRPKIStatus";
import MessageBadge from "./messageBadge";
import {
    faCaretRight,
    faCheckCircle,
    faExclamationCircle,
    faQuestionCircle,
    faTimesCircle
} from "@fortawesome/free-solid-svg-icons";
import {Link} from "react-router";


function formatAsns(origins) {
    return origins.map(origin => `AS${origin}`).join(', ');
}

const rpkiStatusTexts = {
    VALID: asn => `A ROA allows AS${asn} to originate this prefix, so the route object is RPKI-valid.`,
    INVALID: asn => `A ROA covers this prefix, but none allows AS${asn} to originate it, so the route object is RPKI-invalid.`,
    NOT_FOUND: () => 'No ROA covers this prefix, so the RPKI status of the route object is unknown.',
};

function irrRouteTooltip(prefix, sourceName, asn, rpkiStatus, bgpOrigins) {
    let match;
    if (!bgpOrigins.length)
        match = 'but this prefix is not seen in the DFZ';
    else if (bgpOrigins.includes(asn))
        match = 'matching an origin seen in the DFZ';
    else
        match = `but this prefix is announced in the DFZ by ${formatAsns(bgpOrigins)}`;
    return `${sourceName} has a route object for ${prefix} with origin AS${asn}, ${match}. `
        + `${rpkiStatusTexts[rpkiStatus](asn)} Click to view the object.`;
}

function rpkiTooltip(prefix, rpkiRoutes, bgpOrigins) {
    const prefixLength = Number(prefix.split('/')[1]);
    const texts = rpkiRoutes.map(({asn, rpkiMaxLength}) => {
        if (asn === 0)
            return `A ROA for AS0 makes announcements of ${prefix} and more specific prefixes RPKI-invalid, unless another ROA allows them.`;
        const moreSpecifics = rpkiMaxLength > prefixLength
            ? ` and more specific prefixes up to /${rpkiMaxLength}` : ', but no more specific prefixes';
        return `A ROA allows AS${asn} to originate ${prefix}${moreSpecifics}.`;
    });
    const roaOrigins = rpkiRoutes.map(({asn}) => asn);
    const withoutRoa = bgpOrigins.filter(origin => !roaOrigins.includes(origin));
    for (const origin of withoutRoa)
        texts.push(`AS${origin} announces this prefix in the DFZ, but has no ROA for it.`);
    return texts.join(' ');
}


class PrefixTableBody extends Component {
    icons = {
        danger: faTimesCircle,
        warning: faExclamationCircle,
        info: faQuestionCircle,
        success: faCheckCircle,
    };

    renderSourceCell(prefix, irrRoutes, sourceName, bgpOrigins) {
        // The irrSourceColumns are dynamic per query. Not all prefixes
        // have data on all sources. This method renders a column
        // for this prefix, given a source.
        const routesForSource = irrRoutes[sourceName];
        if (!routesForSource) return <td key={sourceName}/>;
        return <td key={sourceName}>{
            routesForSource.map(
                ({asn, rpkiStatus, rpslText}, idx) => [
                    idx > 0 && ", ",
                    <a className="link-dark" key={asn} href="/"
                       title={irrRouteTooltip(prefix, sourceName, asn, rpkiStatus, bgpOrigins)}
                       onClick={(e) => {
                           e.preventDefault();
                           this.props.handleIrrRouteSelect(prefix, asn, sourceName, rpslText, rpkiStatus);
                       }}>
                        <AsnWithRPKIStatus asn={asn} rpkiStatus={rpkiStatus}/>
                    </a>
                ]
            )
        }</td>;
    }

    renderRpkiCells(prefix, rpkiRoutes, bgpOrigins) {
        const title = rpkiRoutes.length ? rpkiTooltip(prefix, rpkiRoutes, bgpOrigins) : undefined;
        return <td key="rpkiRoutes" className="mono" title={title}>{rpkiRoutes.map(
            ({asn, rpkiMaxLength}, idx) => [
                idx > 0 && ", ",
                asn, " ",
                <span key={asn} className="small">
                    <FontAwesomeIcon aria-label="max length" icon={faCaretRight}/>/{rpkiMaxLength}
                </span>
            ]
        )}</td>;
    }

    classNameForRow(categoryOverall) {
        return this.props.reducedColour ? '' : `table-${categoryOverall}`;
    }

    render() {
        const {prefixesData, irrSourceColumns, reducedColour, filterWarningError, messageExplanations} = this.props;
        let tableData = prefixesData;
        if (filterWarningError) {
            tableData = tableData.filter(({categoryOverall}) => categoryOverall === "danger" || categoryOverall === "warning");
        }
        if (!tableData.length) {
            return (
                <tbody><tr key="nodata"><td key="nodata" colSpan="100">No records with an error or warning status.</td></tr></tbody>
            )
        }
        return (
            <tbody>
            {tableData.map((
                {prefix, categoryOverall, rir, bgpOrigins, rpkiRoutes, irrRoutes, messages}) =>
                <tr key={prefix} className={this.classNameForRow(categoryOverall)}>
                    <td key="prefix"><Link to={`/prefix/${prefix}`} className="link-dark">{prefix}</Link></td>
                    <td key="rir" className="nowrap">{rir}</td>
                    <td key="bgpOrigins"><a href={`https://lg.ring.nlnog.net/prefix?q=${prefix}&match=exact&peer=all`}
                                            className="link-dark">{bgpOrigins.join(', ')}</a></td>
                    {this.renderRpkiCells(prefix, rpkiRoutes, bgpOrigins)}
                    {irrSourceColumns.map(
                        sourceName => this.renderSourceCell(prefix, irrRoutes, sourceName, bgpOrigins)
                    )}
                    {reducedColour && <td key="adviceIcon" className="lead"
                        title={`Overall status: ${categoryOverall}`}>
                        <FontAwesomeIcon icon={this.icons[categoryOverall]} aria-label={`Overall status: ${categoryOverall}`}/>
                    </td>}
                    <td key="messages">
                        {messages.map(({category, key: messageKey, text}) =>
                            <MessageBadge key={text} category={category} text={text}
                                          explanation={messageExplanations[messageKey]}
                                          reducedColour={reducedColour}/>
                        )}
                    </td>
                </tr>
            )}
            </tbody>
        );
    }
}

PrefixTableBody.propTypes = {
    irrSourceColumns: PropTypes.arrayOf(PropTypes.string).isRequired,
    prefixesData: PropTypes.arrayOf(PropTypes.object).isRequired,
    reducedColour: PropTypes.bool,
    filterWarningError: PropTypes.bool,
    handleIrrRouteSelect: PropTypes.func,
    messageExplanations: PropTypes.objectOf(PropTypes.string).isRequired,
};


export default PrefixTableBody;
