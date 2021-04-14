import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Spinner from "../common/spinner";
import PrefixTableBody from "./prefixTableBody";
import {findIrrSourceColumns, sortPrefixesDataBy} from "../../utils/prefixData";
import PrefixTableHeader from "./prefixTableHeader";


class PrefixTable extends Component {
    state = {sortedPrefixesData: [], irrSourceColumns: [], reducedColour: false}

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

    renderTableContent() {
        if (!this.props.hasLoaded)
            return this.renderTablePlaceholder(<Spinner/>);
        if (!this.props.prefixesData.length)
            return this.renderTablePlaceholder("No prefixes were found or query was too large to execute.");
        return <PrefixTableBody
            irrSourceColumns={this.state.irrSourceColumns}
            prefixesData={this.state.sortedPrefixesData}
            reducedColour={this.state.reducedColour}
        />
    }

    handleReducedColourChange = ({currentTarget: input}) => {
        this.setState({reducedColour: input.checked});
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
                <form className="text-end">
                    <input
                        type="checkbox"
                        id="reducedColour"
                        className="me-2"
                        checked={this.state.reducedColour}
                        onChange={this.handleReducedColourChange}
                    />
                    <label htmlFor="reducedColour">Reduced colour mode</label>
                </form>
                <table className="table table-sm mb-5 table-fixed table-striped">
                    <PrefixTableHeader
                        irrSourceColumns={this.state.irrSourceColumns}
                        onSort={this.handleSort}
                        reducedColour={this.state.reducedColour}
                    />
                    {this.renderTableContent()}
                </table>
            </>
        );
    }
}

PrefixTable.propTypes = {
    prefixesData: PropTypes.arrayOf(PropTypes.object).isRequired,
    hasLoaded: PropTypes.bool,
};


export default PrefixTable;
