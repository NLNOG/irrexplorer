import React, {Component} from 'react';
import PropTypes from 'prop-types';

import PrefixTableExplanation from "./prefixTable/prefixTableExplanation";
import PrefixTable from "./prefixTable/prefixTable";
import api from "../services/api";
import SetIncludedTable from "./common/setIncludedTable";

class ASNQuery extends Component {
    state = {
        hasLoadedPrefixes: false,
        directOriginPrefixes: [],
        overlapPrefixes: [],
        apiCallUrl: '',
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
            hasLoadedPrefixes: false,
            directOriginPrefixes: [],
            overlapPrefixes: [],
            apiCallUrl: '',
        });
        const {data, url} = await api.getPrefixesForASN(this.props.query);
        this.setState({
            hasLoadedPrefixes: true,
            directOriginPrefixes: data.directOrigin,
            overlapPrefixes: data.overlaps,
            apiCallUrl: url,
        });
    }

    render() {
        const {query, reducedColour, filterWarningError} = this.props;
        const {overlapPrefixes, hasLoadedPrefixes, directOriginPrefixes} = this.state;
        return (
            <>
                <h1>Report for ASN {query}</h1>
                <PrefixTableExplanation/>
                <h2 className="h3 mt-4">
                    Prefixes originated by {query}
                </h2>
                <hr/>
                <PrefixTable
                    prefixesData={directOriginPrefixes}
                    hasLoaded={hasLoadedPrefixes}
                    reducedColour={reducedColour}
                    filterWarningError={filterWarningError}
                    apiCallUrl={this.state.apiCallUrl}
                />
                <h2 className="h3 mt-4">
                    Other prefixes overlapping with prefixes originated by {query}
                </h2>
                <hr/>
                <PrefixTable
                    prefixesData={overlapPrefixes}
                    hasLoaded={hasLoadedPrefixes}
                    reducedColour={reducedColour}
                    filterWarningError={filterWarningError}
                    apiCallUrl={this.state.apiCallUrl}
                />
                <h2 className="h3 mt-4">
                    Included in the following AS sets:
                </h2>
                <hr/>
                <SetIncludedTable query={this.props.query} objectClass="as-set"/>
                <h2 className="h3 mt-4">
                    Included in the following route sets:
                </h2>
                <hr/>
                <SetIncludedTable query={this.props.query} objectClass="route-set"/>
            </>
        );
    }
}

ASNQuery.propTypes = {
    query: PropTypes.string.isRequired,
    reducedColour: PropTypes.bool,
    filterWarningError: PropTypes.bool,
};

export default ASNQuery;
