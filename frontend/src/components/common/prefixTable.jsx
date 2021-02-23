import React, {Component} from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faSort, faSortDown} from '@fortawesome/free-solid-svg-icons'

import Spinner from "./spinner";
import api from "../../services/api";
import PrefixTableBody from "./prefixTableBody";

class PrefixTable extends Component {
    state = {prefixesData: [], irrSourceColumns: [], hasLoaded: false}

    async componentDidMount() {
        await this.loadPrefixesData();
    }

    async componentDidUpdate(prevProps) {
        if (prevProps.queryPrefix !== this.props.queryPrefix) {
            this.setState({prefixesData: []});
            await this.loadPrefixesData();
        }
    }

    async loadPrefixesData() {
        const prefixesData = await api.getPrefixesData(this.props.queryPrefix);
        this.setState({prefixesData, hasLoaded: true});
        this.updateIrrSourceColumns();
    }

    updateIrrSourceColumns() {
        let irrSources = [];
        for (const prefixData of this.state.prefixesData) {
            const sourcesForPrefix = Object.keys(prefixData.irrRoutes);
            irrSources.push(...sourcesForPrefix);
        }
        const irrSourceColumns = _.uniq(irrSources).sort();
        this.setState({irrSourceColumns});
    }

    renderTableContent() {
        const {hasLoaded, irrSourceColumns, prefixesData} = this.state;
        if (!hasLoaded) return;
        if (!prefixesData.length)
            return (
                <tbody>
                <td colSpan="5">No prefixes were found.</td>
                </tbody>
            )
        return <PrefixTableBody
            irrSourceColumns={irrSourceColumns}
            prefixesData={prefixesData}
        />

    }

    render() {
        return (
            <>
                {!this.state.hasLoaded && <Spinner/>}
                <table className="table  table-sm">
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
};


export default PrefixTable;
