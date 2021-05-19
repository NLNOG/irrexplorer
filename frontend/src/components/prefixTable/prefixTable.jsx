import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Spinner from "../common/spinner";
import PrefixTableBody from "./prefixTableBody";
import {findIrrSourceColumns, sortPrefixesDataBy} from "../../utils/prefixData";
import PrefixTableHeader from "./prefixTableHeader";
import WhoisModal from "./whoisModal";
import TableFooter from "../common/tableFooter";


class PrefixTable extends Component {
    state = {sortedPrefixesData: [], irrSourceColumns: []}

    constructor(props) {
        super(props);
        this.whoisModalRef = React.createRef();
    }

    componentDidMount() {
        this.updateState();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.prefixesData !== this.props.prefixesData)
            this.updateState();
    }

    updateState() {
        this.setState({
            sortedPrefixesData: sortPrefixesDataBy(this.props.prefixesData, 'prefix'),
            irrSourceColumns: findIrrSourceColumns(this.props.prefixesData),
        });

    }

    handleSort = ({key, order}) => {
        const sortedPrefixesData = sortPrefixesDataBy(this.props.prefixesData, key, order);
        this.setState({sortedPrefixesData});
    }

    handleIrrRouteSelect = (prefix, asn, sourceName, rpslText, rpkiStatus) => {
        this.whoisModalRef.current.openWithContent(prefix, asn, sourceName, rpslText, rpkiStatus);
    }

    renderTableContent() {
        if (!this.props.hasLoaded)
            return this.renderTablePlaceholder(<Spinner/>);
        if (!this.props.prefixesData.length)
            return this.renderTablePlaceholder("No prefixes were found or query was too large to execute.");
        return <PrefixTableBody
            irrSourceColumns={this.state.irrSourceColumns}
            prefixesData={this.state.sortedPrefixesData}
            reducedColour={this.props.reducedColour}
            handleIrrRouteSelect={this.handleIrrRouteSelect}
        />
    }

    renderTablePlaceholder(placeholder) {
        return (
            <tbody>
            <tr>
                <td colSpan="5" className="text-center">{placeholder}</td>
            </tr>
            </tbody>
        );
    }

    render() {
        return (
            <>
                <table className="table table-sm mb-5 table-fixed table-striped">
                    <PrefixTableHeader
                        irrSourceColumns={this.state.irrSourceColumns}
                        onSort={this.handleSort}
                        reducedColour={this.props.reducedColour}
                    />
                    {this.renderTableContent()}
                    <TableFooter url={this.props.apiCallUrl} />
                </table>
                <WhoisModal ref={this.whoisModalRef}/>
            </>
        );
    }
}

PrefixTable.propTypes = {
    prefixesData: PropTypes.arrayOf(PropTypes.object).isRequired,
    hasLoaded: PropTypes.bool,
    reducedColour: PropTypes.bool,
    apiCallUrl: PropTypes.string,
};


export default PrefixTable;
