import React, {Component} from 'react';
import PropTypes from 'prop-types';

import api from "../../services/api";
import Spinner from "./spinner";
import {Link} from "@reach/router";
import TableFooter from "./tableFooter";


class AsSetExpansionTable extends Component {
    state = {
        hasLoaded: false,
        subSets: [],
        apiCallUrl: '',
    }

    async componentDidMount() {
        await this.load();
    }

    async componentDidUpdate(prevProps) {
        if (prevProps.query !== this.props.query) {
            await this.load();
        }
    }

    async load() {
        this.setState({
            hasLoaded: false,
            subSets: [],
            apiCallUrl: '',
        });
        const {data, url} = await api.getSetExpansion(this.props.query);
        this.setState({
            hasLoaded: true,
            subSets: data,
            apiCallUrl: url,
        });
    }

    renderTableContent() {
        const {hasLoaded, subSets, apiCallUrl} = this.state;
        if (!hasLoaded)
            return this.renderTablePlaceholder(<Spinner/>);
        if (!subSets.length)
            return this.renderTablePlaceholder("AS set was not found.");
        return (
            <>
                <thead>
                <tr>
                    <th key="name" scope="col">Name</th>
                    <th key="source" scope="col">Source</th>
                    <th key="depth" scope="col">Depth</th>
                    <th key="path" scope="col">Path</th>
                    <th key="members" scope="col">Members</th>
                </tr>
                </thead>
                <tbody>
                {subSets.map(({name, source, depth, path, members}) =>
                    <tr key={name + path.join()}>
                        <td key="name"><Link to={`/as-set/${name}`}>{name}</Link></td>
                        <td key="source">{source}</td>
                        <td key="depth">{depth}</td>
                        <td key="path">{path.join(' ➜ ')}</td>
                        <td key="members">{members.join(' ')}</td>
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
                <td colSpan="4" className="text-center">{placeholder}</td>
            </tr>
            </tbody>
        );
    }

    render() {
        return (
            <table className="table mb-5 table-fixed table-striped">
                <caption>Expansion depth is limited beyond 1000 total as-sets.</caption>
                {this.renderTableContent()}
            </table>
        );
    }
}

AsSetExpansionTable.propTypes = {
    query: PropTypes.string.isRequired,
};


export default AsSetExpansionTable;
