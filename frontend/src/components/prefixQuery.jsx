import React, {Component} from 'react';
import PropTypes from 'prop-types';
import PrefixTableExplanation from "./prefixTable/prefixTableExplanation";
import PrefixTable from "./prefixTable/prefixTable";
import {findLeastSpecific} from "../utils/prefixData";
import api from "../services/api";

class PrefixQuery extends Component {
    state = {
        leastSpecificPrefix: null,
        directOverlapPrefixes: {hasLoaded: false, data: []},
        leastSpecificOverlapPrefixes: {hasLoaded: false, data: []},
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
            directOverlapPrefixes: {hasLoaded: false, data: []},
            leastSpecificOverlapPrefixes: {hasLoaded: false, data: []},
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
        const data = await api.getPrefixesForPrefix(query);
        console.log(target, data);
        this.setState({
            [target]: {hasLoaded: true, data},
        })
    }

    render() {
        const {query, reducedColour} = this.props;
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
                    reducedColour={reducedColour}
                />

                {leastSpecificPrefix && <>
                    <h2 className="h3 mt-4">
                        All overlaps of least specific match {leastSpecificPrefix}
                    </h2>
                    <hr/>
                    <PrefixTable
                        prefixesData={leastSpecificOverlapPrefixes.data}
                        hasLoaded={leastSpecificOverlapPrefixes.hasLoaded}
                        reducedColour={reducedColour}
                    />
                </>}
            </>
        );
    }
}

PrefixQuery.propTypes = {
    query: PropTypes.string.isRequired,
    reducedColour: PropTypes.bool,
};

export default PrefixQuery;
