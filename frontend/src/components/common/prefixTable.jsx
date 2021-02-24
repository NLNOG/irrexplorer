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
        if (prevProps.queryPrefix !== this.props.queryPrefix) {
            await this.loadPrefixesData();
        }
    }

    async loadPrefixesData() {
        const prefixDataSource = new PrefixDataSource(this.props.queryPrefix, this.props.onLeastSpecificFound);
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
                <table className="table table-sm mb-5">
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
    queryPrefix: PropTypes.string.isRequired,
    onLeastSpecificFound: PropTypes.func,
};


export default PrefixTable;
