import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faSort, faSortDown, faSortUp} from '@fortawesome/free-solid-svg-icons'


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

    renderCell = (label, cellSortKey) => {
        const {key:currentKey, order} = this.state.sortColumn;

        let sortIcon = faSort;
        if (cellSortKey === currentKey && order === 'asc') sortIcon = faSortDown;
        if (cellSortKey === currentKey && order === 'desc') sortIcon = faSortUp;
        return (
            <th key={cellSortKey} scope="col" className="clickable" onClick={() => this.handleSort(cellSortKey)}>
                {label} <FontAwesomeIcon icon={sortIcon}/>
            </th>
        );

    }
    render() {
        return <thead>
        <tr>
            {this.renderCell('Prefix', 'prefix')}
            {this.renderCell('RIR', 'rir')}
            {this.renderCell('BGP', 'bgpOrigins')}
            {this.renderCell('RPKI', 'rpkiRoutes')}
            {this.props.irrSourceColumns.map(sourceName =>
                this.renderCell(sourceName, `irrRoutes.${sourceName}`)
            )}
            {this.renderCell('Advice', 'messages')}
        </tr>
        </thead>;
    }
}


PrefixTableHeader.propTypes = {
    irrSourceColumns: PropTypes.arrayOf(PropTypes.string).isRequired,
    onSort: PropTypes.func.isRequired,
};

export default PrefixTableHeader;
