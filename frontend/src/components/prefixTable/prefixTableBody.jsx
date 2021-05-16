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
import {Link} from "@reach/router";


class PrefixTableBody extends Component {
    icons = {
        danger: faTimesCircle,
        warning: faExclamationCircle,
        info: faQuestionCircle,
        success: faCheckCircle,
    };

    renderSourceCell(prefix, irrRoutes, sourceName) {
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

    renderRpkiCells(rpkiRoutes) {
        return <td key="rpkiRoutes" className="mono">{rpkiRoutes.map(
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
        const {prefixesData, irrSourceColumns, reducedColour} = this.props;
        return (
            <tbody>
            {prefixesData.map((
                {prefix, categoryOverall, rir, bgpOrigins, rpkiRoutes, irrRoutes, messages}) =>
                <tr key={prefix} className={this.classNameForRow(categoryOverall)}>
                    <td key="prefix"><Link to={`/prefix/${prefix}`} className="link-dark">{prefix}</Link></td>
                    <td key="rir" className="nowrap">{rir}</td>
                    <td key="bgpOrigins"><a href={`http://lg.ring.nlnog.net/query/${prefix}`}
                                            className="link-dark">{bgpOrigins.join(', ')}</a></td>
                    {this.renderRpkiCells(rpkiRoutes)}
                    {irrSourceColumns.map(
                        sourceName => this.renderSourceCell(prefix, irrRoutes, sourceName)
                    )}
                    {reducedColour && <td key="adviceIcon" className="lead">
                        <FontAwesomeIcon icon={this.icons[categoryOverall]} title={`Status: ${categoryOverall}`}/>
                    </td>}
                    <td key="messages">
                        {messages.map(({category, text}) =>
                            <MessageBadge key={text} category={category} text={text}
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
    handleIrrRouteSelect: PropTypes.func,
};


export default PrefixTableBody;
