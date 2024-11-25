import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle} from "@fortawesome/free-regular-svg-icons";
import _ from 'lodash';

import Spinner from "./spinner";
import api from "../../services/api";
import {Link} from "@reach/router";
import TableFooter from "./tableFooter";


class SetIncludedTable extends Component {
    state = {
        hasLoaded: false,
        irrsSeen: [],
        rows: [],
        apiCallUrl: '',
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
            apiCallUrl: '',
        });
        const response = await api.getSetMemberOf(this.props.query, this.props.objectClass);
        this.processResponse(response);
    }

    processResponse({data, url}) {
        const irrsPerSet = {};
        if (!data.setsPerIrr) return;
        for (const [irrName, setNames] of Object.entries(data.setsPerIrr)) {
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
            irrsSeen: data.irrsSeen,
            hasLoaded: true,
            apiCallUrl: url,
        })
    }

    renderTableContent() {
        const {hasLoaded, irrsSeen, rows, apiCallUrl} = this.state;
        if (!hasLoaded)
            return this.renderTablePlaceholder(<Spinner/>);
        if (!rows.length)
            return this.renderTablePlaceholder(`No ${this.props.objectClass}s were found.`);
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
                        <td key="name"><Link to={`/${this.props.objectClass}/${setName}`}>{setName}</Link></td>
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
                <TableFooter url={apiCallUrl} />
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

SetIncludedTable.propTypes = {
    query: PropTypes.string.isRequired,
    objectClass: PropTypes.string.isRequired,
};


export default SetIncludedTable;
