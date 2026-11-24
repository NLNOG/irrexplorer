import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faSort, faSortDown, faSortUp} from '@fortawesome/free-solid-svg-icons'

import columnDescriptions from "./columnDescriptions";


class PrefixTableHeader extends Component {
    state = {sortColumn: {key: 'prefix', order: 'asc'}};

    handleSort = (key) => {
        const sortColumn = {...this.state.sortColumn};
        if (sortColumn.key === key) {
            sortColumn.order = (sortColumn.order === 'asc') ? 'desc' : 'asc';
        } else {
            sortColumn.key = key;
            sortColumn.order = 'asc';
        }
        this.setState({sortColumn});
        this.props.onSort(sortColumn);
    }

    renderCell = (label, cellSortKey, description) => {
        if (!cellSortKey)
            return <th key={label} scope="col">{label}</th>;

        const {key:currentKey, order} = this.state.sortColumn;

        let sortIcon = faSort;
        if (cellSortKey === currentKey && order === 'asc') sortIcon = faSortDown;
        if (cellSortKey === currentKey && order === 'desc') sortIcon = faSortUp;
        return (
            <th
                key={cellSortKey}
                scope="col"
                className="clickable nowrap"
                tabIndex="0"
                onClick={() => this.handleSort(cellSortKey)}
                onKeyDown={() => this.handleSort(cellSortKey)}
                title={`${description} Click to sort.`}
            >
                {label} <FontAwesomeIcon icon={sortIcon}/>
            </th>
        );

    }
    render() {
        return <thead>
        <tr>
            {this.renderCell('Prefix', 'prefix', columnDescriptions.prefix)}
            {this.renderCell('RIR', 'rir', columnDescriptions.rir)}
            {this.renderCell('BGP', 'bgpOrigins', columnDescriptions.bgp)}
            {this.renderCell('RPKI', 'rpkiRoutes', columnDescriptions.rpki)}
            {this.props.irrSourceColumns.map(sourceName =>
                this.renderCell(sourceName, `irrRoutes.${sourceName}`, columnDescriptions.irr)
            )}
            {this.props.reducedColour && this.renderCell('', null)}
            {this.renderCell('Advice', 'messages', columnDescriptions.advice)}
        </tr>
        </thead>;
    }
}


PrefixTableHeader.propTypes = {
    irrSourceColumns: PropTypes.arrayOf(PropTypes.string).isRequired,
    onSort: PropTypes.func.isRequired,
    reducedColour: PropTypes.bool,
};

export default PrefixTableHeader;
