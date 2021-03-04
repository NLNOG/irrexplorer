import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle} from "@fortawesome/free-regular-svg-icons";
import _ from 'lodash';

import Spinner from "./spinner";
import api from "../../services/api";


class AsSetTable extends Component {
    state = {
        hasLoadedSets: false,
        irrsSeen: [],
        rows: [],
    }

    async componentDidMount() {
        await this.loadSetData();
    }

    async componentDidUpdate(prevProps) {
        if (prevProps.queryASN !== this.props.queryASN) {
            await this.loadSetData();
        }
    }

    async loadSetData() {
        this.setState({
            hasLoadedSets: false,
            irrsSeen: [],
            rows: [],
        });
        const response = await api.getSetMemberOf(this.props.queryASN);
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
            hasLoadedSets: true,
        })
    }

    renderTableContent() {
        const {hasLoadedSets, irrsSeen, rows} = this.state;
        if (!hasLoadedSets)
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
                        <td key={setName}>{setName}</td>
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

AsSetTable.propTypes = {
    queryASN: PropTypes.string.isRequired,
};


export default AsSetTable;
