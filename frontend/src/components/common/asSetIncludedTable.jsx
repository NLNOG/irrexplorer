import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle} from "@fortawesome/free-regular-svg-icons";
import _ from 'lodash';

import Spinner from "./spinner";
import api from "../../services/api";
import {Link} from "@reach/router";


class AsSetIncludedTable extends Component {
    state = {
        hasLoaded: false,
        irrsSeen: [],
        rows: [],
    }

    async componentDidMount() {
        await this.loadSetData();
    }

    async componentDidUpdate(prevProps) {
        if (prevProps.query !== this.props.query) {
            await this.loadSetData();
        }
    }

    async loadSetData() {
        this.setState({
            hasLoaded: false,
            irrsSeen: [],
            rows: [],
        });
        const response = await api.getSetMemberOf(this.props.query);
        this.processResponse(response);
    }

    processResponse(response) {
        const irrsPerSet = {};
        if (!response.setsPerIrr) return;
        for (const [irrName, setNames] of Object.entries(response.setsPerIrr)) {
            for (const setName of setNames) {
                const existing_entries = irrsPerSet[setName] ? irrsPerSet[setName] : [];
                irrsPerSet[setName] = [...existing_entries, irrName];
            }
        }
        const rows = []
        for (const [setName, irrNames] of Object.entries(irrsPerSet)) {
            rows.push({setName, irrNames});
        }
        this.setState({
            rows: _.orderBy(rows, ['setName']),
            irrsSeen: response.irrsSeen,
            hasLoaded: true,
        })
    }

    renderTableContent() {
        const {hasLoaded, irrsSeen, rows} = this.state;
        if (!hasLoaded)
            return this.renderTablePlaceholder(<Spinner/>);
        if (!rows.length)
            return this.renderTablePlaceholder("No sets were found.");
        return (
            <>
                <thead>
                <tr>
                    <th key="name" scope="col">Name</th>
                    {irrsSeen.map(irrName =>
                        <th key={irrName} scope="col">{irrName}</th>
                    )}
                </tr>
                </thead>
                <tbody>
                {rows.map(({setName, irrNames: irrNamesForRow}) =>
                    <tr key={setName}>
                        <td key="name"><Link to={`/as-set/${setName}`}>{setName}</Link></td>
                        {irrsSeen.map(seenIrr =>
                            <td key={seenIrr} className="text-center">{
                                irrNamesForRow.includes(seenIrr)
                                    ? <FontAwesomeIcon icon={faCheckCircle} title={`Present in ${seenIrr}`}/>
                                    : ''
                            }</td>
                        )}
                    </tr>
                )}
                </tbody>
            </>
        );
    }

    renderTablePlaceholder(placeholder) {
        return (
            <tbody>
            <tr>
                <td className="text-center">{placeholder}</td>
            </tr>
            </tbody>
        );
    }

    render() {
        return (
            <table style={{width: 'auto'}} className="table mb-5 table-fixed">
                {this.renderTableContent()}
            </table>
        );
    }
}

AsSetIncludedTable.propTypes = {
    query: PropTypes.string.isRequired,
};


export default AsSetIncludedTable;
