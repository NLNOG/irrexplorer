import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Spinner from "./spinner";
import PrefixTableBody from "./prefixTableBody";
import {PrefixDataSource, sortPrefixesDataBy} from "../../services/prefixDataSource";
import PrefixTableHeader from "./prefixTableHeader";


class PrefixTable extends Component {
    state = {prefixesData: [], irrSourceColumns: [], hasLoaded: false}

    async componentDidMount() {
        await this.loadPrefixesData();
    }

    async componentDidUpdate(prevProps) {
        const {query, queryType} = this.props;
        if (prevProps.query !== query || prevProps.queryType !== queryType) {
            await this.loadPrefixesData();
        }
    }

    async loadPrefixesData() {
        const {query, queryType, onLeastSpecificFound} = this.props;
        const prefixDataSource = new PrefixDataSource(queryType, query, onLeastSpecificFound);
        this.setState({...prefixDataSource.reset()});
        this.setState({...await prefixDataSource.load()});
    }

    handleSort = ({key, order}) => {
        const prefixesData = sortPrefixesDataBy(this.state.prefixesData, key, order);
        this.setState({prefixesData});
    }

    renderTableContent() {
        const {hasLoaded, irrSourceColumns, prefixesData} = this.state;
        if (!hasLoaded)
            return this.renderTablePlaceholder(<Spinner/>);
        if (!prefixesData.length)
            return this.renderTablePlaceholder("No prefixes were found.")
        return <PrefixTableBody
            irrSourceColumns={irrSourceColumns}
            prefixesData={prefixesData}
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
                <table className="table table-sm mb-5 table-fixed">
                    <PrefixTableHeader
                        irrSourceColumns={this.state.irrSourceColumns}
                        onSort={this.handleSort}
                    />
                    {this.renderTableContent()}
                </table>
            </>
        );
    }
}

PrefixTable.propTypes = {
    query: PropTypes.any,
    queryType: PropTypes.string,
    onLeastSpecificFound: PropTypes.func,
};


export default PrefixTable;
