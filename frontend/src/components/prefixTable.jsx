import React, {Component} from 'react';
import PropTypes from 'prop-types';
import _ from 'lodash';

import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faSort, faSortDown} from '@fortawesome/free-solid-svg-icons'

import Spinner from "./common/spinner";
import api from "../services/api";
import PrefixTableBody from "./prefixTableBody";

class PrefixTable extends Component {
    state = {prefixesData: [], irrSourceColumns: []}

    async componentDidMount() {
        await this.loadprefixesData();
    }

    async componentDidUpdate(prevProps) {
        if (prevProps.searchPrefix !== this.props.searchPrefix) {
            this.setState({prefixesData: []});
            await this.loadprefixesData();
        }
    }

    async loadprefixesData() {
        const prefixesData = await api.getPrefixesData(this.props.searchPrefix);
        this.setState({prefixesData});
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

    render() {
        return (
            <>
                {!this.state.prefixesData.length && <Spinner/>}
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
                    <PrefixTableBody
                        irrSourceColumns={this.state.irrSourceColumns}
                        prefixesData={this.state.prefixesData}
                    />
                </table>
            </>
        );
    }
}

PrefixTable.propTypes = {
    searchPrefix: PropTypes.string.isRequired,
};


export default PrefixTable;
