import React, {Component} from 'react';
import PropTypes from 'prop-types';

import RPKIStatusIcon from "./common/rpkiStatusIcon";
import MessageBadge from "./common/messageBadge";


class PrefixTableBody extends Component {
    renderSourceCells(irrRoutes) {
        return this.props.irrSourceColumns.map(
            sourceName => this.renderSourceCell(irrRoutes, sourceName)
        );
    }

    renderSourceCell(irrRoutes, sourceName) {
        const routesForSource = irrRoutes[sourceName];
        if (!routesForSource) return <td key={sourceName}/>;
        return <td key={sourceName}>{routesForSource.map(
            ({asn, rpkiStatus}, idx) => [
                idx > 0 && ", ",
                <span key={asn} className="nowrap">
                    {asn}
                    <RPKIStatusIcon rpkiStatus={rpkiStatus}/>
                </span>
            ]
        )}</td>;
    }

    renderMessages(messages) {
        return messages.map(
            ({category, text}) => <MessageBadge key={text} category={category} text={text}/>
        );
    }

    render() {
        return (
            <tbody>
            {this.props.prefixesData.map((
                {prefix, categoryOverall, rir, bgpOrigins, rpkiRoutes, irrRoutes, messages}) =>
                <tr key={prefix} className={`table-${categoryOverall}`}>
                    <td key="prefix">{prefix}</td>
                    <td key="rir" className="nowrap">{rir}</td>
                    <td key="bgpOrigins">{bgpOrigins.join()}</td>
                    <td key="rpkiRoutes">{rpkiRoutes.map(rpkiRoute => rpkiRoute.asn).join(', ')}</td>
                    {this.renderSourceCells(irrRoutes)}
                    <td key="messages" className="messages">{this.renderMessages(messages)}</td>
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
