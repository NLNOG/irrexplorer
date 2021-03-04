import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheckCircle} from "@fortawesome/free-regular-svg-icons";
import _ from 'lodash';

import Spinner from "./spinner";


class AsSetTable extends Component {
    state = {rows: []}

    componentDidMount() {
        this.updateState();
    }

    componentDidUpdate(prevProps) {
        if (prevProps.setsPerIrr !== this.props.setsPerIrr)
            this.updateState();
    }

    updateState() {
        const setsPerIrr = {};
        if (!this.props.setsPerIrr) return;
        for (const [irrName, setNames] of Object.entries(this.props.setsPerIrr)) {
            for (const setName of setNames) {
                setsPerIrr[setName] = [...setsPerIrr[setName] ? setsPerIrr[setName] : [], irrName];
            }
        }
        const rows = []
        for(const [setName, irrNames] of Object.entries(setsPerIrr)) {
            rows.push({setName, irrNames});
        }
        this.setState({rows: _.orderBy(rows, ['setName'])})
    }

    renderTableContent() {
        if (!this.props.hasLoaded)
            return this.renderTablePlaceholder(<Spinner/>);
        if (!this.state.rows.length)
            return this.renderTablePlaceholder("No sets were found.");
        return (
            <>
                <thead>
                <tr>
                    <th key="name" scope="col">Name</th>
                    {this.props.irrsSeen.map(irrName =>
                        <th key={irrName} scope="col">{irrName}</th>
                    )}
                </tr>
                </thead>
                <tbody>
                {this.state.rows.map(({setName, irrNames}) =>
                    <tr key={setName}>
                        <td key={setName}>{setName}</td>
                        {this.props.irrsSeen.map(irrName =>
                            <td key={irrName} className="text-center">{
                                irrNames.includes(irrName)
                                    ? <FontAwesomeIcon icon={faCheckCircle} title={`Present in ${irrName}`} />
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
    setsPerIrr: PropTypes.object,
    irrsSeen: PropTypes.arrayOf(PropTypes.string),
    hasLoaded: PropTypes.bool,
};


export default AsSetTable;
