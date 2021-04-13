import React, {Component} from 'react';
import PropTypes from 'prop-types';

import PrefixTableExplanation from "./prefixTable/prefixTableExplanation";
import PrefixTable from "./prefixTable/prefixTable";
import api from "../services/api";
import AsSetIncludedTable from "./common/asSetIncludedTable";

class ASNQuery extends Component {
    state = {
        hasLoadedPrefixes: false,
        directOriginPrefixes: [],
        overlapPrefixes: [],
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
        });
        const response = await api.getPrefixesForASN(this.props.query);
        this.setState({
            hasLoadedPrefixes: true,
            directOriginPrefixes: response.directOrigin,
            overlapPrefixes: response.overlaps,
        });
    }

    render() {
        const {query} = this.props;
        const {overlapPrefixes, hasLoadedPrefixes, directOriginPrefixes} = this.state;
        return (
            <>
                <h1>Report for ASN {query}</h1>
                <PrefixTableExplanation/>
                <h2 className="h3 mt-4">
                    Prefixes originated by {query}
                </h2>
                <hr/>
                <PrefixTable prefixesData={directOriginPrefixes} hasLoaded={hasLoadedPrefixes}
                />
                <h2 className="h3 mt-4">
                    Other prefixes overlapping with prefixes originated by {query}
                </h2>
                <hr/>
                <PrefixTable prefixesData={overlapPrefixes} hasLoaded={hasLoadedPrefixes}/>
                <h2 className="h3 mt-4">
                    Included in the following sets:
                </h2>
                <hr/>
                <AsSetIncludedTable query={this.props.query}/>
            </>
        );
    }
}

ASNQuery.propTypes = {
    query: PropTypes.string.isRequired,
};

export default ASNQuery;
