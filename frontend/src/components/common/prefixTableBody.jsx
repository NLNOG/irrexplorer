import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

import AsnWithRPKIStatus from "./asnWithRPKIStatus";
import MessageBadge from "./messageBadge";
import {faCaretRight} from "@fortawesome/free-solid-svg-icons";


class PrefixTableBody extends Component {
    renderSourceCell(irrRoutes, sourceName) {
        // The irrSourceColumns are dynamic per query. Not all prefixes
        // have data on all sources. This method renders the columns
        // for this prefix, given the sources.
        const routesForSource = irrRoutes[sourceName];
        if (!routesForSource) return <td key={sourceName}/>;
        return <td key={sourceName}>{routesForSource.map(
            ({asn, rpkiStatus}, idx) => [
                idx > 0 && ", ",
                <AsnWithRPKIStatus key={asn} asn={asn} rpkiStatus={rpkiStatus}/>
            ]
        )}</td>;
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

    render() {
        const {prefixesData, irrSourceColumns} = this.props;
        return (
            <tbody>
            {prefixesData.map((
                {prefix, categoryOverall, rir, bgpOrigins, rpkiRoutes, irrRoutes, messages}) =>
                <tr key={prefix} className={`table-${categoryOverall}`}>
                    <td key="prefix">{prefix}</td>
                    <td key="rir" className="nowrap">{rir}</td>
                    <td key="bgpOrigins">{bgpOrigins.join()}</td>
                    {this.renderRpkiCells(rpkiRoutes)}
                    {irrSourceColumns.map(
                        sourceName => this.renderSourceCell(irrRoutes, sourceName)
                    )}
                    <td key="messages">
                        {messages.map(({category, text}) =>
                            <MessageBadge key={text} category={category} text={text}/>
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
};


export default PrefixTableBody;
