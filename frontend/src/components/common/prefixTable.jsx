import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faSort, faSortDown} from '@fortawesome/free-solid-svg-icons'

import Spinner from "./spinner";
import PrefixTableBody from "./prefixTableBody";
import PrefixDataSource from "../../services/prefixDataSource";

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
                    <thead>
                    <tr>
                        <th scope="col">Prefix <FontAwesomeIcon icon={faSortDown}/></th>
                        <th scope="col">RIR <FontAwesomeIcon icon={faSort}/></th>
                        <th scope="col">BGP <FontAwesomeIcon icon={faSort}/></th>
                        <th scope="col">RPKI <FontAwesomeIcon icon={faSort}/></th>
                        {this.state.irrSourceColumns.map(sourceName =>
                            <th scope="col" key={sourceName}>{sourceName} <FontAwesomeIcon icon={faSort}/></th>
                        )}
                        <th scope="col" className="messages">Advice</th>
                    </tr>
                    </thead>
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
