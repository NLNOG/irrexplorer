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
            await this.loadPrefixesData();
        }
    }

    async loadPrefixesData() {
        // As there may be confusing existing state, reset it all first
        this.setState({prefixesData: [], irrSourceColumns: [], hasLoaded: false});
        if (this.props.onLeastSpecificFound) this.props.onLeastSpecificFound(null);

        const prefixesData = await api.getPrefixesData(this.props.queryPrefix);
        this.setState({prefixesData, hasLoaded: true});
        this.updateIrrSourceColumns();
        this.notifyLeastSpecificFound();
    }

    updateIrrSourceColumns() {
        // Other than a few fixed columns, there are columns for each source
        // found for at least one prefix. This method therefore finds the set
        // of all IRR sources, used to display the columns.
        let irrSources = [];
        for (const prefixData of this.state.prefixesData) {
            const sourcesForPrefix = Object.keys(prefixData.irrRoutes);
            irrSources.push(...sourcesForPrefix);
        }
        const irrSourceColumns = _.uniq(irrSources).sort();
        this.setState({irrSourceColumns});
    }

    notifyLeastSpecificFound() {
        // The prefix query page first renders directly overlapping prefixes,
        // but if applicable, then also renders all overlaps of the least specific
        // overlapping prefix found. This method detects finds the least specific
        // prefix from the API results, and if it is shorter than the query,
        // calls a callback.
        if (!this.state.prefixesData.length || !this.props.onLeastSpecificFound)
            return
        const queryPrefixLength = this.props.queryPrefix.split('/')[1];
        const allPrefixes = this.state.prefixesData.map(({prefix}) => {
            const [ip, len] = prefix.split('/')
            return {ip, len};
        });
        allPrefixes.sort((a, b) => a.len > b.len);
        const leastSpecific = allPrefixes[0];
        if (!queryPrefixLength || leastSpecific.len < queryPrefixLength)
            this.props.onLeastSpecificFound(allPrefixes[0].ip + '/' + allPrefixes[0].len);
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
