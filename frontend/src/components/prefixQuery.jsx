import React, {Component} from 'react';
import PropTypes from 'prop-types';
import PrefixTableExplanation from "./prefixTable/prefixTableExplanation";
import PrefixTable from "./prefixTable/prefixTable";
import {findLeastSpecific} from "../utils/prefixData";
import api from "../services/api";

class PrefixQuery extends Component {
    state = {
        leastSpecificPrefix: null,
        directOverlapPrefixes: {hasLoaded: false, data: [], apiCallUrl: ''},
        leastSpecificOverlapPrefixes: {hasLoaded: false, data: [], apiCallUrl: ''},
    };

    async componentDidMount() {
        await this.loadPrefixesData();
    }

    async componentDidUpdate(prevProps) {
        if (prevProps.query !== this.props.query) {
            await this.loadPrefixesData();
        }
    }

    async loadPrefixesData() {
        this.setState({
            leastSpecificPrefix: null,
            directOverlapPrefixes: {hasLoaded: false, data: [], apiCallUrl: ''},
            leastSpecificOverlapPrefixes: {hasLoaded: false, data: [], apiCallUrl: ''},
        });
        await this.loadPrefixData(this.props.query, 'directOverlapPrefixes');
        const leastSpecificPrefix = findLeastSpecific(this.props.query, this.state.directOverlapPrefixes.data);
        this.setState({
            leastSpecificPrefix: leastSpecificPrefix,
        })
        if (leastSpecificPrefix) {
            await this.loadPrefixData(leastSpecificPrefix, 'leastSpecificOverlapPrefixes');
        }
    }

    async loadPrefixData(query, target) {
        const {data, url} = await api.getPrefixesForPrefix(query);
        this.setState({
            [target]: {hasLoaded: true, data, apiCallUrl: url},
        })
    }

    render() {
        const {query, reducedColour, filterWarningError} = this.props;
        const {leastSpecificOverlapPrefixes, directOverlapPrefixes, leastSpecificPrefix} = this.state;
        return (
            <>
                <h1>Report for prefix {query}</h1>
                <PrefixTableExplanation/>
                <h2 className="h3 mt-4">
                    Directly overlapping prefixes of {query}
                </h2>
                <hr/>
                <PrefixTable
                    prefixesData={directOverlapPrefixes.data}
                    hasLoaded={directOverlapPrefixes.hasLoaded}
                    apiCallUrl={directOverlapPrefixes.apiCallUrl}
                    reducedColour={reducedColour}
                    filterWarningError={filterWarningError}
                />

                {leastSpecificPrefix && <>
                    <h2 className="h3 mt-4">
                        All overlaps of least specific match {leastSpecificPrefix}
                    </h2>
                    <hr/>
                    <PrefixTable
                        prefixesData={leastSpecificOverlapPrefixes.data}
                        hasLoaded={leastSpecificOverlapPrefixes.hasLoaded}
                        apiCallUrl={leastSpecificOverlapPrefixes.apiCallUrl}
                        reducedColour={reducedColour}
                        filterWarningError={filterWarningError}
                    />
                </>}
            </>
        );
    }
}

PrefixQuery.propTypes = {
    query: PropTypes.string.isRequired,
    reducedColour: PropTypes.bool,
    filterWarningError: PropTypes.bool,
};

export default PrefixQuery;
